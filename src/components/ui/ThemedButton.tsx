import React from 'react';
import { colors } from '../../styles/design-tokens';

interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  children: React.ReactNode;
  onClick?: () => void;
  disabled?: boolean;
  fullWidth?: boolean;
  icon?: React.ReactNode;
}

export function Button({ 
  variant = 'primary', 
  size = 'md', 
  children, 
  onClick,
  disabled = false,
  fullWidth = false,
  icon
}: ButtonProps) {
  const baseStyles = 'rounded-full transition-all hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2';
  
  const variants = {
    primary: 'text-white',
    secondary: 'text-white',
    outline: 'bg-white border-2',
    ghost: 'bg-transparent hover:bg-opacity-10',
  };

  const sizes = {
    sm: 'px-4 py-2 text-sm',
    md: 'px-6 py-3 text-base',
    lg: 'px-8 py-4 text-lg',
  };

  const bgColors = {
    primary: colors.mainGreen2,
    secondary: colors.pointPink,
    outline: colors.white,
    ghost: 'transparent',
  };

  const borderColors = {
    primary: 'transparent',
    secondary: 'transparent',
    outline: colors.mainGreen1,
    ghost: 'transparent',
  };

  const textColors = {
    primary: colors.white,
    secondary: colors.white,
    outline: colors.mainGreen2,
    ghost: colors.textDark,
  };

  return (
    <button
      className={`${baseStyles} ${variants[variant]} ${sizes[size]} ${fullWidth ? 'w-full' : ''}`}
      style={{
        backgroundColor: bgColors[variant],
        borderColor: borderColors[variant],
        color: textColors[variant],
      }}
      onClick={onClick}
      disabled={disabled}
    >
      {icon && <span>{icon}</span>}
      <span>{children}</span>
    </button>
  );
}
