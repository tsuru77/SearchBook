import requests
import psycopg2
from psycopg2.extensions import connection as psycopg2_conn # alias pour le typage
import re
import argparse
import unicodedata
from nltk.corpus import stopwords
# import networkx as nx
from collections import defaultdict
import time
import os

# import module pour calculer la centralité
import graph_algorithms

# --- CONFIGURATION (À ADAPTER) ---
DB_CONFIG = {
    'host': "localhost",
    'database': "searchbook",
    'user': "searchbook",
    'password': "searchbook_password"
}

GUTENBERG_URL = "https://www.gutenberg.org/cache/epub/{id}/pg{id}.txt"


NORMALIZE_UNICODE = True  # Mettre à False pour désactiver la normalisation Unicode
DISABLE_STOP_WORDS = False  # Mettre à True pour désactiver le filtrage des stop words

# Mots vides standards pour le cas d'échec
# Définition globale
try:
    STOP_LANGUAGES = {
        'french': set(stopwords.words('french')),
        'english': set(stopwords.words('english')),
        # Ajouter d'autres langues
    }
    # Définir un fallback sûr au cas où une langue n'est pas trouvée
    DEFAULT_STOP_WORDS = STOP_LANGUAGES['english'] 
except LookupError:
    # Gérer si les données NLTK ne sont pas installées
    print("ATTENTION: Les données NLTK (stopwords) ne sont pas installées.")
    STOP_LANGUAGES = {}
    DEFAULT_STOP_WORDS = set()

# Seuil de similarité Jaccard pour créer une arête dans le graphe
JACCARD_THRESHOLD = 0.1


# --- 1. PRÉ-TRAITEMENT ET METADONNÉES ---

METADATA_PATTERNS = {
    'title': re.compile(r"Title:\s*(.+)", re.IGNORECASE),
    'author': re.compile(r"Author:\s*(.+)", re.IGNORECASE),
    'language': re.compile(r"Language:\s*(.+)", re.IGNORECASE),
    'publication_year': re.compile(r"Release Date:\s*[A-Za-z]+\s+\d+,\s*(\d{4})", re.IGNORECASE) 
}


def extract_metadata(content : str) -> dict:
    """Extraction des métadonnées du livre à partir du contenu brut"""
    metadata = {}
    for key, pattern in METADATA_PATTERNS.items():
        match = pattern.search(content)
        # Utilise .strip() pour retirer les espaces des extrémités
        metadata[key] = match.group(1).strip() if match else None 
    
    if not metadata.get('language'):
        metadata['language'] = 'unknown'
    
    if not metadata.get('title'):
        metadata['title'] = 'unknown'
        
    return metadata

def clean_and_tokenize(content : str, language : str = 'english') -> list[str]:
    """
    Nettoie le contenu, supprime les accents, le met en minuscule,
    supprime la ponctuation et filtre les stop words.
    """
    # 1. Mise en minuscule
    content_lower = content.lower()
    content_to_clean = content_lower
    
    if NORMALIZE_UNICODE:
        # 2. Normalisation Unicode (NFD) et suppression des accents (Mn)
        normalized_content = unicodedata.normalize('NFD', content_lower)
        content_to_clean = ''.join(
            char for char in normalized_content 
            if unicodedata.category(char) != 'Mn'
        )
        
    # 3. Retrait de la ponctuation et des caractères spéciaux
    content_clean = re.sub(r"[^\w\s'-]", ' ', content_to_clean, flags=re.UNICODE)

    
    # 4. Tokenisation simple et gestion des stop words
    tokens = content_clean.split()
    
    stop_words = {} # Par défaut

    if not DISABLE_STOP_WORDS:
        lang_key = language.lower()
        found_in_cache = False
        
        # --- A. Recherche dans le cache pré-chargé (STOP_LANGUAGES) ---
        for key, stop_set in STOP_LANGUAGES.items():
            if key in lang_key:
                stop_words = stop_set
                found_in_cache = True
                break
        
        # --- B. Tentative de chargement dynamique si non trouvé ---
        if not found_in_cache:
            # Tente d'extraire le nom de langue le plus probable (ex: 'french' de 'french (france)')
            lang_to_try = lang_key.split(' ')[0] 
            
            try:
                # Tente de charger la langue directement via la bibliothèque NLTK
                new_stop_words = set(stopwords.words(lang_to_try))
                
                # Succès: Mise à jour du cache global pour les appels futurs
                STOP_LANGUAGES[lang_to_try] = new_stop_words 
                stop_words = new_stop_words
                # print(f"   -> Langue '{lang_to_try}' chargée dynamiquement et mise en cache.") # Décommenter pour debug
                
            except LookupError:
                # Échec: La langue n'est pas supportée par NLTK, on garde le DEFAULT_STOP_WORDS
                stop_words = DEFAULT_STOP_WORDS
    
    # Filtrer les mots vides et les chaînes vides
    clean_tokens = [token for token in tokens if token and token not in stop_words]
    
    return clean_tokens

