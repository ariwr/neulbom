import React from 'react';
import { Search } from 'lucide-react';

export function SearchSection() {
  return (
    <section 
      className="py-16 px-4"
      style={{
        background: `linear-gradient(135deg, #99dbc4 0%, #78d39e 100%)`
      }}
    >
      <div className="max-w-3xl mx-auto">
        <div className="bg-white rounded-full shadow-lg flex items-center px-6 py-4">
          <input
            type="text"
            placeholder="검색어를 입력하세요"
            className="flex-1 outline-none text-base"
            style={{ color: '#333333' }}
          />
          <button 
            className="ml-4 w-12 h-12 rounded-full flex items-center justify-center hover:opacity-90 transition-opacity"
            style={{ backgroundColor: '#78d39e' }}
          >
            <Search size={20} color="#FFFFFF" />
          </button>
        </div>
      </div>
    </section>
  );
}
