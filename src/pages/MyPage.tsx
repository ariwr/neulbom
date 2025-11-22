import React from 'react';
import { User, Settings, Bookmark, MessageCircle, LogOut } from 'lucide-react';
import { Card } from '../components/ui/ThemedCard';
import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/ThemedButton';
import { colors } from '../styles/design-tokens';
import type { Welfare } from '../services/welfareService';

interface MyPageProps {
  onNavigate?: (page: string) => void;
  bookmarkedWelfares: Welfare[];
}

export function MyPage({ onNavigate, bookmarkedWelfares }: MyPageProps) {
  const userLevel = 2;
  const levelProgress = 65; // percentage

  const chatHistory = [
    { title: '복지 서비스 문의', date: '2025.11.20' },
    { title: '돌봄 스트레스 상담', date: '2025.11.19' },
  ];

  return (
    <div className="min-h-screen pb-20" style={{ backgroundColor: colors.lightGray }}>
      {/* Header */}
      <section 
        className="py-12 px-4"
        style={{
          background: `linear-gradient(135deg, ${colors.mainGreen1} 0%, ${colors.mainGreen2} 100%)`,
        }}
      >
        <div className="max-w-4xl mx-auto text-center">
          <div 
            className="w-20 h-20 rounded-full mx-auto mb-4 flex items-center justify-center"
            style={{ backgroundColor: colors.white }}
          >
            <User size={32} style={{ color: colors.mainGreen2 }} />
          </div>
          <h1 className="text-xl text-white mb-2">
            김늘봄 님
          </h1>
          <p className="text-sm text-white opacity-90">
            kim.neulbom@example.com
          </p>
        </div>
      </section>

      {/* Content */}
      <div className="max-w-4xl mx-auto px-4 -mt-8">
        {/* User Level Card */}
        <Card variant="elevated" padding="lg" className="mb-6">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-lg" style={{ color: colors.textDark }}>
                사용자 등급
              </h2>
              <Badge variant="level2" size="lg">Level {userLevel}</Badge>
            </div>

            {/* Progress Bar */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm" style={{ color: colors.textSub }}>
                  Level 3까지
                </span>
                <span className="text-sm" style={{ color: colors.mainGreen2 }}>
                  {levelProgress}%
                </span>
              </div>
              <div 
                className="h-2 rounded-full overflow-hidden"
                style={{ backgroundColor: colors.lightGray }}
              >
                <div
                  className="h-full rounded-full transition-all"
                  style={{
                    width: `${levelProgress}%`,
                    backgroundColor: colors.mainGreen2,
                  }}
                />
              </div>
            </div>

            <div 
              className="p-4 rounded-xl"
              style={{ backgroundColor: colors.lightGray }}
            >
              <p className="text-sm mb-2" style={{ color: colors.textDark }}>
                현재 권한
              </p>
              <ul className="space-y-1">
                <li className="text-xs" style={{ color: colors.textSub }}>
                  ✓ 챗봇 이용
                </li>
                <li className="text-xs" style={{ color: colors.textSub }}>
                  ✓ 복지 정보 검색
                </li>
                <li className="text-xs" style={{ color: colors.textSub }}>
                  ✓ 커뮤니티 읽기
                </li>
              </ul>
            </div>

            <Button variant="outline" size="sm" fullWidth>
              Level 3 인증 신청하기
            </Button>
          </div>
        </Card>

        {/* Profile Info */}
        <Card variant="elevated" padding="lg" className="mb-6">
          <div className="space-y-4">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg" style={{ color: colors.textDark }}>
                프로필 정보
              </h2>
              <button className="text-sm hover:opacity-70 transition-opacity" style={{ color: colors.mainGreen2 }}>
                수정
              </button>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-xs mb-1" style={{ color: colors.textSub }}>
                  이름
                </p>
                <p className="text-sm" style={{ color: colors.textDark }}>
                  김늘봄
                </p>
              </div>
              <div>
                <p className="text-xs mb-1" style={{ color: colors.textSub }}>
                  나이
                </p>
                <p className="text-sm" style={{ color: colors.textDark }}>
                  35세
                </p>
              </div>
              <div>
                <p className="text-xs mb-1" style={{ color: colors.textSub }}>
                  거주 지역
                </p>
                <p className="text-sm" style={{ color: colors.textDark }}>
                  서울특별시 강남구
                </p>
              </div>
              <div>
                <p className="text-xs mb-1" style={{ color: colors.textSub }}>
                  돌봄 대상
                </p>
                <p className="text-sm" style={{ color: colors.textDark }}>
                  부모님
                </p>
              </div>
            </div>
          </div>
        </Card>

        {/* Bookmarked Welfare */}
        <Card variant="elevated" padding="lg" className="mb-6">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Bookmark size={18} style={{ color: colors.mainGreen2 }} />
                <h2 className="text-lg" style={{ color: colors.textDark }}>
                  북마크한 복지 정보
                </h2>
              </div>
              <button 
                onClick={() => onNavigate?.('welfare')}
                className="text-sm hover:opacity-70 transition-opacity" 
                style={{ color: colors.mainGreen2 }}
              >
                전체보기
              </button>
            </div>

            {bookmarkedWelfares.length === 0 ? (
              <p className="text-xs" style={{ color: colors.textSub}} >
                아직 북마크한 복지 정보가 없습니다.
              </p>
            ) : (
            <div className="space-y-2">
              {bookmarkedWelfares.map((item, index) => (
                <div 
                  key={index}
                  className="p-3 rounded-lg flex items-center justify-between cursor-pointer hover:opacity-80 transition-opacity"
                  style={{ backgroundColor: colors.lightGray }}
                  onClick={() => onNavigate?.('welfare-detail')}
                >
                  <span className="text-sm" style={{ color: colors.textDark }}>
                    {item.title}
                  </span>
                  <span className="text-xs" style={{ color: colors.textSub }}>
                    {item.date}
                  </span>
                </div>
              ))}
            </div>
            )}
          </div>
        </Card>

        {/* Chat History */}
        <Card variant="elevated" padding="lg" className="mb-6">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <MessageCircle size={18} style={{ color: colors.mainGreen2 }} />
                <h2 className="text-lg" style={{ color: colors.textDark }}>
                  대화 기록
                </h2>
              </div>
              <button 
                onClick={() => onNavigate?.('chat')}
                className="text-sm hover:opacity-70 transition-opacity" 
                style={{ color: colors.mainGreen2 }}
              >
                전체보기
              </button>
            </div>

            <div className="space-y-2">
              {chatHistory.map((item, index) => (
                <div 
                  key={index}
                  className="p-3 rounded-lg flex items-center justify-between cursor-pointer hover:opacity-80 transition-opacity"
                  style={{ backgroundColor: colors.lightGray }}
                  onClick={() => onNavigate?.('chat')}
                >
                  <span className="text-sm" style={{ color: colors.textDark }}>
                    {item.title}
                  </span>
                  <span className="text-xs" style={{ color: colors.textSub }}>
                    {item.date}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </Card>

        {/* Settings & Logout */}
        <Card variant="elevated" padding="lg">
          <div className="space-y-3">
            <button className="w-full flex items-center justify-between p-3 rounded-lg hover:bg-opacity-50 transition-all" style={{ backgroundColor: colors.lightGray }}>
              <div className="flex items-center space-x-3">
                <Settings size={18} style={{ color: colors.textSub }} />
                <span className="text-sm" style={{ color: colors.textDark }}>
                  설정
                </span>
              </div>
            </button>
            
            <button className="w-full flex items-center justify-between p-3 rounded-lg hover:bg-opacity-50 transition-all" style={{ backgroundColor: colors.lightGray }}>
              <div className="flex items-center space-x-3">
                <LogOut size={18} style={{ color: colors.error }} />
                <span className="text-sm" style={{ color: colors.error }}>
                  로그아웃
                </span>
              </div>
            </button>
          </div>
        </Card>
      </div>
    </div>
  );
}
