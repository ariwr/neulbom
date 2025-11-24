import React from 'react';
import { MessageCircle } from 'lucide-react';
import type { Page } from '../types/page';

interface FloatingActionButtonsProps {
  onNavigate: (page: Page) => void;
}

export function FloatingActionButtons({ onNavigate }: FloatingActionButtonsProps) {
  const handleChatClick = () => {
    onNavigate('chat');
  };

  return (
    <div className="fixed top-20 left-1/2 transform -translate-x-1/2 z-40">
      <button
        onClick={handleChatClick}
        className="w-16 h-16 rounded-full shadow-lg hover:opacity-90 transition-all hover:scale-105 flex items-center justify-center"
        style={{ 
          backgroundColor: '#78d39e',
          boxShadow: '0 4px 12px rgba(120, 211, 158, 0.4)'
        }}
        title="챗봇 상담"
      >
        <MessageCircle size={28} color="#FFFFFF" />
      </button>
    </div>
  );
}
