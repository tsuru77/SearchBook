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
        <li key={suggestion.id ?? crypto.randomUUID()} className="suggestion-item">
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', flex: 1 }}>
            {suggestion.image_url ? (
              <img
                src={suggestion.image_url}
                alt=""
                style={{ width: '40px', height: '60px', objectFit: 'cover', borderRadius: '4px', background: '#2a2a35' }}
              />
            ) : (
              <div style={{ width: '40px', height: '60px', borderRadius: '4px', background: '#2a2a35' }} />
            )}
            <div>
              <strong>{suggestion.title ?? 'Untitled'}</strong>
              <p className="muted" style={{ fontSize: '0.9rem' }}>{suggestion.author ?? 'Unknown author'}</p>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            {suggestion.id && (
              <Link className="text-link" to={`/books/${suggestion.id}`} style={{ fontSize: '0.9rem' }}>
                Open ↗
              </Link>
            )}
            {suggestion.similarity !== null && (
              <span className="score-chip secondary" style={{ fontSize: '0.75rem' }}>
                {suggestion.similarity?.toFixed(0)} views
              </span>
            )}
          </div>
        </li>
      ))}
    </ul>
  );
}


