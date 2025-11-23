import React, { CSSProperties } from 'react';
import { colors } from '../../styles/design-tokens';

interface CardProps {
  children: React.ReactNode;
  variant?: 'default' | 'elevated' | 'outlined';
  padding?: 'sm' | 'md' | 'lg';
  className?: string;
  onClick?: React.MouseEventHandler<HTMLDivElement>;
  style?: CSSProperties;
}

export function Card({ 
  children, 
  variant = 'default',
  padding = 'md',
  className = '',
  onClick,
}: CardProps) {
  const paddingClasses = {
    sm: 'p-4',
    md: 'p-6',
    lg: 'p-8',
  };

  const variantStyles = {
    default: {
      backgroundColor: colors.white,
      boxShadow: '0 0 20px rgba(0, 0, 0, 0.1)',
    },
    elevated: {
      backgroundColor: colors.white,
      boxShadow: '0 0 20px rgba(0, 0, 0, 0.1)',
    },
    outlined: {
      backgroundColor: colors.white,
      border: `1px solid ${colors.lightGray}`,
    },
  };

  return (
    <div
      className={`rounded-2xl transition-all shadow-soft ${paddingClasses[padding]} ${onClick ? 'cursor-pointer hover:shadow-lg' : ''} ${className}`}
      style={variantStyles[variant]}
      onClick={onClick}
    >
      {children}
    </div>
  );
}