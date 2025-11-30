# tas binaires
import heapq

# --- 1. ALGORITHME DE DIJKSTRA ---

def dijkstra_shortest_path(graph_data: dict, source_id: int) -> dict[int, float | None]:
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

def calculate_closeness_scores(adjacency_list: dict) -> dict[int, float]:
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
        
        # 1. Trouver les chemins les plus courts vers tous les noeuds
        shortest_distances = dijkstra_shortest_path(adjacency_list, source_id)
        
        # 2. Calculer la Farness (somme des distances) et le nombre de noeuds accessibles
        total_distance = 0.0
        reachable_nodes_count = 0
        
        # On itère sur tous les noeuds du graphe
        for target_id in nodes_in_graph:
            distance = shortest_distances.get(target_id)
            
            # Ne considérer que les noeuds accessibles et différents du noeud source
            if distance is not None and distance != float('inf') and source_id != target_id:
                total_distance += distance
                reachable_nodes_count += 1

        # 3. Calculer la Closeness (Closeness = nombre de noeuds accessibles / distance totale)
        if total_distance > 0:
            # Note: Si total_distance est très faible, ce score peut dépasser 1.0 (voir discussion précédente).
            # Nous utilisons le résultat direct de la formule pour les graphes pondérés.
            closeness = reachable_nodes_count / total_distance 
        else:
             # Cas isolé ou auto-connecté (si le graphe est déconnecté)
            closeness = 0.0 

        closeness_scores[source_id] = closeness
        
    return closeness_scores