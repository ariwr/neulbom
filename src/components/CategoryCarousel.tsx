import React, { useRef } from 'react';
import { ChevronLeft, ChevronRight, FileText, Bell, Map, MapPin, AlertCircle, Users } from 'lucide-react';

const categories = [
  { icon: FileText, label: '복지서비스', color: '#fac1c1' },
  { icon: Bell, label: '서비스신청', color: '#f8d9a4' },
  { icon: MapPin, label: '복지위기알림', color: '#99dbc4' },
  { icon: Map, label: '복지지도', color: '#78d39e' },
  { icon: AlertCircle, label: '복지신고', color: '#fac1c1' },
  { icon: Users, label: '맞춤형급여안내', color: '#f8d9a4' },
];

export function CategoryCarousel() {
  const scrollRef = useRef<HTMLDivElement>(null);

  const scroll = (direction: 'left' | 'right') => {
    if (scrollRef.current) {
      const scrollAmount = 300;
      scrollRef.current.scrollBy({
        left: direction === 'left' ? -scrollAmount : scrollAmount,
        behavior: 'smooth'
      });
    }
  };

  return (
    <div className="my-12 relative">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl" style={{ color: '#333333' }}>자주 찾는 서비스</h2>
        <div className="flex space-x-2">
          <button
            onClick={() => scroll('left')}
            className="w-10 h-10 rounded-full flex items-center justify-center shadow-sm hover:opacity-80 transition-opacity"
            style={{ backgroundColor: '#E8E8E8' }}
          >
            <ChevronLeft size={20} style={{ color: '#666666' }} />
          </button>
          <button
            onClick={() => scroll('right')}
            className="w-10 h-10 rounded-full flex items-center justify-center shadow-sm hover:opacity-80 transition-opacity"
            style={{ backgroundColor: '#E8E8E8' }}
          >
            <ChevronRight size={20} style={{ color: '#666666' }} />
          </button>
        </div>
      </div>

      <div 
        ref={scrollRef}
        className="flex space-x-6 overflow-x-auto scrollbar-hide pb-4"
        style={{ scrollbarWidth: 'none', msOverflowStyle: 'none' }}
      >
        {categories.map((category, index) => {
          const Icon = category.icon;
          return (
            <div
              key={index}
              className="flex-shrink-0 flex flex-col items-center cursor-pointer hover:opacity-80 transition-opacity"
            >
              <div
                className="w-20 h-20 rounded-full flex items-center justify-center shadow-md mb-3"
                style={{ backgroundColor: category.color }}
              >
                <Icon size={32} color="#FFFFFF" />
              </div>
              <span className="text-sm text-center whitespace-nowrap" style={{ color: '#666666' }}>
                {category.label}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
