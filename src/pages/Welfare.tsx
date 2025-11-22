import React, { useState } from 'react';
import { Search, Filter, Grid, List } from 'lucide-react';
import { Input } from '../components/ui/ThemedInput';
import { Button } from '../components/ui/ThemedButton';
import { Card } from '../components/ui/ThemedCard';
import { Badge } from '../components/ui/Badge';
import { WelfareCard } from '../components/WelfareCard';
import { colors } from '../styles/design-tokens';
import type { Welfare } from '../services/welfareService';

interface WelfareProps {
  onNavigate?: (page: string) => void;
  welfares: Welfare[];          // 전체 복지 목록
  bookmarkedIds: number[];      // 북마크된 내용
  onToggleBookmark: (id: number) => void;   // 토글 핸들러
}

export function Welfare({ onNavigate, welfares, bookmarkedIds, onToggleBookmark }: WelfareProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [selectedFilters, setSelectedFilters] = useState<string[]>([]);

  const filters = {
    age: ['영유아', '아동', '청소년', '청년', '중장년', '노인'],
    category: ['돌봄', '의료', '주거', '교육', '일자리', '생활지원'],
    region: ['서울', '경기', '인천', '부산', '대구'],
  };

  return (
    <div className="min-h-screen pb-20" style={{ backgroundColor: colors.lightGray }}>
      {/* Search Header */}
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
          
          {/* Search Bar */}
          <Card variant="elevated" padding="sm">
            <div className="flex items-center space-x-3">
              <Search size={20} style={{ color: colors.textSub }} />
              <input
                type="text"
                placeholder="필요한 복지 서비스를 검색하세요"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="flex-1 outline-none text-base"
                style={{ color: colors.textDark }}
              />
              <Button variant="primary" size="sm">
                검색
              </Button>
            </div>
          </Card>

          {/* Quick Filters */}
          <div className="flex flex-wrap gap-2 mt-4 justify-center">
            {['전체', '노인돌봄', '장애인지원', '아동돌봄', '의료지원'].map((tag) => (
              <Badge key={tag} variant="default" size="md">
                {tag}
              </Badge>
            ))}
          </div>
        </div>
      </section>

      {/* Filter & View Controls */}
      <div className="max-w-7xl mx-auto px-4 py-6">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-2">
            <Button variant="outline" size="sm" icon={<Filter size={16} />}>
              필터
            </Button>
            <span className="text-sm" style={{ color: colors.textSub }}>
              총 {welfares.length}개
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

        {/* Results Grid */}
        <div className={`grid gap-6 ${viewMode === 'grid' ? 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3' : 'grid-cols-1'}`}>
          {welfares.map((welfare, index) => (
            <WelfareCard
              key={index}
              title={welfare.title}
              summary={welfare.summary}
              eligibility={welfare.eligibility}
              onClick={() => onNavigate?.('welfare-detail')}
            />
          ))}
        </div>

        {/* Load More */}
        <div className="text-center mt-8">
          <Button variant="outline" size="md">
            더 보기
          </Button>
        </div>
      </div>
    </div>
  );
}
