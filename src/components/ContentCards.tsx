import React from 'react';
import { Star, Map, Gift, TrendingUp } from 'lucide-react';

const cards = [
  {
    icon: Star,
    title: '자주 이용하는 서비스',
    description: '자주 사용하는 서비스를 빠르게 찾아보세요',
    color: '#99dbc4',
  },
  {
    icon: Map,
    title: '복지지도',
    description: '내 주변 복지 시설을 확인해보세요',
    color: '#78d39e',
  },
  {
    icon: Gift,
    title: '혜택 안내',
    description: '받을 수 있는 혜택을 확인하세요',
    color: '#fac1c1',
  },
  {
    icon: TrendingUp,
    title: '복지 통계',
    description: '복지 서비스 이용 현황을 확인하세요',
    color: '#f8d9a4',
  },
];

export function ContentCards() {
  return (
    <div className="my-12 grid grid-cols-1 md:grid-cols-2 gap-6">
      {cards.map((card, index) => {
        const Icon = card.icon;
        return (
          <div
            key={index}
            className="bg-white rounded-3xl p-8 shadow-md hover:shadow-lg transition-shadow cursor-pointer"
            style={{ border: '1px solid #E8E8E8' }}
          >
            <div className="flex items-start space-x-4">
              <div
                className="w-16 h-16 rounded-2xl flex items-center justify-center flex-shrink-0"
                style={{ backgroundColor: card.color }}
              >
                <Icon size={28} color="#FFFFFF" />
              </div>
              <div className="flex-1">
                <h3 className="text-lg mb-2" style={{ color: '#333333' }}>
                  {card.title}
                </h3>
                <p className="text-sm" style={{ color: '#666666' }}>
                  {card.description}
                </p>
              </div>
            </div>
            
            {/* Placeholder content area */}
            <div className="mt-6 h-32 rounded-2xl" style={{ backgroundColor: '#E8E8E8' }}>
              <div className="w-full h-full flex items-center justify-center text-sm" style={{ color: '#666666' }}>
                콘텐츠 영역
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
