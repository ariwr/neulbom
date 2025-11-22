import React, { useState } from 'react';
import { ChevronDown, ChevronUp } from 'lucide-react';

export function AnnouncementBar() {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div className="my-8">
      <div 
        className="rounded-2xl p-4 shadow-sm"
        style={{ backgroundColor: '#E8E8E8' }}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <span 
              className="px-3 py-1 rounded-full text-sm"
              style={{ backgroundColor: '#FFFFFF', color: '#666666' }}
            >
              공지사항
            </span>
            <p className="text-sm" style={{ color: '#333333' }}>
              [정상서 발발] 2025년 복지로 연도도 조사 당첨자 안내
            </p>
          </div>
          <button 
            onClick={() => setIsExpanded(!isExpanded)}
            className="p-2 rounded-full hover:opacity-70 transition-opacity"
            style={{ backgroundColor: '#FFFFFF' }}
          >
            {isExpanded ? (
              <ChevronUp size={20} style={{ color: '#666666' }} />
            ) : (
              <ChevronDown size={20} style={{ color: '#666666' }} />
            )}
          </button>
        </div>
        
        {isExpanded && (
          <div className="mt-4 pt-4 border-t" style={{ borderColor: '#FFFFFF' }}>
            <p className="text-sm" style={{ color: '#666666' }}>
              공지사항 상세 내용이 여기에 표시됩니다. 이것은 확장된 영역입니다.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
