import { useState } from 'react';

type SearchBarProps = {
  defaultValue?: string;
  placeholder?: string;
  buttonLabel?: string;
  onSubmit: (value: string) => void;
};

export function SearchBar({
  defaultValue = '',
  placeholder = 'Search for books...',
  buttonLabel = 'Search',
  onSubmit,
}: SearchBarProps) {
  const [value, setValue] = useState(defaultValue);

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!value.trim()) {
      return;
    }
    onSubmit(value.trim());
  };

  return (
    <form className="search-bar" onSubmit={handleSubmit}>
      <input
        className="search-input"
        type="text"
        value={value}
        placeholder={placeholder}
        onChange={(event) => setValue(event.target.value)}
      />
      <button className="primary-button" type="submit">
        {buttonLabel}
      </button>
    </form>
  );
}


