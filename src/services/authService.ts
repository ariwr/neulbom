// 인증 서비스
import { apiPost, apiGet, apiPut, setAuthToken } from '../config/api';

export interface SignupData {
  name: string;
  email: string;
  password: string;
  password_confirm: string;
  age?: number;
  region?: string;
  care_target?: string;
}

export interface LoginData {
  email: string;
  password: string;
}

export interface UserProfile {
  id: number;
  email: string;
  age?: number;
  region?: string;
  level: number;
  is_active: boolean;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

// 회원가입
export async function signup(data: SignupData): Promise<TokenResponse> {
  const response = await apiPost<TokenResponse>('/api/auth/signup', data);
  setAuthToken(response.access_token);
  return response;
}

// 로그인 (인증 없이 호출)
export async function login(data: LoginData): Promise<TokenResponse> {
  try {
    // 로그인 API는 인증이 필요 없으므로 직접 fetch 호출
    const url = `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/api/auth/login`;
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: '로그인에 실패했습니다.' }));
      let errorMessage = errorData.detail || errorData.message || '로그인에 실패했습니다.';
      
      // 백엔드 에러 메시지를 한국어로 변환
      if (errorMessage.includes('Incorrect email or password') || errorMessage.includes('email') || errorMessage.includes('password')) {
        errorMessage = '회원이 아닙니다. 회원가입을 진행해주세요.';
      } else if (errorMessage.includes('Inactive user')) {
        errorMessage = '비활성화된 계정입니다. 관리자에게 문의해주세요.';
      }
      
      const error = new Error(errorMessage) as Error & { status?: number };
      error.status = response.status;
      throw error;
    }
    
    const responseData: TokenResponse = await response.json();
    
    // 개발 모드에서만 로깅
    if (import.meta.env.DEV) {
      console.log('로그인 응답:', responseData);
    }
    
    if (!responseData || !responseData.access_token) {
      if (import.meta.env.DEV) {
        console.error('로그인 응답에 access_token이 없습니다:', responseData);
      }
      throw new Error('로그인 응답에 토큰이 없습니다.');
    }
    
    // 토큰 저장 (동기적으로 실행됨)
    setAuthToken(responseData.access_token);
    
    // 개발 모드에서만 로깅
    if (import.meta.env.DEV) {
      console.log('토큰 저장 완료:', responseData.access_token.substring(0, 20) + '...');
    }
    
    // 토큰이 제대로 저장되었는지 즉시 확인
    const savedToken = localStorage.getItem('authToken');
    if (!savedToken) {
      if (import.meta.env.DEV) {
        console.error('토큰 저장 실패! 저장된 토큰이 없습니다.');
      }
      throw new Error('토큰 저장에 실패했습니다.');
    }
    
    return responseData;
  } catch (error: any) {
    // 개발 모드에서만 로깅
    if (import.meta.env.DEV) {
      console.error('로그인 함수 오류:', error);
    }
    // 에러를 다시 throw하여 상위에서 처리할 수 있도록 함
    throw error;
  }
}

// 로그아웃
export function logout(): void {
  setAuthToken(null);
}

// 프로필 조회
export async function getProfile(): Promise<UserProfile> {
  return apiGet<UserProfile>('/api/users/me');
}

// 프로필 수정
export async function updateProfile(data: Partial<UserProfile>): Promise<UserProfile> {
  return apiPut<UserProfile>('/api/users/me', data);
}

