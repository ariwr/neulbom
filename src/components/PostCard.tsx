import React from 'react';
import { MessageCircle, AlertTriangle } from 'lucide-react';
import { Card } from './ui/ThemedCard';
import { Badge } from './ui/Badge';
import { colors } from '../styles/design-tokens';

interface PostCardProps {
  title: string;
  preview: string;
  tags: string[];
  date: string;
  commentCount: number;
  hasCrisisFlag?: boolean;
  onClick?: () => void;
}

export function PostCard({
  title,
  preview,
  tags,
  date,
  commentCount,
  hasCrisisFlag = false,
  onClick,
}: PostCardProps) {
  return (
    <Card onClick={onClick} padding="md">
      <div className="space-y-3">
        {/* Crisis Flag */}
        {hasCrisisFlag && (
          <div className="flex items-center space-x-2 mb-2">
            <AlertTriangle size={16} style={{ color: colors.error }} />
            <span className="text-xs" style={{ color: colors.error }}>
              위기 감지됨
            </span>
          </div>
        )}

        {/* Title */}
        <h3 className="text-base" style={{ color: colors.textDark }}>
          {title}
        </h3>

        {/* Preview */}
        <p className="text-sm line-clamp-2" style={{ color: colors.textSub }}>
          {preview}
        </p>

        {/* Tags */}
        <div className="flex flex-wrap gap-2">
          {tags.map((tag, index) => (
            <Badge key={index} variant="default" size="sm">
              #{tag}
            </Badge>
          ))}
        </div>

        {/* Meta */}
        <div className="flex items-center justify-between pt-2 border-t" style={{ borderColor: colors.lightGray }}>
          <span className="text-xs" style={{ color: colors.textSub }}>
            {date}
          </span>
          <div className="flex items-center space-x-1">
            <MessageCircle size={14} style={{ color: colors.textSub }} />
            <span className="text-xs" style={{ color: colors.textSub }}>
              {commentCount}
            </span>
          </div>
        </div>
      </div>
    </Card>
  );
}
