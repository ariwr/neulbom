import React, { useState, useEffect } from 'react';
import { Search } from 'lucide-react';
import { WelfareCard } from '../components/WelfareCard';
import { Card } from '../components/ui/ThemedCard';
import { colors } from '../styles/design-tokens';
import type { Welfare } from '../services/welfareService';
import { getRecentWelfares, getPopularWelfares } from '../services/welfareService';
import { getAuthToken } from '../config/api';
import type { Page } from '../types/page';

interface HomeProps {
  onNavigate?: (page: Page) => void;
  bookmarkedIds: number[];
  onToggleBookmark: (id: number) => void;
  // 복지 카드 클릭 시 상세로 이동시키는 콜백
  onSelectWelfare?: (id: number) => void;
  // 검색어 전달 콜백
  onSearchQuery?: (query: string) => void;
}

export function Home({
  onNavigate,
  bookmarkedIds,
  onToggleBookmark,
  onSelectWelfare,
  onSearchQuery,
}: HomeProps) {
  const [keyword, setKeyword] = useState('');
  const [recentWelfares, setRecentWelfares] = useState<Welfare[]>([]);
  const [popularWelfares, setPopularWelfares] = useState<Welfare[]>([]);
  const [isLoadingRecent, setIsLoadingRecent] = useState(true);
  const [isLoadingPopular, setIsLoadingPopular] = useState(true);

  // 최근 본 복지 정보 로드 (로그인한 사용자만)
  useEffect(() => {
    const loadRecentWelfares = async () => {
      setIsLoadingRecent(true);
      try {
        const data = await getRecentWelfares(6);
        setRecentWelfares(data);
      } catch (error) {
        // 개발 모드에서만 로깅
        if (import.meta.env.DEV) {
          console.error('최근 본 복지 정보 로드 실패:', error);
        }
        setRecentWelfares([]);
      } finally {
        setIsLoadingRecent(false);
      }
    };

    // 로그인한 경우에만 로드
    if (getAuthToken()) {
      loadRecentWelfares();
    } else {
      setIsLoadingRecent(false);
    }
  }, []);

  // 인기 복지 정보 로드 (모든 사용자)
  useEffect(() => {
    const loadPopularWelfares = async () => {
      setIsLoadingPopular(true);
      try {
        const data = await getPopularWelfares(6);
        setPopularWelfares(data);
      } catch (error) {
        // 개발 모드에서만 로깅
        if (import.meta.env.DEV) {
          console.error('인기 복지 정보 로드 실패:', error);
        }
        setPopularWelfares([]);
      } finally {
        setIsLoadingPopular(false);
      }
    };

    loadPopularWelfares();
  }, []);

  const handleSearch = () => {
    const q = keyword.trim();
    if (!q) return;

    // 검색어를 상위 컴포넌트에 전달
    onSearchQuery?.(q);
    // 복지서비스 검색 페이지로 이동
    onNavigate?.('welfare');
  };

  return (
    <div className="pb-20">
      {/* Header */}
      <section
        className="py-12 px-4"
        style={{
          background: `linear-gradient(135deg, ${colors.mainGreen1} 0%, ${colors.mainGreen2} 100%)`,
        }}
      >
        <div className="max-w-4xl mx-auto">
          <h1 className="text-2xl text-white mb-6 text-center font-bold">
            어떤 복지 서비스를 찾고 계신가요?
          </h1>

          {/* 검색바 카드 */}
          <Card variant="elevated" padding="sm" className="rounded-full">
            <div className="flex items-center space-x-3">
              <Search size={20} style={{ color: colors.textSub }} />
              <input
                type="text"
                placeholder="복지 서비스를 검색해보세요 (예: 노인돌봄, 장애인)"
                value={keyword}
                onChange={(e) => setKeyword(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                className="flex-1 outline-none text-base"
                style={{ color: colors.textDark }}
              />
            </div>
          </Card>
        </div>
      </section>

      {/* 최근 본 복지 정보 섹션 */}
      {(getAuthToken() || recentWelfares.length > 0) && (
        <section className="max-w-7xl mx-auto px-4 mt-8">
          <div className="flex items-center justify-between mb-6">
            <h2
              className="text-base sm:text-lg md:text-xl font-semibold"
              style={{ color: colors.textDark }}
            >
              최근 본 복지 정보
            </h2>
            <button
              onClick={() => onNavigate?.('welfare')}
              className="text-xs sm:text-sm md:text-base font-medium hover:opacity-70 transition-opacity"
              style={{ color: colors.mainGreen2 }}
            >
              전체보기 →
            </button>
          </div>

          {isLoadingRecent ? (
            <div className="text-center py-8">
              <p className="text-sm" style={{ color: colors.textSub }}>
                로딩 중...
              </p>
            </div>
          ) : recentWelfares.length === 0 ? (
            <div className="text-center py-8">
              <p className="text-sm" style={{ color: colors.textSub }}>
                아직 본 복지 정보가 없습니다. 복지 정보를 검색해보세요!
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-5 md:gap-6">
              {recentWelfares.slice(0, 3).map((welfare) => (
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
        </section>
      )}

      {/* 자주 보는 복지 정보 (인기 복지 정보) 섹션 */}
      <section className="max-w-7xl mx-auto px-4 mt-8">
        <div className="flex items-center justify-between mb-6">
          <h2
            className="text-base sm:text-lg md:text-xl font-semibold"
            style={{ color: colors.textDark }}
          >
            자주 보는 복지 정보
          </h2>
          <button
            onClick={() => onNavigate?.('welfare')}
            className="text-xs sm:text-sm md:text-base font-medium hover:opacity-70 transition-opacity"
            style={{ color: colors.mainGreen2 }}
          >
            전체보기 →
          </button>
        </div>

        {isLoadingPopular ? (
          <div className="text-center py-8">
            <p className="text-sm" style={{ color: colors.textSub }}>
              로딩 중...
            </p>
          </div>
        ) : popularWelfares.length === 0 ? (
          <div className="text-center py-8">
            <p className="text-sm" style={{ color: colors.textSub }}>
              인기 복지 정보가 없습니다.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-5 md:gap-6">
            {popularWelfares.slice(0, 3).map((welfare) => (
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
      </section>
    </div>
  );
}
