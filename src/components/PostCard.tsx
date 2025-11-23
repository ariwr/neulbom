import React from 'react';
import { MessageCircle, AlertTriangle, Heart, Bookmark } from 'lucide-react';
import { Card } from './ui/ThemedCard';
import { Badge } from './ui/Badge';
import { colors } from '../styles/design-tokens';

interface PostCardProps {
  title: string;
  preview: string;
  // tags: string[];
  date: string;
  commentCount: number;
  hasCrisisFlag?: boolean;

  // ⭐ 신규 props
  likeCount: number;
  isLiked: boolean;
  isBookmarked: boolean;
  categoryLabel?: string;
  onToggleLike?: () => void;
  onToggleBookmark?: () => void;

  onClick?: () => void;
}

export function PostCard({
  title,
  preview,
  // tags,
  date,
  commentCount,
  hasCrisisFlag = false,

  likeCount,
  isLiked,
  isBookmarked,
  categoryLabel,

  onToggleLike,
  onToggleBookmark,

  onClick,
}: PostCardProps) {
  return (
    <Card padding="md" className="cursor-pointer" onClick={onClick}>
      <div className="space-y-3">
        {/* Crisis Flag */}
        {hasCrisisFlag && (
          <div className="flex items-center space-x-2">
            <AlertTriangle size={16} style={{ color: colors.error }} />
            <span className="text-xs" style={{ color: colors.error }}>
              위기 감지됨
            </span>
          </div>
        )}

        {/* Category */}
        {categoryLabel && (
          <Badge variant="level1" size="sm">
            {categoryLabel}
          </Badge>
        )}

        {/* Title */}
        <h3 className="text-base font-bold" style={{ color: colors.textDark }}>
          {title}
        </h3>
    

        {/* Preview */}
        <p className="text-sm line-clamp-2" style={{ color: colors.textSub }}>
          {preview}
        </p>

        {/* Tags */}
        {/* <div className="flex flex-wrap gap-2">
          {tags.map((tag, index) => (
            <Badge key={index} variant="default" size="sm">
              #{tag}
            </Badge>
          ))}
        </div> */}

        {/* Meta */}
        <div
          className="flex items-center justify-between pt-2 border-t"
          style={{ borderColor: colors.lightGray }}
        >
          {/* Left side: 날짜 */}
          <span className="text-xs" style={{ color: colors.textSub }}>
            {date}
          </span>

          {/* Right side: 댓글, 좋아요, 북마크 */}
          <div className="flex items-center space-x-3">

            {/* 댓글 수 */}
            <div className="flex items-center space-x-1">
              <MessageCircle size={14} style={{ color: colors.textSub }} />
              <span className="text-xs" style={{ color: colors.textSub }}>
                {commentCount}
              </span>
            </div>

            {/* 좋아요 */}
            <div
              className="flex items-center space-x-1 cursor-pointer"
              onClick={(e) => {
                e.stopPropagation(); // 카드 클릭과 분리
                onToggleLike?.();
              }}
            >
              <Heart
                size={14}
                fill={isLiked ? colors.pointPink : 'none'}
                style={{ color: isLiked ? colors.pointPink : colors.textSub }}
              />
              <span className="text-xs" style={{ color: colors.textSub }}>
                {likeCount}
              </span>
            </div>

            {/* 북마크 */}
            <div
              className="cursor-pointer"
              onClick={(e) => {
                e.stopPropagation();
                onToggleBookmark?.();
              }}
            >
              <Bookmark
                size={14}
                fill={isBookmarked ? colors.mainGreen2 : 'none'}
                style={{
                  color: isBookmarked ? colors.mainGreen2 : colors.textSub,
                }}
              />
            </div>
          </div>
        </div>
      </div>
    </Card>
  );
}