# --- B. INGESTION ET INDEXATION ---

def _process_and_insert_book(cursor, content : str, gutenberg_id : int, min_words : int, conn : psycopg2_conn, book_token_sets : dict[int, set[str]]) -> bool | None:
    """Logique de traitement et d'insertion pour un seul livre (utilisée par les deux fonctions d'ingestion)."""
    
    metadata = extract_metadata(content)
    clean_tokens = clean_and_tokenize(content, metadata.get('language', 'english'))
    word_count = len(clean_tokens)
    
    if word_count < min_words:
        print(f"ID {gutenberg_id}: '{metadata.get('title', 'TITRE INCONNU')}' trop court ({word_count} mots).")
        return None # Retourne None si le livre est ignoré

    print(f"ID {gutenberg_id}: '{metadata.get('title', 'TITRE INCONNU')}' - Traitement...")

    # 2. Calcul des Term Frequencies (TF)
    term_frequencies = defaultdict(int)
    for token in clean_tokens:
        term_frequencies[token] += 1

    # --- Insertion dans la table BOOKS ---
    cursor.execute("""
        INSERT INTO books (gutenberg_id, title, author, language, publication_year, content, word_count)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING id;
    """, (
        gutenberg_id,
        metadata.get('title'),
        metadata.get('author'),
        metadata.get('language'),
        metadata.get('publication_year'),
        content.lower(),
        word_count
    ))
    book_id = cursor.fetchone()[0]
    
    # On stocke l'ensemble de tokens uniques (les clés) en mémoire
    book_token_sets[book_id] = set(term_frequencies.keys())
    
    # --- Insertion dans la table INVERTED_INDEX ---
    index_values = [ (word, book_id, freq) for word, freq in term_frequencies.items() ]
    
    if index_values:
        template = "(%s, %s, %s)"
        values_list = [cursor.mogrify(template, v).decode('utf-8') for v in index_values]
        cursor.execute(f"""
            INSERT INTO inverted_index (word, book_id, frequency)
            VALUES {", ".join(values_list)};
        """)
    
    conn.commit()
    print(f"   -> Livre ID {book_id} indexé et enregistré.")
    return True # Indique le succès

def ingest_and_index_books_from_directory(conn : psycopg2_conn, directory_path : str, min_words : int) -> dict[int, set[str]]: 
    """Lit les fichiers .txt dans un répertoire local et les indexe."""
    print(f"--- 1. INGESTION À PARTIR DU RÉPERTOIRE LOCAL '{directory_path}' ---")
    
    cursor = conn.cursor()
    book_token_sets = {} 
    
    for filename in os.listdir(directory_path):
        if not filename.endswith('.txt'):
            continue
        
        filepath = os.path.join(directory_path, filename)
        
        # Extrait l'ID Gutenberg à partir du nom du fichier (ex: pg123.txt -> 123)
        match = re.search(r'pg(\d+)\.txt', filename)
        if not match:
            print(f"Fichier {filename}: Impossible d'extraire l'ID Gutenberg, ignoré.")
            continue
            
        gutenberg_id = int(match.group(1))

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            _process_and_insert_book(cursor, content, gutenberg_id, min_words, conn, book_token_sets)

        except psycopg2.Error as e:
            conn.rollback()
            print(f"Erreur DB pour fichier {filename}: {e}")
        except Exception as e:
            print(f"Erreur de traitement pour le fichier {filename}: {e}")
            
    print(f"Ingestion terminée. {len(book_token_sets)} livres prêts pour le graphe.")
    return book_token_sets


def _ingest_from_gutenberg(conn : psycopg2_conn, start_id : int, num_texts : int, min_words : int) -> dict[int, set[str]]: 
    """Télécharge les livres depuis Gutenberg et les indexe."""
    print(f"--- 1. INGESTION DIRECTE DEPUIS GUTENBERG (ID {start_id} à {start_id + num_texts}) ---")
    
    cursor = conn.cursor()
    book_token_sets = {}


    for i in range(start_id, start_id + num_texts):
        url = GUTENBERG_URL.format(id=i)
        
        try:
            response = requests.get(url, timeout=15)
            if response.status_code != 200:
                print(f"ID {i}: Non disponible ({response.status_code}), ignoré.")
                time.sleep(0.5)
                continue

            content = response.text
            
            _process_and_insert_book(cursor, content, i, min_words, conn, book_token_sets)
            
        except psycopg2.Error as e:
            conn.rollback()
            print(f"Erreur DB pour ID {i}: {e}")
        except requests.exceptions.RequestException as e:
            print(f"Erreur de connexion pour l'ID {i}: {e}")
        
        # Respecter Gutenberg
        time.sleep(0.5)
        
    print(f"Ingestion terminée. {len(book_token_sets)} livres prêts pour le graphe.")
    return book_token_sets


# --- C. CALCULS DE GRAPHE ET MISE À JOUR DB ---

