import { useState, useEffect } from 'react';

import { SearchBar } from '../components/SearchBar';
import { SearchResultCard } from '../components/SearchResultCard';
import { SuggestionsList } from '../components/SuggestionsList';
import { api } from '../lib/api';
import type { SearchResult, Suggestion } from '../types/api';

export function AdvancedRegexView() {
  const [regex, setRegex] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [isSearching, setIsSearching] = useState(false);
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [suggestionsError, setSuggestionsError] = useState<string | null>(null);
  const [isLoadingSuggestions, setIsLoadingSuggestions] = useState(false);

  useEffect(() => {
    loadSuggestions('0');
  }, []);

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

  const handleRegexSearch = async (value: string) => {
    setRegex(value);
    setError(null);
    setIsSearching(true);
    try {
      const response = await api.regex(value);
      setResults(response.results);
    } catch (err) {
      setResults([]);
      setError(err instanceof Error ? err.message : 'Regex search failed');
    } finally {
      setIsSearching(false);
    }
  };

  return (
    <section>
      <header className="view-header">
        <div>
          <p className="eyebrow">RegEx Search</p>
          <h1>Precision matching</h1>
          <p className="muted">Use regex patterns to find phrases and structures.</p>
        </div>
      </header>

      <SearchBar
        placeholder="Enter an Elasticsearch regex (e.g. .*dragon.*castle)"
        buttonLabel="Run regex"
        onSubmit={handleRegexSearch}
      />

      {isSearching && <p className="muted">Running regex query…</p>}
      {error && (
        <p className="error">
          {error}
        </p>
      )}

      <div className="stack" style={{ gap: '3rem' }}>
        <div className="stack">
          {regex && (
            <p className="muted">
              Showing matches for <strong>/{regex}/</strong>
            </p>
          )}
          <div className="results-grid">
            {results.map((result) => (
              <SearchResultCard key={result.id ?? crypto.randomUUID()} result={result} />
            ))}
          </div>
          {!results.length && !isSearching && <p className="muted">No matches yet.</p>}
        </div>

        {suggestions.length > 0 && (
          <aside className="panel">
            <div className="panel-header">
              <h3>Suggestions</h3>
              <button className="text-button" onClick={() => loadSuggestions('0')}>
                Refresh
              </button>
            </div>
            <SuggestionsList
              suggestions={suggestions}
              isLoading={isLoadingSuggestions}
              error={suggestionsError}
            />
          </aside>
        )}
      </div>
    </section>
  );
}


