/**
 * Types TypeScript pour les appels API
 */

export interface DocumentResult {
  doc_id: string;
  title: string;
  author: string | null;
  word_count: number | null;
  occurrences: number;
  pagerank_score: number | null;
  ranking_position: number;
}

export interface SuggestionResult {
  doc_id: string;
  title: string;
  author: string | null;
  jaccard_score: number;
}

export interface SearchResponse {
  query: string;
  ranking_by: string;
  total_results: number;
  results: DocumentResult[];
  suggestions: SuggestionResult[];
  execution_time_ms: number | null;
}

export type RankingType = "occurrences" | "pagerank";
