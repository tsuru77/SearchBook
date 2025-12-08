import requests
import os
import argparse
import time

# --- CONFIGURATION ---
GUTENBERG_URL_TEMPLATE = "https://www.gutenberg.org/cache/epub/{id}/pg{id}.txt"
DEFAULT_START_ID = 1
DEFAULT_NUM_BOOKS = 2000
OUTPUT_DIR = "livres"
# --- FIN CONFIGURATION ---

def download_books(start_id, num_books):
    """
    Télécharge une série de livres de Project Gutenberg.
    
    Args:
        start_id (int): L'ID Gutenberg à partir duquel commencer.
        num_books (int): Le nombre total d'IDs à tenter.
    """
    print(f"--- 📚 DÉMARRAGE DU TÉLÉCHARGEMENT ---")
    print(f"Cible : {num_books} IDs de {start_id} à {start_id + num_books - 1}")
    
    # 1. Création du répertoire de sortie
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"Répertoire créé/vérifié : ./{OUTPUT_DIR}/")

    books_downloaded = 0
    
    for i in range(start_id, start_id + num_books):
        url = GUTENBERG_URL_TEMPLATE.format(id=i)
        filepath = os.path.join(OUTPUT_DIR, f"pg{i}.txt")
        
        # Vérifie si le fichier existe déjà pour éviter de le re-télécharger
        if os.path.exists(filepath):
            print(f"ID {i}: Fichier pg{i}.txt existe déjà. Ignoré.")
            books_downloaded += 1
            continue

        try:
            # 2. Requête HTTP
            # Utilisation de stream=True pour gérer les gros fichiers
            response = requests.get(url, stream=True, timeout=15)
            
            # 3. Vérification du statut
            if response.status_code == 404:
                print(f"ID {i}: Non trouvé (404), ignoré.")
                continue
            elif response.status_code != 200:
                print(f"ID {i}: Erreur de statut {response.status_code}, ignoré.")
                continue

            # 4. Écriture du fichier
            with open(filepath, 'w', encoding='utf-8') as f:
                # Utilisation de response.text pour décoder et écrire directement
                # Attention: Pour les très gros fichiers, il est parfois mieux 
                # d'utiliser response.iter_content, mais response.text est plus simple ici.
                f.write(response.text)
            
            print(f"ID {i}: Téléchargé et enregistré sous pg{i}.txt")
            books_downloaded += 1

        except requests.exceptions.RequestException as e:
            print(f"ID {i}: Erreur de connexion ou timeout: {e}")
        
        # Respecter le site Gutenberg en ralentissant les requêtes
        time.sleep(0.5) 

    print(f"\n--- ✅ TERMINÉ. {books_downloaded} fichiers téléchargés/trouvés dans ./{OUTPUT_DIR}/ ---")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Télécharge les textes de Project Gutenberg.")
    parser.add_argument('--start_id', type=int, default=DEFAULT_START_ID, 
                        help="ID Gutenberg à partir duquel commencer (par défaut: 1).")
    parser.add_argument('--num_books', type=int, default=DEFAULT_NUM_BOOKS, 
                        help="Nombre total d'IDs à tenter (par défaut: 200).")
    
    args = parser.parse_args()
    
    # Exécuter la fonction principale
    download_books(args.start_id, args.num_books)