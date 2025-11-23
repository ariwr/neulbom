import React from 'react';
import { colors } from '../../styles/design-tokens';

interface BadgeProps {
  children: React.ReactNode;
  variant?: 'level1' | 'level2' | 'level3' | 'crisis' | 'default';
  size?: 'sm' | 'md' | 'lg';
}

export function Badge({ children, variant = 'default', size = 'md' }: BadgeProps) {
  const sizes = {
    sm: 'px-2 py-1 text-xs',
    md: 'px-3 py-1 text-sm',
    lg: 'px-4 py-2 text-base',
  };

  const variants = {
    level1: { bg: colors.mainGreen1, text: colors.white },
    level2: { bg: colors.mainGreen2, text: colors.white },
    level3: { bg: colors.pointYellow, text: colors.textDark },
    crisis: { bg: colors.error, text: colors.white },
    default: { bg: colors.lightGray, text: colors.textSub },
  };

  const style = variants[variant];

  return (
    <span
      className={`inline-flex items-center rounded-full ${sizes[size]}`}
      style={{
        backgroundColor: style.bg,
        color: style.text,
      }}
    >
      {children}
    </span>
  );
}