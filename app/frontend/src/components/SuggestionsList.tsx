import { Link } from 'react-router-dom';

import type { Suggestion } from '../types/api';

type Props = {
  suggestions: Suggestion[];
  isLoading?: boolean;
  error?: string | null;
};

export function SuggestionsList({ suggestions, isLoading = false, error = null }: Props) {
  if (isLoading) {
    return <p className="muted">Loading suggestions…</p>;
  }

  if (error) {
    return (
      <p className="error">
        Suggestions error: <span>{error}</span>
      </p>
    );
  }

  if (!suggestions.length) {
    return <p className="muted">No suggestions available yet.</p>;
  }

  return (
    <ul className="suggestions">
      {suggestions.map((suggestion) => (
        <li key={suggestion.id ?? crypto.randomUUID()}>
          <div>
            <strong>{suggestion.title ?? 'Untitled'}</strong>
            <p className="muted">{suggestion.author ?? 'Unknown author'}</p>
          </div>
          {suggestion.id && (
            <Link className="text-link" to={`/books/${suggestion.id}`}>
              Open ↗
            </Link>
          )}
          {suggestion.similarity !== null && (
            <span className="score-chip secondary">{suggestion.similarity?.toFixed(3)}</span>
          )}
        </li>
      ))}
    </ul>
  );
}


