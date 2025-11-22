import React from 'react';
import { Bookmark, ExternalLink } from 'lucide-react';
import { Card } from './ui/ThemedCard';
import { Badge } from './ui/Badge';
import { Button } from './ui/ThemedButton';
import { colors } from '../styles/design-tokens';

interface WelfareCardProps {
  title: string;
  summary: string;
  eligibility: string[];
  isBookmarked?: boolean;
  onBookmark?: () => void;
  onClick?: () => void;
}

export function WelfareCard({
  title,
  summary,
  eligibility,
  isBookmarked = false,
  onBookmark,
  onClick,
}: WelfareCardProps) {
  return (
    <Card variant="elevated" onClick={onClick}>
      <div className="space-y-4">
        {/* Header */}
        <div className="flex items-start justify-between">
          <h3 className="text-lg flex-1" style={{ color: colors.textDark }}>
            {title}
          </h3>
          <button
            onClick={(e) => {
              e.stopPropagation();
              onBookmark?.();
            }}
            className="p-2 rounded-full hover:bg-opacity-10 transition-all"
            style={{ backgroundColor: isBookmarked ? colors.pointYellow : colors.lightGray }}
          >
            <Bookmark 
              size={18} 
              fill={isBookmarked ? colors.textDark : 'none'}
              style={{ color: colors.textDark }}
            />
          </button>
        </div>

        {/* Summary */}
        <p className="text-sm line-clamp-3" style={{ color: colors.textSub }}>
          {summary}
        </p>

        {/* Eligibility Tags */}
        <div className="flex flex-wrap gap-2">
          {eligibility.map((tag, index) => (
            <Badge key={index} variant="default" size="sm">
              {tag}
            </Badge>
          ))}
        </div>

        {/* Actions */}
        <div className="flex items-center space-x-2 pt-2">
          <Button variant="primary" size="sm" icon={<ExternalLink size={14} />}>
            신청하기
          </Button>
          <Button variant="outline" size="sm">
            자세히 보기
          </Button>
        </div>
      </div>
    </Card>
  );
}
