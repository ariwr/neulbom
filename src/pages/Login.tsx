import React, { useState } from 'react';
import { Input } from '../components/ui/ThemedInput';
import { Button } from '../components/ui/ThemedButton';
import { Card } from '../components/ui/ThemedCard';
import { colors } from '../styles/design-tokens';
import type { Page } from '../types/page';

interface LoginProps {
  onNavigate?: (page: Page) => void;
}

export function Login({ onNavigate }: LoginProps) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  return (
    <div 
      className="min-h-screen flex items-center justify-center p-4"
      style={{
        background: `linear-gradient(135deg, ${colors.mainGreen1} 0%, ${colors.mainGreen2} 100%)`,
      }}
    >
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center space-x-2 mb-4">
            <span className="text-4xl">🌿</span>
            <h1 className="text-3xl text-white">늘봄</h1>
          </div>
          <p className="text-sm text-white opacity-90">
            돌봄가족을 위한 AI 복지 도우미
          </p>
        </div>

        {/* Login Card */}
        <Card variant="elevated" padding="lg">
          <div className="space-y-6">
            <div className="space-y-4">
              <Input
                type="email"
                label="이메일"
                placeholder="이메일을 입력하세요"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                fullWidth
              />
              <Input
                type="password"
                label="비밀번호"
                placeholder="비밀번호를 입력하세요"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                fullWidth
              />
            </div>

            <Button 
              variant="primary" 
              size="lg" 
              fullWidth
              onClick={() => onNavigate?.('home')}
            >
              로그인
            </Button>

            <div className="flex items-center justify-between text-sm">
              <button 
                className="hover:opacity-70 transition-opacity"
                style={{ color: colors.textSub }}
              >
                비밀번호 찾기
              </button>
              <button 
                onClick={() => onNavigate?.('signup')}
                className="hover:opacity-70 transition-opacity"
                style={{ color: colors.mainGreen2 }}
              >
                회원가입
              </button>
            </div>
          </div>
        </Card>

        {/* Info */}
        <p className="text-center text-xs mt-6 text-white opacity-75">
          늘봄은 돌봄가족을 위한 정서지원과 복지정보를 제공합니다
        </p>
      </div>
    </div>
  );
}
