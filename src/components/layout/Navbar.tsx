import React from 'react';
import { Home, MessageCircle, Gift, Users, User } from 'lucide-react';
import { colors } from '../../styles/design-tokens';

interface NavbarProps {
  activePage?: string;
  onNavigate?: (page: string) => void;
}

const navItems = [
  { id: 'home', label: '홈', icon: Home },
  { id: 'chat', label: '챗봇', icon: MessageCircle },
  { id: 'welfare', label: '복지 검색', icon: Gift },
  { id: 'community', label: '커뮤니티', icon: Users },
  { id: 'mypage', label: '마이페이지', icon: User },
];

export function Navbar({ activePage = 'home', onNavigate }: NavbarProps) {
  return (
    <nav className="bg-white shadow-sm sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div className="flex-shrink-0">
            <div 
              className="px-6 py-2 rounded-full flex items-center space-x-2"
              style={{ backgroundColor: colors.mainGreen1 }}
            >
              <span className="text-white">🌿</span>
              <span className="text-white">늘봄</span>
            </div>
          </div>

          {/* Navigation Items */}
          <div className="hidden md:flex items-center space-x-2">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activePage === item.id;
              
              return (
                <button
                  key={item.id}
                  onClick={() => onNavigate?.(item.id)}
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

          {/* User Profile */}
          <div className="flex items-center space-x-4">
            <button 
              className="w-10 h-10 rounded-full flex items-center justify-center"
              style={{ backgroundColor: colors.lightGray }}
            >
              <User size={20} style={{ color: colors.textSub }} />
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Navigation */}
      <div className="md:hidden fixed bottom-0 left-0 right-0 bg-white border-t z-50" style={{ borderColor: colors.lightGray }}>
        <div className="flex items-center justify-around py-2">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activePage === item.id;
            
            return (
              <button
                key={item.id}
                onClick={() => onNavigate?.(item.id)}
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
