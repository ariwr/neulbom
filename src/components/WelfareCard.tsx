import React, { memo } from 'react';
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
      // Card 자체도 클릭 가능 (상세로 이동 등)
      onClick={onClick}
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
          <Button
            variant="outline"
            size="sm"
            onClick={(e: React.MouseEvent<HTMLButtonElement>) => {
              e.stopPropagation(); // 여기서도 카드 onClick 막고
              onClick?.();        // 상세 페이지 이동 콜백 호출
            }}
          >
            자세히 보기
          </Button>
        </div>
      </div>
    </Card>
  );
});