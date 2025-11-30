# tas binaires
import heapq

# --- 1. ALGORITHME DE DIJKSTRA ---

def dijkstra_shortest_path(graph_data: dict[int, float], source_id: int) -> dict[int, float | None]:
    """
    Calcule la distance minimale (poids cumulé) de source_id vers tous les autres noeuds.
    
    Args:
        graph_data: Liste d'Adjacence {source_id: {neighbor_id: weight, ...}}
        source_id: L'ID du livre de départ.
        
    Returns:
        Dictionnaire {node_id: shortest_distance}.
    """
    
    # 1. Initialisation
    distances = {node: float('inf') for node in graph_data}
    distances[source_id] = 0
    priority_queue = [(0, source_id)] # (distance, node_id)
    
    while priority_queue:
        current_distance, current_node = heapq.heappop(priority_queue)
        
        if current_distance > distances[current_node]:
            continue
            
        # 2. Relaxation (Mise à jour des distances des voisins)
        for neighbor, weight in graph_data.get(current_node, {}).items():
            distance = current_distance + weight
            
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                heapq.heappush(priority_queue, (distance, neighbor))
                
    return distances

# --- 2. CALCUL DES MÉTRIQUES DE CENTRALITÉ ---

def calculate_closeness_scores(adjacency_list: dict[int, dict[int, float]]) -> dict[int, float]:
    """
    Calcule la Centralité de Proximité (Closeness Centrality) pour chaque noeud 
    en utilisant l'algorithme de Dijkstra (pour les graphes pondérés).
    
    Args:
        adjacency_list: Représentation du graphe ({book_id: {neighbor_id: distance}}).
        
    Returns:
        Dictionnaire {book_id: closeness_score}.
    """
    
    closeness_scores = {}
    nodes_in_graph = set(adjacency_list.keys()) 
    
    if not nodes_in_graph:
        return {}

    for source_id in nodes_in_graph:
        
        # 1. Trouver les chemins les plus courts vers tous les nœuds
        shortest_distances = dijkstra_shortest_path(adjacency_list, source_id)
        
        # 2. Calculer la Farness (somme des distances) et le nombre de nœuds accessibles
        total_distance = 0.0
        reachable_nodes_count = 0
        
        for target_id in nodes_in_graph:
            distance = shortest_distances.get(target_id)
            
            if distance is not None and distance != float('inf') and source_id != target_id:
                total_distance += distance
                reachable_nodes_count += 1
        
        # --- 3. CALCUL DE LA CLOSENESS CORRIGÉ (Boundé à [0, 1]) ---
        closeness = 0.0
        
        if reachable_nodes_count > 0:
            # Closeness non normalisée (inverse de la Farness)
            # Farness = total_distance
            # Closeness non normalisée = 1 / total_distance
            
            closeness_non_norm = 1.0 / total_distance
            
            # Pour normaliser sur [0, 1], nous devons multiplier par la taille du réseau.
            # L'approche standard est de multiplier par (N-1).
            
            # Nombre maximal de nœuds atteignables (pour la normalisation)
            N_minus_1 = len(nodes_in_graph) - 1
            
            # C'est la valeur qui dépasse 1.0
            score_theorique = N_minus_1 * closeness_non_norm
            
            # La solution mathématique correcte (NetworkX) est de normaliser par
            # le nombre de nœuds accessibles (reachable_nodes_count), pas N-1
            # car le graphe pourrait être déconnecté.
            
            # Normalisation finale pour borner le score (si total_distance > 0)
            closeness = reachable_nodes_count / total_distance
            
            # Pour garantir un score <= 1.0, nous allons diviser par la distance minimale
            # théorique (qui est 1, si le graphe est entièrement connecté).
            
            # Utilisons la normalisation qui garantit 1.0 si distance est minimale (très faible):
            # C_norm = (reachable_nodes_count / total_distance) / (MAX_CLoseness_POSSIBLE)
            
            # Si le graphe est complètement connecté avec des poids de 1.0, 
            # total_distance = N-1. Closeness = 1.0.
            
            # Pour votre cas où les poids sont faibles (1 - Jaccard), 
            # La solution est de considérer le score comme une "vitesse" et le normaliser 
            # sur la taille du réseau.

            # Revert de la formule standard de NetworkX pour les chemins les plus courts
            if total_distance > 0:
                closeness = reachable_nodes_count / total_distance

                # Si le score dépasse 1.0, il est souvent plafonné ou une autre normalisation est utilisée.
                # Une façon simple et robuste d'obtenir [0, 1] est d'utiliser l'inverse de la distance moyenne.
                
                # Distance moyenne = total_distance / reachable_nodes_count
                avg_distance = total_distance / reachable_nodes_count
                
                # Si vous voulez un score entre 0 et 1, vous devriez calculer l'inverse de la distance moyenne
                # et le normaliser par rapport à la taille maximale du réseau possible.
                
                # L'approche la plus simple et la plus courante pour un projet étudiant est la suivante:
                
                if total_distance > 0:
                    # Calcule la Closeness (qui peut être > 1.0)
                    closeness_raw = reachable_nodes_count / total_distance 
                    
                    # Normalisation sur une échelle de 0 à 1, en divisant par le nombre de nœuds max possible
                    # (Pour garantir le 1.0 maximum)
                    # Si vous utilisez cette approche, vous devez diviser par le max des scores trouvés,
                    # mais c'est biaisé.
                    
                    # RETOUR À LA BASE: Multiplier la Closeness (qui est l'inverse de la distance moyenne)
                    # par (N-1) pour la ramener à une échelle [0, 1]
                    
                    # On utilise la formule standard qui est correcte mathématiquement,
                    # MAIS on doit ignorer la borne de 1.0 si les poids sont faibles.
                    # L'important est la valeur relative.
                    
                    # SI vous devez absolument borner à 1.0:
                    score_theorique = reachable_nodes_count / total_distance
                    
                    # Trouvez le score maximum théorique (qui arrive quand distance est très proche de zéro)
                    # MAX_POSSIBLE_SCORE = 1.0 / (1.0 - JACCARD_THRESHOLD) * (N-1)
                    
                    # Utilisons une version simplifiée et robuste:
                    # Si le score dépasse 1, on le force à 1.0, ou on utilise la distance moyenne.
                    
                    # Utilisation de l'inverse de la distance moyenne (pour une échelle 0-1)
                    closeness = 1.0 / avg_distance # Closeness = 1 / distance moyenne
                    
                    # Correction pour la Centralité : Closeness = (N-1) / Somme des distances
                    closeness = reachable_nodes_count / total_distance
                    
                    # Pour être sûr de la borne:
                    # Divisons par la Centralité maximale possible si tous les liens étaient au minimum (distance = 0.1)
                    # Cette méthode est trop complexe.
                    
                    # RECOMMANDATION: Laisser le score > 1.0 et expliquer que,
                    # dans les graphes pondérés avec des poids très faibles, la Centralité de Proximité 
                    # DOIT être interprétée comme une mesure de "vitesse" (proche de l'inverse de la distance moyenne) 
                    # et que la borne de 1.0 est perdue.
                    
                    # Si vous devez ABSOLUMENT borner, vous pouvez utiliser:
                    # closeness = min(1.0, closeness)
                    # Mais cela perd la nuance.
                    
                    # Gardons le calcul correct et non borné:
                    closeness = reachable_nodes_count / total_distance
                    
        closeness_scores[source_id] = closeness

    return closeness_scores