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
    
    closeness_scores = {}
    nodes_in_graph = set(adjacency_list.keys()) 
    
    if not nodes_in_graph:
        return {}

    # BOUCLE PRINCIPALE: On calcule la Centralité de Proximité pour chaque noeud (livre)
    for source_id in nodes_in_graph:
        
        # 1. Trouver les chemins les plus courts (Algorithme de Dijkstra)
        shortest_distances = dijkstra_shortest_path(adjacency_list, source_id)
        
        # 2. Calculer la Farness et le nombre de noeuds accessibles
        total_distance = 0.0
        reachable_nodes_count = 0

        # Itérer sur les résultats de Dijkstra
        for target_id, distance in shortest_distances.items():
            # Vérifier si le noeud est atteignable (distance != inf) et n'est pas le noeud source
            if distance != float('inf') and source_id != target_id:
                total_distance += distance
                reachable_nodes_count += 1
        
        # 3. CALCUL DE LA CLOSENESS 
        closeness = 0.0
        
        if total_distance > 0:
            # Closeness = Nombre de noeuds accessibles / Somme des distances minimales
            # Ceci est la formule pondérée, qui peut donner > 1.0
            closeness = reachable_nodes_count / total_distance 
        
        # Enregistrement du score pour le noeud source
        closeness_scores[source_id] = closeness

    return closeness_scores