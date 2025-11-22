import React, { useState } from 'react';
import { Input } from '../components/ui/ThemedInput';
import { Button } from '../components/ui/ThemedButton';
import { Card } from '../components/ui/ThemedCard';
import { Badge } from '../components/ui/Badge';
import { colors } from '../styles/design-tokens';
import { ChevronLeft } from 'lucide-react';

interface SignupProps {
  onNavigate: (page: string) => void;
}

export function Signup({ onNavigate }: SignupProps) {
  const [formData, setFormData] = useState({
    name: '',
    age: '',
    region: '',
    careTarget: '',
    email: '',
    password: '',
    confirmPassword: '',
  });

  return (
    <div 
      className="min-h-screen p-4"
      style={{ backgroundColor: colors.lightGray }}
    >
      <div className="max-w-2xl mx-auto py-8">
        {/* Back Button */}
        <button 
          onClick={() => onNavigate?.('login')}
          className="flex items-center space-x-2 mb-6 hover:opacity-70 transition-opacity"
          style={{ color: colors.textDark }}
        >
          <ChevronLeft size={20} />
          <span>돌아가기</span>
        </button>

        {/* Header */}
        <div className="mb-8">
          <h1 className="text-2xl mb-2" style={{ color: colors.textDark }}>
            회원가입
          </h1>
          <p className="text-sm" style={{ color: colors.textSub }}>
            늘봄 서비스 이용을 위한 정보를 입력해주세요
          </p>
        </div>

        {/* User Level Info */}
        <Card variant="elevated" padding="md" className="mb-6">
          <h3 className="text-base mb-4" style={{ color: colors.textDark }}>
            사용자 등급 안내
          </h3>
          <div className="space-y-3">
            <div className="flex items-start space-x-3">
              <Badge variant="level1" size="sm">Level 1</Badge>
              <div className="flex-1">
                <p className="text-sm" style={{ color: colors.textDark }}>
                  기본 회원
                </p>
                <p className="text-xs mt-1" style={{ color: colors.textSub }}>
                  챗봇, 복지 검색 이용 가능
                </p>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <Badge variant="level2" size="sm">Level 2</Badge>
              <div className="flex-1">
                <p className="text-sm" style={{ color: colors.textDark }}>
                  인증 회원
                </p>
                <p className="text-xs mt-1" style={{ color: colors.textSub }}>
                  커뮤니티 읽기 권한 추가
                </p>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <Badge variant="level3" size="sm">Level 3</Badge>
              <div className="flex-1">
                <p className="text-sm" style={{ color: colors.textDark }}>
                  완전 인증 회원
                </p>
                <p className="text-xs mt-1" style={{ color: colors.textSub }}>
                  커뮤니티 글쓰기 권한 포함
                </p>
              </div>
            </div>
          </div>
        </Card>

        {/* Signup Form */}
        <Card variant="elevated" padding="lg">
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <Input
                label="이름"
                placeholder="이름"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              />
              <Input
                type="number"
                label="나이"
                placeholder="나이"
                value={formData.age}
                onChange={(e) => setFormData({ ...formData, age: e.target.value })}
              />
            </div>

            <Input
              label="거주 지역"
              placeholder="예: 서울특별시 강남구"
              value={formData.region}
              onChange={(e) => setFormData({ ...formData, region: e.target.value })}
              fullWidth
            />

            <Input
              label="돌봄 대상"
              placeholder="예: 부모님, 자녀 등"
              value={formData.careTarget}
              onChange={(e) => setFormData({ ...formData, careTarget: e.target.value })}
              fullWidth
            />

            <div className="border-t pt-4" style={{ borderColor: colors.lightGray }}>
              <Input
                type="email"
                label="이메일"
                placeholder="이메일@example.com"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                fullWidth
              />
            </div>

            <Input
              type="password"
              label="비밀번호"
              placeholder="비밀번호 (8자 이상)"
              value={formData.password}
              onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              fullWidth
            />

            <Input
              type="password"
              label="비밀번호 확인"
              placeholder="비밀번호 재입력"
              value={formData.confirmPassword}
              onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
              fullWidth
            />

            <div className="pt-4">
              <Button
                variant="primary"
                size="lg"
                fullWidth
                onClick={() => {
                  // 나중에 여기서 실제 회원가입 API 호출(onSignup(formData)) 들어갈 자리
                  onNavigate('login');      // 회원가입 후 로그인 페이지로 이동
                }}
                >
                가입하기
              </Button>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
