import React, { useState, useMemo, useEffect } from 'react';
import { Search, Filter, Grid, List } from 'lucide-react';
import { Card } from '../components/ui/ThemedCard';
import { Button } from '../components/ui/ThemedButton';
import { Badge } from '../components/ui/Badge';
import { WelfareCard } from '../components/WelfareCard';
import { colors } from '../styles/design-tokens';
import type { Welfare } from '../services/welfareService';
import type { Page } from '../types/page';

interface WelfareProps {
  onNavigate?: (page: Page) => void;
  welfares: Welfare[];
  bookmarkedIds: number[];
  onToggleBookmark: (id: number) => void;
  initialQuery?: string;   // ★ Home에서 검색어 전달 받을 준비
  onSelectWelfare?: (id: number) => void;
}

export function Welfare({
  onNavigate,
  welfares,
  bookmarkedIds,
  onToggleBookmark,
  onSelectWelfare,
  initialQuery = '',  // 없으면 빈값
}: WelfareProps) {
  const [searchQuery, setSearchQuery] = useState(initialQuery);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');

  // ⭐ "프론트 검색"은 임시 기능 → 나중에 API fetch로 대체 가능
  const filtered = useMemo(() => {
    const q = searchQuery.trim().toLowerCase();
    if (!q) return welfares;

    return welfares.filter((w) => {
      const title = (w.title ?? '').toLowerCase();
      const summary = (w.summary ?? '').toLowerCase();
      const elig = w.eligibility.join(' ').toLowerCase();
      return (
        title.includes(q) ||
        summary.includes(q) ||
        elig.includes(q)
      );
    });
  }, [welfares, searchQuery]);

  return (
    <div className="min-h-screen pb-20" style={{ backgroundColor: colors.lightGray }}>
      {/* ================= 상단 헤더 ================= */}
      <section 
        className="py-12 px-4"
        style={{
          background: `linear-gradient(135deg, ${colors.mainGreen1} 0%, ${colors.mainGreen2} 100%)`,
        }}
      >
        <div className="max-w-4xl mx-auto">
          <h1 className="text-2xl text-white mb-6 text-center">
            복지 서비스 검색
          </h1>

          {/* 검색창 */}
          <Card variant="elevated" padding="sm" className="rounded-full">
            <div className="flex items-center space-x-3">
              <Search size={20} style={{ color: colors.textSub }} />
              <input
                type="text"
                placeholder="필요한 복지 서비스를 검색하세요"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="flex-1 outline-none text-base bg-transparent"
                style={{ color: colors.textDark }}
              />
            </div>
          </Card>

          {/* 태그 (빠른 필터) */}
          <div className="flex flex-wrap gap-2 mt-4 justify-center">
            {['전체', '노인돌봄', '장애인지원', '아동돌봄', '의료지원'].map((tag) => (
              <Badge key={tag} variant="default" size="md">
                {tag}
              </Badge>
            ))}
          </div>
        </div>
      </section>

      {/* ================= 정렬/뷰컨트롤 ================= */}
      <div className="max-w-7xl mx-auto px-4 py-6">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-2">
            <Button variant="outline" size="sm" icon={<Filter size={16} />}>
              필터
            </Button>
            <span className="text-sm" style={{ color: colors.textSub }}>
              총 {filtered.length}개
            </span>
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={() => setViewMode('grid')}
              className="p-2 rounded-lg"
              style={{
                backgroundColor: viewMode === 'grid' ? colors.mainGreen1 : colors.lightGray,
                color: viewMode === 'grid' ? colors.white : colors.textSub,
              }}
            >
              <Grid size={18} />
            </button>
            <button
              onClick={() => setViewMode('list')}
              className="p-2 rounded-lg"
              style={{
                backgroundColor: viewMode === 'list' ? colors.mainGreen1 : colors.lightGray,
                color: viewMode === 'list' ? colors.white : colors.textSub,
              }}
            >
              <List size={18} />
            </button>
          </div>
        </div>

        {/* ================= 목록 ================= */}
        <div className={`grid gap-6 ${viewMode === 'grid'
            ? 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3'
            : 'grid-cols-1'
          }`}
        >
          {filtered.map((welfare) => (
            <WelfareCard
              key={welfare.id}
              title={welfare.title}
              summary={welfare.summary}
              eligibility={welfare.eligibility}
              isBookmarked={bookmarkedIds.includes(welfare.id)}
              onBookmark={() => onToggleBookmark(welfare.id)}
              onClick={() => onSelectWelfare?.(welfare.id)}
            />
          ))}
        </div>

        <div className="text-center mt-8">
          <Button variant="outline" size="md">
            더 보기
          </Button>
        </div>
      </div>
    </div>
  );
}