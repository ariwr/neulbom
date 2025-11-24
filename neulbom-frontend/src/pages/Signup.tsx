import React, { useState } from 'react';
import { Input } from '../components/ui/ThemedInput';
import { Button } from '../components/ui/ThemedButton';
import { Card } from '../components/ui/ThemedCard';
import { Badge } from '../components/ui/Badge';
import { colors } from '../styles/design-tokens';
import { ChevronLeft, CheckCircle, AlertCircle } from 'lucide-react';
import type { Page } from '../types/page';
import { signup } from '../services/authService';

interface SignupProps {
  onNavigate: (page: Page) => void;
  onSignupSuccess?: () => void;
}

export function Signup({ onNavigate, onSignupSuccess }: SignupProps) {
  const [formData, setFormData] = useState({
    name: '',
    age: '',
    region: '',
    careTarget: '',
    email: '',
    password: '',
    confirmPassword: '',
  });
  
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

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

            {/* 에러 메시지 */}
            {error && (
              <div className="flex items-center space-x-2 p-3 rounded-md" style={{ backgroundColor: colors.error + '10', borderLeft: `4px solid ${colors.error}` }}>
                <AlertCircle size={16} style={{ color: colors.error }} />
                <span className="text-sm" style={{ color: colors.error }}>{error}</span>
              </div>
            )}

            {/* 성공 메시지 */}
            {success && (
              <div className="flex items-center space-x-2 p-3 rounded-md" style={{ backgroundColor: '#10b981' + '10', borderLeft: '4px solid #10b981' }}>
                <CheckCircle size={16} style={{ color: '#10b981' }} />
                <span className="text-sm" style={{ color: '#10b981' }}>회원가입이 완료되었습니다! 로그인 페이지로 이동합니다.</span>
              </div>
            )}

            <div className="pt-4">
              <Button
                variant="primary"
                size="lg"
                fullWidth
                disabled={isLoading || success}
                onClick={async () => {
                  // 유효성 검사
                  if (!formData.name.trim()) {
                    setError('이름을 입력해주세요.');
                    return;
                  }
                  if (!formData.email.trim()) {
                    setError('이메일을 입력해주세요.');
                    return;
                  }
                  if (!formData.password.trim()) {
                    setError('비밀번호를 입력해주세요.');
                    return;
                  }
                  if (formData.password.length < 8) {
                    setError('비밀번호는 8자 이상이어야 합니다.');
                    return;
                  }
                  if (formData.password !== formData.confirmPassword) {
                    setError('비밀번호가 일치하지 않습니다.');
                    return;
                  }

                  setIsLoading(true);
                  setError(null);
                  setSuccess(false);

                  try {
                    // 회원가입 API 호출
                    await signup({
                      name: formData.name.trim(),
                      email: formData.email.trim(),
                      password: formData.password,
                      password_confirm: formData.confirmPassword,
                      age: formData.age ? parseInt(formData.age) : undefined,
                      region: formData.region.trim() || undefined,
                      care_target: formData.careTarget.trim() || undefined,
                    });

                    // 성공 메시지 표시
                    setSuccess(true);
                    
                    // 회원가입 시 입력한 프로필 정보를 localStorage에 저장
                    const profileData = {
                      name: formData.name.trim(),
                      age: formData.age ? `${formData.age}세` : '',
                      region: formData.region.trim() || '',
                      target: formData.careTarget.trim() || '',
                    };
                    localStorage.setItem('userProfile', JSON.stringify(profileData));
                    
                    // 회원가입 성공 시 로그인 상태 업데이트
                    onSignupSuccess?.();
                    
                    // 2초 후 로그인 페이지로 이동
                    setTimeout(() => {
                      onNavigate('login');
                    }, 2000);
                  } catch (err: any) {
                    // 에러 메시지 표시
                    const errorMessage = err?.message || '회원가입에 실패했습니다. 다시 시도해주세요.';
                    setError(errorMessage);
                  } finally {
                    setIsLoading(false);
                  }
                }}
                >
                {isLoading ? '가입 중...' : success ? '가입 완료!' : '가입하기'}
              </Button>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
