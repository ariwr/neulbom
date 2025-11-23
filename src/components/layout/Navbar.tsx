import React from 'react';
import { MessageCircle, Users, User, LogIn, LogOut } from 'lucide-react';
import { colors } from '../../styles/design-tokens';
import type { Page } from '../../types/page';

interface NavbarProps {
  activePage: Page;
  onNavigate: (page: Page) => void;
  isLoggedIn?: boolean;
  onLoginClick?: () => void;
  onLogoutClick?: () => void;
  onCommunityClick?: (page: Page) => void; // 커뮤니티 클릭 핸들러 추가
}

// NavItem type 정의
type NavItem = {
  id: Page;
  label: string;
  icon: React.ComponentType<{ size?: number}>;
}

// 홈/마이페이지 제외한 메뉴만 정의
const navItems: NavItem[] = [
  { id: 'chat', label: '챗봇', icon: MessageCircle },
  { id: 'community', label: '커뮤니티', icon: Users },
];

export function Navbar({ 
  activePage = 'home', 
  onNavigate,
  isLoggedIn = false,
  onLoginClick,
  onLogoutClick,
  onCommunityClick,
}: NavbarProps) {
  // 커뮤니티 클릭 핸들러
  const handleCommunityClick = (page: Page) => {
    if (onCommunityClick) {
      onCommunityClick(page);
    } else {
      onNavigate(page);
    }
  };
  return (
    <nav className="bg-white shadow-sm sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">

          {/* Logo → 항상 home 이동 */}
          <div className="flex-shrink-0">
            <button
              onClick={() => onNavigate('home')}
              className="px-6 py-2 rounded-full flex items-center space-x-1 hover:opacity-80 transition-all"
              style={{ backgroundColor: colors.mainGreen1 }}
            >
              <span className="text-white">🍀</span>
              <span className="text-white">늘봄</span>
            </button>
          </div>

          {/* 중간 네비게이션 (PC) */}
          <div className="hidden md:flex items-center space-x-2">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activePage === item.id;

              return (
                <button
                  key={item.id}
                  onClick={() => item.id === 'community' ? handleCommunityClick(item.id) : onNavigate(item.id)}
                  className="flex items-center space-x-2 px-4 py-2 rounded-full transition-all"
                  style={{
                    backgroundColor: isActive ? colors.mainGreen1 : 'transparent',
                    color: isActive ? colors.white : colors.textDark,
                  }}
                >
                  <Icon size={18} />
                  <span className="text-sm">{item.label}</span>
                </button>
              );
            })}
          </div>

          {/* 우측 상단: 로그인/로그아웃 버튼 및 프로필 */}
          <div className="flex items-center space-x-4">
            {isLoggedIn ? (
              <>
                {/* 로그아웃 버튼 */}
                <button
                  onClick={onLogoutClick}
                  className="px-4 py-2 rounded-full text-sm font-medium hover:opacity-80 transition-all flex items-center space-x-2"
                  style={{ 
                    backgroundColor: colors.lightGray,
                    color: colors.textDark,
                  }}
                >
                  <LogOut size={16} />
                  <span>로그아웃</span>
                </button>
                {/* 프로필 아이콘 */}
                <button
                  onClick={() => onNavigate('mypage')}
                  className="w-10 h-10 rounded-full flex items-center justify-center hover:opacity-80 transition-all"
                  style={{ backgroundColor: colors.lightGray }}
                >
                  <User size={20} style={{ color: colors.textSub }} />
                </button>
              </>
            ) : (
              /* 로그인 버튼 */
              <button
                onClick={onLoginClick}
                className="px-4 py-2 rounded-full text-sm font-medium hover:opacity-80 transition-all flex items-center space-x-2"
                style={{ 
                  backgroundColor: colors.mainGreen2,
                  color: colors.white,
                }}
              >
                <LogIn size={16} />
                <span>로그인</span>
              </button>
            )}
          </div>
        </div>
      </div>

      {/* 모바일 하단 네비게이션: 챗봇/복지/커뮤니티만 */}
      <div
        className="md:hidden fixed bottom-0 left-0 right-0 bg-white border-t z-50"
        style={{ borderColor: colors.lightGray }}
      >
        <div className="flex items-center justify-around py-2">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activePage === item.id;

            return (
              <button
                key={item.id}
                onClick={() => item.id === 'community' ? handleCommunityClick(item.id) : onNavigate(item.id)}
                className="flex flex-col items-center py-2 px-3 rounded-lg transition-all"
                style={{
                  color: isActive ? colors.mainGreen2 : colors.textSub,
                }}
              >
                <Icon size={20} />
                <span className="text-xs mt-1">{item.label}</span>
              </button>
            );
          })}
        </div>
      </div>
    </nav>
  );
}
