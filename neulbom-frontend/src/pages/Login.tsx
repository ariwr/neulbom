import React, { useState } from 'react';
import { Input } from '../components/ui/ThemedInput';
import { Button } from '../components/ui/ThemedButton';
import { Card } from '../components/ui/ThemedCard';
import { colors } from '../styles/design-tokens';
import type { Page } from '../types/page';
import { login } from '../services/authService';

interface LoginProps {
  onNavigate?: (page: Page) => void;
  onLoginSuccess?: (token?: string) => void;
}

export function Login({ onNavigate, onLoginSuccess }: LoginProps) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

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
          <div className="inline-flex items-center mb-2">
            <span className="text-4xl">🍀</span>
            <h1 className="text-3xl text-white font-bold">늘봄</h1>
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

            {/* 에러 메시지 */}
            {error && (
              <div className="p-3 rounded-md text-sm" style={{ backgroundColor: colors.error + '10', color: colors.error }}>
                {error}
              </div>
            )}

            <Button 
              variant="primary" 
              size="lg" 
              fullWidth
              disabled={isLoading}
              onClick={async () => {
                if (!email.trim() || !password.trim()) {
                  setError('이메일과 비밀번호를 입력해주세요.');
                  return;
                }

                setIsLoading(true);
                setError(null);

                try {
                  const response = await login({ email: email.trim(), password });
                  
                  if (!response.access_token) {
                    throw new Error('로그인 응답에 토큰이 없습니다.');
                  }
                  
                  // 로그인 성공 후 콜백 호출 (토큰 전달)
                  // 상태 업데이트가 완료되도록 먼저 호출
                  if (onLoginSuccess) {
                    onLoginSuccess(response.access_token);
                  }
                  
                  // 상태 업데이트가 완료되도록 충분한 지연
                  // React의 상태 업데이트가 완료되도록 기다림
                  await new Promise(resolve => setTimeout(resolve, 300));
                  
                  // 페이지 이동
                  onNavigate?.('home');
                } catch (err: any) {
                  console.error('로그인 실패:', err);
                  
                  // 에러 메시지 처리
                  let errorMessage = '로그인에 실패했습니다. 다시 시도해주세요.';
                  
                  if (err?.message) {
                    errorMessage = err.message;
                  } else if (err?.status === 0) {
                    errorMessage = '서버에 연결할 수 없습니다. 백엔드 서버가 실행 중인지 확인해주세요.';
                  } else if (err?.status === 401) {
                    errorMessage = '이메일 또는 비밀번호가 올바르지 않습니다.';
                  } else if (err?.status === 400) {
                    errorMessage = '요청이 올바르지 않습니다.';
                  }
                  
                  setError(errorMessage);
                } finally {
                  setIsLoading(false);
                }
              }}
            >
              {isLoading ? '로그인 중...' : '로그인'}
            </Button>

            <div className="flex items-center justify-between text-sm">
              <button 
                onClick={() => onNavigate?.('home')}
                className="hover:opacity-70 transition-opacity"
                style={{ color: colors.textSub }}
              >
                비회원으로 이용하기
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
