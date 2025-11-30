import { useState } from 'react';

import { SearchBar } from '../components/SearchBar';
import { SearchResultCard } from '../components/SearchResultCard';
import { api } from '../lib/api';
import type { SearchResult } from '../types/api';

export function AdvancedRegexView() {
  const [regex, setRegex] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [isSearching, setIsSearching] = useState(false);

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
          <p className="muted">Use ES-compatible regex patterns to find phrases and structures.</p>
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

      <div className="stack">
        {regex && (
          <p className="muted">
            Showing matches for <strong>/{regex}/</strong>
          </p>
        )}
        {results.map((result) => (
          <SearchResultCard key={result.id ?? crypto.randomUUID()} result={result} />
        ))}
        {!results.length && !isSearching && <p className="muted">No matches yet.</p>}
      </div>
    </section>
  );
}


