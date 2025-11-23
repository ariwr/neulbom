// src/pages/Community.tsx
import React, { useMemo, useState } from 'react';
import { PenSquare, Search, TrendingUp } from 'lucide-react';
import { Card } from '../components/ui/ThemedCard';
import { Button } from '../components/ui/ThemedButton';
import { Badge } from '../components/ui/Badge';
import { PostCard } from '../components/PostCard';
import { colors } from '../styles/design-tokens';
import type { Post } from '../services/postService';
import type { Page } from '../types/page';

interface CommunityProps {
  posts: Post[];
  onNavigate?: (page: Page) => void;
  onPostClick?: (id: number) => void;
  onToggleLike?: (id: number) => void;
  onToggleBookmark?: (id: number) => void;
}

type CategoryId = 'all' | 'info' | 'counsel' | 'free';
type SortOption = 'popular' | 'recent';

export function Community({
  posts,
  onNavigate,
  onPostClick,
  onToggleLike,
  onToggleBookmark,
}: CommunityProps) {
  // 카테고리: 전체 / 정보공유 / 고민상담 / 자유게시판
  const [activeCategory, setActiveCategory] = useState<CategoryId>('all');
  // 정렬: 인기순(좋아요순) / 최신순(날짜순)
  const [sortOption, setSortOption] = useState<SortOption>('popular');

  const categoryTabs = [
    { id: 'all' as CategoryId, label: '전체' },
    { id: 'info' as CategoryId, label: '정보공유' },
    { id: 'counsel' as CategoryId, label: '고민상담' },
    { id: 'free' as CategoryId, label: '자유게시판' },
  ];

  // 카테고리 + 정렬 적용된 게시글 리스트
  const filteredAndSortedPosts = useMemo(() => {
    // 1) 카테고리 필터
    const filtered = posts.filter((post) => {
      if (activeCategory === 'all') return true;
      return post.category === activeCategory;
    });

    // 2) 정렬
    const sorted = [...filtered].sort((a, b) => {
      if (sortOption === 'popular') {
        // 좋아요 수 기준 내림차순
        return b.likeCount - a.likeCount;
      }

      // 최신순: 날짜 내림차순
      const dateA = new Date(a.date).getTime();
      const dateB = new Date(b.date).getTime();
      return dateB - dateA;
    });

    return sorted;
  }, [posts, activeCategory, sortOption]);

  return (
    <div
      className="min-h-screen pb-20"
      style={{ backgroundColor: colors.lightGray }}
    >
      {/* Header */}
      <section
        className="py-12 px-4"
        style={{
          background: `linear-gradient(135deg, ${colors.pointPink} 0%, ${colors.pointYellow} 100%)`,
        }}
      >
        <div className="max-w-4xl mx-auto">
          <h1 className="text-3xl text-white mb-1 text-center font-bold">
            익명 커뮤니티
          </h1>
          <p className="text-s text-center mb-6" style={{ color: '#fff' }}>
            모든 게시글은 닉네임이 아닌 익명으로 작성됩니다.
          </p>

          {/* Search */}
          <Card variant="elevated" padding="sm" className="rounded-full">
            <div className="flex items-center space-x-3">
              <Search size={20} style={{ color: colors.textSub }} />
              <input
                type="text"
                placeholder="게시글 검색"
                className="flex-1 outline-none text-base bg-transparent"
                style={{ color: colors.textDark }}
              />
            </div>
          </Card>
        </div>
      </section>

      {/* Content */}
      <div className="max-w-4xl mx-auto px-4 py-6">
        {/* ------ 카테고리 영역 (첫 줄, 중앙 정렬) ------ */}
        <div className="w-full flex justify-center mb-4">
          <div className="flex flex-wrap items-center gap-2">
            {categoryTabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveCategory(tab.id)}
                className="px-4 py-2 rounded-full text-sm transition-all"
                style={{
                  backgroundColor:
                    activeCategory === tab.id ? colors.mainGreen2 : colors.lightGray,
                  color:
                    activeCategory === tab.id ? colors.white : colors.textSub,
                }}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>

        {/* ------ 정렬 + 글쓰기 영역 (두 번째 줄) ------ */}
        <div className="flex items-center justify-between w-full mb-6">
          {/* 왼쪽: 정렬 버튼 */}
          <div className="flex items-center gap-2 text-xs">
            <button
              onClick={() => setSortOption('popular')}
              className="px-3 py-1 rounded-full transition-all"
              style={{
                backgroundColor:
                  sortOption === 'popular' ? colors.mainGreen2 : colors.lightGray,
                color:
                  sortOption === 'popular' ? colors.white : colors.textSub,
              }}
            >
              인기순
            </button>
            <button
              onClick={() => setSortOption('recent')}
              className="px-3 py-1 rounded-full transition-all"
              style={{
                backgroundColor:
                  sortOption === 'recent' ? colors.mainGreen2 : colors.lightGray,
                color:
                  sortOption === 'recent' ? colors.white : colors.textSub,
              }}
            >
              최신순
            </button>
          </div>

          {/* 오른쪽: 글쓰기 */}
          <div className="flex items-center justify-end">
            <Button
              variant="primary"
              size="sm"
              icon={<PenSquare size={16} />}
              onClick={() => onNavigate?.('post-submit')}
            >
              글쓰기
            </Button>
          </div>
        </div>

        {/* Post List */}
        <div className="space-y-4">
          {filteredAndSortedPosts.map((post) => (
            <PostCard
              key={post.id}
              title={post.title}
              preview={post.preview}
              // tags={post.tags}
              date={post.date}
              commentCount={post.commentCount}
              hasCrisisFlag={post.hasCrisisFlag}
              likeCount={post.likeCount}
              isLiked={post.isLiked}
              isBookmarked={post.isBookmarked}
              categoryLabel={
                post.category === 'info'
                  ? '정보공유'
                  : post.category === 'counsel'
                  ? '고민상담'
                  : post.category === 'free'
                  ? '자유게시판'
                  : '전체'
              }
              onToggleLike={() => onToggleLike?.(post.id)}
              onToggleBookmark={() => onToggleBookmark?.(post.id)}
              onClick={() => onPostClick?.(post.id)}
            />
          ))}
        </div>

        {/* Pagination (임시) */}
        <div className="flex items-center justify-center space-x-2 mt-8">
          {[1, 2, 3, 4, 5].map((page) => (
            <button
              key={page}
              className="w-10 h-10 rounded-full text-sm transition-all"
              style={{
                backgroundColor:
                  page === 1 ? colors.mainGreen2 : colors.lightGray,
                color: page === 1 ? colors.white : colors.textSub,
              }}
            >
              {page}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
