import { useState } from 'react';

import { SearchBar } from '../components/SearchBar';
import { SearchResultCard } from '../components/SearchResultCard';
import { SuggestionsList } from '../components/SuggestionsList';
import { api } from '../lib/api';
import type { SearchResult, Suggestion } from '../types/api';

export function HomeSearchView() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [selectedBookId, setSelectedBookId] = useState<string | null>(null);
  const [isSearching, setIsSearching] = useState(false);
  const [searchError, setSearchError] = useState<string | null>(null);
  const [suggestionsError, setSuggestionsError] = useState<string | null>(null);
  const [isLoadingSuggestions, setIsLoadingSuggestions] = useState(false);

  const handleSearch = async (value: string) => {
    setQuery(value);
    setSearchError(null);
    setIsSearching(true);
    try {
      const response = await api.search(value);
      setResults(response.results);
      const topResultId = response.results[0]?.id ?? null;
      setSelectedBookId(topResultId);
      if (topResultId) {
        await loadSuggestions(topResultId);
      } else {
        setSuggestions([]);
      }
    } catch (error) {
      setSearchError(error instanceof Error ? error.message : 'Unable to search');
      setResults([]);
    } finally {
      setIsSearching(false);
    }
  };

  const loadSuggestions = async (bookId: string) => {
    setIsLoadingSuggestions(true);
    setSuggestionsError(null);
    try {
      const response = await api.suggestions(bookId);
      setSuggestions(response.results);
    } catch (error) {
      setSuggestionsError(error instanceof Error ? error.message : 'Unable to fetch suggestions');
      setSuggestions([]);
    } finally {
      setIsLoadingSuggestions(false);
    }
  };

  return (
    <section>
      <header className="view-header">
        <div>
          <p className="eyebrow">Keyword Search</p>
          <h1>Find books instantly</h1>
          <p className="muted">Powered by Elasticsearch BM25 + graph centrality.</p>
        </div>
      </header>

      <SearchBar onSubmit={handleSearch} />

      {isSearching && <p className="muted">Searching library…</p>}
      {searchError && (
        <p className="error">
          {searchError}
        </p>
      )}

      <div className="grid two-column">
        <div>
          <h2>Results {query && <span className="muted">for “{query}”</span>}</h2>
          {results.length === 0 && !isSearching && <p className="muted">No results yet. Try a query.</p>}
          <div className="stack">
            {results.map((result) => (
              <SearchResultCard key={result.id ?? crypto.randomUUID()} result={result} />
            ))}
          </div>
        </div>

        <aside className="panel">
          <div className="panel-header">
            <h3>Suggestions</h3>
            {selectedBookId && (
              <button className="text-button" onClick={() => loadSuggestions(selectedBookId)}>
                Refresh
              </button>
            )}
          </div>
          <SuggestionsList
            suggestions={suggestions}
            isLoading={isLoadingSuggestions}
            error={suggestionsError}
          />
        </aside>
      </div>
    </section>
  );
}


