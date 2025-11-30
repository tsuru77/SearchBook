export type SearchResult = {
  id: string | null;
  title: string | null;
  author: string | null;
  score: number | null;
  centrality_score: number | null;
  image_url: string | null;
  snippet: string | null;
};

export type SearchResponse = {
  total: number;
  results: SearchResult[];
};

export type AdvancedSearchResponse = SearchResponse & {
  regex: string;
};

export type BookResponse = {
  id: string | null;
  title: string | null;
  author: string | null;
  text: string | null;
  word_count: number | null;
  centrality_score: number | null;
  image_url: string | null;
  metadata?: Record<string, string | number | null>;
};

export type Suggestion = {
  id: string | null;
  title: string | null;
  author: string | null;
  similarity: number | null;
};

export type SuggestionsResponse = {
  book_id: string;
  results: Suggestion[];
};


