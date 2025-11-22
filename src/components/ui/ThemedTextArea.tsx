import React from 'react';
import { colors } from '../../styles/design-tokens';

interface TextAreaProps {
  placeholder?: string;
  value?: string;
  onChange?: (e: React.ChangeEvent<HTMLTextAreaElement>) => void;
  label?: string;
  error?: string;
  disabled?: boolean;
  rows?: number;
  fullWidth?: boolean;
}

export function TextArea({
  placeholder,
  value,
  onChange,
  label,
  error,
  disabled = false,
  rows = 4,
  fullWidth = false,
}: TextAreaProps) {
  return (
    <div className={`${fullWidth ? 'w-full' : ''}`}>
      {label && (
        <label className="block text-sm mb-2" style={{ color: colors.textDark }}>
          {label}
        </label>
      )}
      <textarea
        placeholder={placeholder}
        value={value}
        onChange={onChange}
        disabled={disabled}
        rows={rows}
        className="px-4 py-3 rounded-xl outline-none border-2 transition-all focus:border-opacity-100 disabled:opacity-50 w-full resize-none"
        style={{
          backgroundColor: colors.white,
          borderColor: error ? colors.error : colors.lightGray,
          color: colors.textDark,
        }}
      />
      {error && (
        <p className="text-sm mt-1" style={{ color: colors.error }}>
          {error}
        </p>
      )}
    </div>
  );
}
