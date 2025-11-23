import React from 'react';
import { colors } from '../../styles/design-tokens';

interface InputProps {
  type?: 'text' | 'email' | 'password' | 'number';
  placeholder?: string;
  value?: string;
  onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void;
  label?: string;
  error?: string;
  disabled?: boolean;
  fullWidth?: boolean;
}

export function Input({
  type = 'text',
  placeholder,
  value,
  onChange,
  label,
  error,
  disabled = false,
  fullWidth = false,
}: InputProps) {
  return (
    <div className={`${fullWidth ? 'w-full' : ''}`}>
      {label && (
        <label className="block text-sm mb-2" style={{ color: colors.textDark }}>
          {label}
        </label>
      )}
      <input
        type={type}
        placeholder={placeholder}
        value={value}
        onChange={onChange}
        disabled={disabled}
        className="px-4 py-3 rounded-xl outline-none border-2 transition-all focus:border-opacity-100 disabled:opacity-50 w-full"
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