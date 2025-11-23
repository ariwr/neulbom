import React, { useState } from 'react';
import { Search } from 'lucide-react';
import { WelfareCard } from '../components/WelfareCard';
import { Card } from '../components/ui/ThemedCard';
import { colors } from '../styles/design-tokens';
import type { Welfare } from '../services/welfareService';

interface HomeProps {
  onNavigate?: (page: string) => void;
  welfares: Welfare[];
  bookmarkedIds: number[];
  onToggleBookmark: (id: number) => void;
}

export function Home({
  onNavigate,
  welfares,
  bookmarkedIds,
  onToggleBookmark,
}: HomeProps) {
  const [keyword, setKeyword] = useState('');

  const handleSearch = () => {
    const q = keyword.trim();
    if (!q) return;

    // 나중에 실제 검색 페이지/쿼리 연결
    // onNavigate?.(`welfare?query=${encodeURIComponent(q)}`);
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
          <h1 className="text-2xl text-white mb-6 text-center">
            어떤 복지 서비스를 찾고 계신가요?
          </h1>

          {/* 검색바 카드 (Community 헤더 그대로) */}
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

      {/* =================== Home.tsx 원래 콘텐츠 (최근 본 복지 정보) =================== */}
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

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-5 md:gap-6">
          {welfares.slice(0, 3).map((welfare) => (
            <WelfareCard
              key={welfare.id}
              title={welfare.title}
              summary={welfare.summary}
              eligibility={welfare.eligibility}
              isBookmarked={bookmarkedIds.includes(welfare.id)}
              onBookmark={() => onToggleBookmark(welfare.id)}
              onClick={() => onNavigate?.('welfare-detail')}
            />
          ))}
        </div>
      </section>
    </div>
  );
}
