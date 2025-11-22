import React from 'react';
import { User } from 'lucide-react';

export function Header() {
  const navItems = ['복지서비스', '서비스 신청', '복지지도', '복지위기알림', '복지신고'];

  return (
    <header className="bg-white shadow-sm sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div className="flex-shrink-0">
            <div className="w-20 h-10 rounded-lg flex items-center justify-center" style={{ backgroundColor: '#99dbc4' }}>
              <span className="text-white">Logo</span>
            </div>
          </div>

          {/* Navigation */}
          <nav className="hidden md:flex items-center space-x-8">
            {navItems.map((item, index) => (
              <a
                key={index}
                href="#"
                className="text-sm hover:opacity-70 transition-opacity"
                style={{ color: '#333333' }}
              >
                {item}
              </a>
            ))}
          </nav>

          {/* Login/My Page */}
          <div className="flex items-center space-x-4">
            <button className="flex items-center space-x-2 px-4 py-2 rounded-full hover:opacity-80 transition-opacity" style={{ backgroundColor: '#E8E8E8' }}>
              <User size={16} style={{ color: '#666666' }} />
              <span className="text-sm" style={{ color: '#666666' }}>로그인</span>
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}
