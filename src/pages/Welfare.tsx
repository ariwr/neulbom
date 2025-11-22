import React, { useState } from 'react';
import { Search, Filter, Grid, List } from 'lucide-react';
import { Input } from '../components/ui/ThemedInput';
import { Button } from '../components/ui/ThemedButton';
import { Card } from '../components/ui/ThemedCard';
import { Badge } from '../components/ui/Badge';
import { WelfareCard } from '../components/WelfareCard';
import { colors } from '../styles/design-tokens';

interface WelfareProps {
  onNavigate?: (page: string) => void;
}

export function Welfare({ onNavigate }: WelfareProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [selectedFilters, setSelectedFilters] = useState<string[]>([]);

  const filters = {
    age: ['영유아', '아동', '청소년', '청년', '중장년', '노인'],
    category: ['돌봄', '의료', '주거', '교육', '일자리', '생활지원'],
    region: ['서울', '경기', '인천', '부산', '대구'],
  };

  const welfareList = [
    {
      title: '노인 장기요양보험',
      summary: '거동이 불편한 노인 등에게 신체활동 또는 가사활동 지원 등의 장기요양급여를 제공',
      eligibility: ['65세 이상', '노인성 질병'],
    },
    {
      title: '장애인 활동지원 서비스',
      summary: '신체적·정신적 장애로 혼자 일상생활이 어려운 분들을 위한 활동 지원',
      eligibility: ['장애인', '만 6세~65세'],
    },
    {
      title: '가족돌봄 휴가제도',
      summary: '가족 구성원의 질병, 사고, 노령으로 인한 돌봄이 필요한 경우 사용',
      eligibility: ['근로자', '돌봄 필요 가족'],
    },
    {
      title: '아이돌봄 서비스',
      summary: '만 12세 이하 아동을 둔 가정에 아이돌보미가 방문하여 돌봄 서비스 제공',
      eligibility: ['만 12세 이하', '맞벌이 가정'],
    },
    {
      title: '노인 맞춤돌봄 서비스',
      summary: '일상생활 영위가 어려운 취약 노인에게 적절한 돌봄서비스 제공',
      eligibility: ['65세 이상', '독거노인'],
    },
    {
      title: '발달장애인 주간활동서비스',
      summary: '성인 발달장애인에게 낮 시간 동안 지역사회 기반 활동 지원',
      eligibility: ['만 18세~65세', '발달장애인'],
    },
  ];

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
              총 {welfareList.length}개
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
          {welfareList.map((welfare, index) => (
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