# (Les fonctions calculate_jaccard et calculate_graph_metrics restent inchangées)

def calculate_jaccard(set_a : set[str], set_b : set[str]):
    """Calcule l'indice de Jaccard entre deux ensembles de tokens."""
    intersection = len(set_a.intersection(set_b))
    union = len(set_a.union(set_b))
    return intersection / union if union > 0 else 0


def calculate_graph_metrics(conn : psycopg2_conn, book_token_sets : dict[int, set[str]]):
    """Calcule Jaccard, construit le graphe et calcule la Closeness Centrality."""
    print("--- 2. CALCUL DES MÉTRIQUES DU GRAPHE ---")
    
    start_time = time.time()
    book_ids = list(book_token_sets.keys())
    N = len(book_ids)
    cursor = conn.cursor()
    
    jaccard_inserts = []

    adjacency_list = defaultdict(dict)
    # G = nx.Graph()
    
    # --- 2a. Calcul des similarités Jaccard (N * (N-1) / 2 comparaisons) ---
    print(f"   -> Calcul de {N * (N-1) // 2} paires Jaccard...")
    
    for i in range(N):
        for j in range(i + 1, N): 
            id_a = book_ids[i]
            id_b = book_ids[j]
            set_a = book_token_sets[id_a]
            set_b = book_token_sets[id_b]
            
            jaccard_score = calculate_jaccard(set_a, set_b)
            
            if jaccard_score >= JACCARD_THRESHOLD:
                distance = 1.0 - jaccard_score 
                jaccard_inserts.append((id_a, id_b, jaccard_score)) 
                # G.add_edge(id_a, id_b, weight=distance)
                adjacency_list[id_a][id_b] = distance
                adjacency_list[id_b][id_a] = distance

    print(f"   -> {len(jaccard_inserts)} arêtes Jaccard > {JACCARD_THRESHOLD} créées.")
    
    # --- 2b. Calcul de la Centralité de Proximité (Closeness) ---
    if adjacency_list:
        # closeness_scores = nx.closeness_centrality(G, distance='weight') 
        closeness_scores = graph_algorithms.calculate_closeness_scores(adjacency_list)
    else:
        closeness_scores = {}
        print("   -> Graphe vide, Closeness non calculée.")

    # --- 2c. Insertion des Arêtes Jaccard et Mise à jour de Closeness ---
    if jaccard_inserts:
        template = "(%s, %s, %s)"
        values_list = [cursor.mogrify(template, v).decode('utf-8') for v in jaccard_inserts]
        cursor.execute(f"""
            INSERT INTO jaccard_graph (book_a_id, book_b_id, similarity_score)
            VALUES {", ".join(values_list)};
        """)

    for book_id, score in closeness_scores.items():
        cursor.execute("""
            UPDATE books SET closeness_score = %s WHERE id = %s;
        """, (score, book_id))
        
    conn.commit()
    end_time = time.time()
    print(f"   -> Calculs terminés et DB mise à jour en {end_time - start_time:.2f} secondes.")


# --- FONCTION PRINCIPALE ---

def main():
    parser = argparse.ArgumentParser(description="Pipeline d'ingestion et de calcul pour le moteur de recherche de bibliothèque.")
    
    # Option pour la lecture locale (Priorité)
    parser.add_argument('--path', type=str, default=None, 
                        help="Chemin vers le répertoire contenant les fichiers Gutenberg (.txt) pour l'ingestion locale.")
    
    # Options pour le téléchargement (utilisé si --path n'est pas fourni)
    parser.add_argument('--start-id', type=int, default=1, help="ID Gutenberg à partir duquel commencer le téléchargement (si pas de --path).")
    parser.add_argument('--num-texts', type=int, default=50, help="Nombre de textes à tenter de traiter (si pas de --path).")
    
    # Autres options
    parser.add_argument('--min-words', type=int, default=10000, help="Taille minimale des livres pour être inclus.")
    args = parser.parse_args()
    print(args)

    # 1. Connexion DB
    try:
        conn = psycopg2.connect(**DB_CONFIG)
    except psycopg2.Error as e:
        print(f"IMPOSSIBLE DE SE CONNECTER À LA BASE DE DONNÉES. Vérifiez DB_CONFIG: {e}")
        return

    # 2. Ingestion et Indexation
    if args.path:
        # MODE LECTURE LOCALE
        if not os.path.isdir(args.path):
            print(f"Erreur: Le chemin '{args.path}' n'est pas un répertoire valide.")
            conn.close()
            return
        book_token_sets = ingest_and_index_books_from_directory(conn, args.path, args.min_words)
    else:
        # MODE TÉLÉCHARGEMENT DIRECT
        book_token_sets = _ingest_from_gutenberg(conn, args.start_id, args.num_texts, args.min_words)
    
    # 3. Calcul du Graphe
    if book_token_sets:
        calculate_graph_metrics(conn, book_token_sets)
    
    conn.close()

if __name__ == "__main__":
    main()