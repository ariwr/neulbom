import React from 'react';

export function Footer() {
  const footerLinks = [
    '서비스 소개',
    '이용약관',
    '개인정보처리방침',
    '고객센터',
    '사이트맵',
  ];

  return (
    <footer className="mt-24 py-12" style={{ backgroundColor: '#E8E8E8' }}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* First row - Links */}
        <div className="flex flex-wrap items-center justify-center space-x-6 mb-6">
          {footerLinks.map((link, index) => (
            <a
              key={index}
              href="#"
              className="text-sm hover:opacity-70 transition-opacity"
              style={{ color: '#666666' }}
            >
              {link}
            </a>
          ))}
        </div>

        {/* Second row - Info */}
        <div className="text-center space-y-2">
          <p className="text-sm" style={{ color: '#666666' }}>
            주소: 서울특별시 종로구 세종대로 209 정부서울청사
          </p>
          <p className="text-sm" style={{ color: '#666666' }}>
            전화: 129 | 이메일: info@example.go.kr
          </p>
          <p className="text-xs mt-4" style={{ color: '#666666' }}>
            © 2025 Government Service Portal. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
}
