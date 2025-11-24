import React, { memo } from 'react';
import { Bookmark } from 'lucide-react';
import { Card } from './ui/ThemedCard';
import { Badge } from './ui/Badge';
import { colors } from '../styles/design-tokens';

interface WelfareCardProps {
  title: string;
  summary?: string; // 옵셔널로 변경
  eligibility: string[];
  isBookmarked?: boolean;
  // 이벤트를 인자로 받을 수 있도록 타입 수정
  onBookmark?: () => void;
  onClick?: () => void;
}

export const WelfareCard = memo(function WelfareCard({
  title,
  summary,
  eligibility,
  isBookmarked = false,
  onBookmark,
  onClick,
}: WelfareCardProps) {
  return (
    <Card
      variant="elevated"
      // 카드 클릭시 바로 상세 페이지로 이동
      onClick={onClick}
      className="cursor-pointer hover:opacity-90 transition-opacity"
    >
      <div className="space-y-4">
        {/* Header */}
        <div className="rounded-full mx-auto mb-1 flex items-center justify-center">
          <h3 className="text-lg flex-1" style={{ color: colors.textDark }}>
            {title}
          </h3>
          <button
            onClick={(e: React.MouseEvent<HTMLButtonElement>) => {
              e.stopPropagation(); // 카드 클릭 이벤트 막기
              onBookmark?.();
            }}
            className="p-2 rounded-full hover:bg-opacity-10 transition-all"
            style={{
              backgroundColor: isBookmarked
                ? colors.lightGray
                : colors.lightGray,
            }}
          >
            <Bookmark
              size={18}
              fill={isBookmarked ? colors.textDark : 'none'}
              style={{ color: colors.textDark }}
            />
          </button>
        </div>

        {/* Summary */}
        {summary && summary.trim() ? (
          <p className="text-sm line-clamp-3" style={{ color: colors.textSub }}>
            {summary}
          </p>
        ) : (
          <p className="text-sm line-clamp-3 italic" style={{ color: colors.textSub }}>
            상세 정보를 확인해주세요.
          </p>
        )}

        {/* Eligibility Tags */}
        <div className="flex flex-wrap gap-2">
          {eligibility.map((tag, index) => (
            <Badge key={index} variant="default" size="sm">
              {tag}
            </Badge>
          ))}
        </div>
      </div>
    </Card>
  );
});