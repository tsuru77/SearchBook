/**
 * Service API pour les appels au backend SearchBook
 */
import { SearchResponse, RankingType } from "../types/api";

const API_BASE_URL =
  (import.meta as any).env?.VITE_API_URL || "http://localhost:8000";

export const searchAPI = {
  /**
   * Recherche simple par mot-clé
   */
  async simpleSearch(
    query: string,
    rankingBy: RankingType = "occurrences",
    limit: number = 20
  ): Promise<SearchResponse> {
    const response = await fetch(`${API_BASE_URL}/api/search/simple`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        query,
        ranking_by: rankingBy,
        limit,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Erreur lors de la recherche simple");
    }

    return response.json();
  },

  /**
   * Recherche avancée par expression régulière
   */
  async advancedSearch(
    regexPattern: string,
    rankingBy: RankingType = "occurrences",
    limit: number = 20
  ): Promise<SearchResponse> {
    const params = new URLSearchParams({
      regex_pattern: regexPattern,
      ranking_by: rankingBy,
      limit: limit.toString(),
    });

    const response = await fetch(
      `${API_BASE_URL}/api/search/advanced?${params}`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
      }
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Erreur lors de la recherche avancée");
    }

    return response.json();
  },
};
