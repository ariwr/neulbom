import React, { useState, useMemo, useEffect } from 'react';
import { Search, Grid, List } from 'lucide-react';
import { Card } from '../components/ui/ThemedCard';
import { Button } from '../components/ui/ThemedButton';
import { Badge } from '../components/ui/Badge';
import { WelfareCard } from '../components/WelfareCard';
import { colors } from '../styles/design-tokens';
import type { Welfare } from '../services/welfareService';
import { searchWelfare } from '../services/welfareService';
import type { Page } from '../types/page';

interface WelfareProps {
  onNavigate?: (page: Page) => void;
  bookmarkedIds: number[];
  onToggleBookmark: (id: number) => void;
  initialQuery?: string;   // ★ Home에서 검색어 전달 받을 준비
  onSelectWelfare?: (id: number) => void;
}

export function Welfare({
  onNavigate,
  bookmarkedIds,
  onToggleBookmark,
  onSelectWelfare,
  initialQuery = '',  // 없으면 빈값
}: WelfareProps) {
  const [searchQuery, setSearchQuery] = useState(initialQuery);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [welfares, setWelfares] = useState<Welfare[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  
  // 페이지네이션 상태
  const [page, setPage] = useState(1);
  const limit = 10;

  // 검색어가 변경되면 페이지 초기화 및 API 호출
  useEffect(() => {
    setPage(1);
  }, [searchQuery]);

  // 검색어 또는 페이지가 변경될 때 API 호출
  useEffect(() => {
    const loadWelfares = async () => {
      setIsLoading(true);
      try {
        const params: any = {
          skip: (page - 1) * limit,
          limit: limit,
        };
        if (searchQuery.trim()) {
          params.keyword = searchQuery.trim();
        }
        const data = await searchWelfare(params);
        setWelfares(data);
      } catch (error) {
        console.error('복지 정보 검색 실패:', error);
        setWelfares([]);
      } finally {
        setIsLoading(false);
      }
    };

    loadWelfares();
  }, [searchQuery, page]);

  // 초기 검색어 설정
  useEffect(() => {
    if (initialQuery) {
      setSearchQuery(initialQuery);
    }
  }, [initialQuery]);

  // 프론트엔드 필터링 (추가 필터링이 필요한 경우)
  const filtered = useMemo(() => {
    // API에서 이미 검색 결과를 받아오므로, 추가 필터링만 수행
    return welfares;
  }, [welfares]);

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
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    // 검색 실행 (useEffect가 자동으로 처리)
                  }
                }}
                className="flex-1 outline-none text-base bg-transparent"
                style={{ color: colors.textDark }}
              />
            </div>
          </Card>

          {/* 태그 (빠른 필터) */}
          <div className="flex flex-wrap gap-2 mt-4 justify-center">
            {['전체', '노인돌봄', '장애인지원', '아동돌봄', '의료지원'].map((tag) => (
              <Badge 
                key={tag} 
                variant="default" 
                size="md"
                onClick={() => {
                  if (tag === '전체') {
                    setSearchQuery('');
                  } else {
                    setSearchQuery(tag);
                  }
                }}
                style={{ cursor: 'pointer' }}
              >
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
            <span className="text-sm" style={{ color: colors.textSub }}>
              {isLoading ? '검색 중...' : `총 ${filtered.length}개`}
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
        {isLoading ? (
          <div className="text-center py-12">
            <p className="text-sm" style={{ color: colors.textSub }}>
              검색 중...
            </p>
          </div>
        ) : filtered.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-sm" style={{ color: colors.textSub }}>
              검색 결과가 없습니다. 다른 키워드로 검색해보세요.
            </p>
          </div>
        ) : (
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
        )}

        {!isLoading && (
          <div className="flex justify-center items-center space-x-4 mt-8">
            <Button 
              variant="outline" 
              size="md"
              disabled={page === 1}
              onClick={() => setPage(p => Math.max(1, p - 1))}
            >
              이전
            </Button>
            <span className="text-sm" style={{ color: colors.textDark }}>
              {page} 페이지
            </span>
            <Button 
              variant="outline" 
              size="md"
              disabled={welfares.length < limit}
              onClick={() => setPage(p => p + 1)}
            >
              다음
            </Button>
          </div>
        )}
      </div>
    </div>
  );
}
