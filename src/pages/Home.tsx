import React from 'react';
import { MessageCircle, Gift, Users, FileText, ArrowRight } from 'lucide-react';
import { Card } from '../components/ui/ThemedCard';
import { Button } from '../components/ui/ThemedButton';
import { WelfareCard } from '../components/WelfareCard';
import { colors } from '../styles/design-tokens';
import type { Welfare } from '../services/welfareService';
import { FormItem } from '../components/ui/form';

interface HomeProps {
  onNavigate?: (page: string) => void;
  welfares: Welfare[];
  bookmarkedIds: number[];
  onToggleBookmark: (id: number) => void;
}

export function Home({ onNavigate, welfares, bookmarkedIds, onToggleBookmark }: HomeProps) {
  const quickAccess = [
    { icon: MessageCircle, label: 'AI 챗봇', color: colors.mainGreen1, page: 'chat' },
    { icon: Gift, label: '복지 검색', color: colors.mainGreen2, page: 'welfare' },
    { icon: Users, label: '커뮤니티', color: colors.pointPink, page: 'community' },
    { icon: FileText, label: '신청 내역', color: colors.pointYellow, page: 'mypage' },
  ];

  return (
    <div className="pb-20">
      {/* Hero Section */}
      <section 
        className="py-16 px-4"
        style={{
          background: `linear-gradient(135deg, #a2e2eb 0%, #82d8e0 100%)`,
        }}
      >
        <div className="max-w-4xl mx-auto text-center">
          <h1 className="text-3xl text-white mb-4">
            안녕하세요, 늘봄입니다 🌿
          </h1>
          <p className="text-white opacity-90 mb-8">
            오늘은 무엇을 도와드릴까요?
          </p>
          
          {/* Quick Chat Access */}
          <Card variant="elevated" padding="md">
            <div className="flex items-center space-x-4">
              <div 
                className="w-12 h-12 rounded-full flex items-center justify-center flex-shrink-0"
                style={{ backgroundColor: colors.mainGreen1 }}
              >
                <MessageCircle size={24} color={colors.white} />
              </div>
              <div className="flex-1 text-left">
                <p className="text-sm" style={{ color: colors.textDark }}>
                  AI 챗봇과 대화하기
                </p>
                <p className="text-xs mt-1" style={{ color: colors.textSub }}>
                  고민을 나누고 복지 정보를 받아보세요
                </p>
              </div>
              <Button 
                variant="primary" 
                size="sm"
                onClick={() => onNavigate?.('chat')}
                icon={<ArrowRight size={16} />}
              >
                시작하기
              </Button>
            </div>
          </Card>
        </div>
      </section>

      {/* Quick Access Cards */}
      <section className="max-w-7xl mx-auto px-4 -mt-8">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {quickAccess.map((item, index) => {
            const Icon = item.icon;
            return (
              <Card 
                key={index} 
                variant="elevated" 
                padding="md"
                onClick={() => onNavigate?.(item.page)}
              >
                <div className="flex flex-col items-center text-center space-y-3">
                  <div
                    className="w-16 h-16 rounded-full flex items-center justify-center"
                    style={{ backgroundColor: item.color }}
                  >
                    <Icon size={28} color={colors.white} />
                  </div>
                  <span className="text-sm" style={{ color: colors.textDark }}>
                    {item.label}
                  </span>
                </div>
              </Card>
            );
          })}
        </div>
      </section>

      {/* Recently Viewed Welfare */}
      <section className="max-w-7xl mx-auto px-4 mt-12">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl" style={{ color: colors.textDark }}>
            최근 본 복지 정보
          </h2>
          <button 
            onClick={() => onNavigate?.('welfare')}
            className="text-sm hover:opacity-70 transition-opacity"
            style={{ color: colors.mainGreen2 }}
          >
            전체보기 →
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {welfares.slice(0, 4).map((welfare) => (
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

      {/* Community Highlight */}
      <section className="max-w-7xl mx-auto px-4 mt-12">
        <Card 
          variant="outlined" 
          padding="lg"
          style={{ background: `linear-gradient(135deg, ${colors.pointPink}20 0%, ${colors.pointYellow}20 100%)` }}
        >
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg mb-2" style={{ color: colors.textDark }}>
                커뮤니티에서 경험을 공유하세요
              </h3>
              <p className="text-sm" style={{ color: colors.textSub }}>
                같은 고민을 가진 분들과 소통하고 정보를 나눠보세요
              </p>
            </div>
            <Button 
              variant="primary"
              onClick={() => onNavigate?.('community')}
            >
              커뮤니티 가기
            </Button>
          </div>
        </Card>
      </section>
    </div>
  );
}