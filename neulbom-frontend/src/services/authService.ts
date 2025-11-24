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
    // 개발 환경에서는 Vite 프록시를 사용하고, 프로덕션에서는 환경변수 사용
    // 프록시 설정: vite.config.ts에서 /api -> http://localhost:8000으로 프록시됨
    const baseUrl = import.meta.env.DEV 
      ? '' // 개발 환경: 프록시 사용 (상대 경로, /api로 시작)
      : (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000');
    
    // 프록시를 사용할 때는 /api로 시작하는 경로를 사용
    // vite.config.ts에서 /api -> http://localhost:8000으로 프록시 설정됨
    const endpoint = '/api/auth/login';
    const url = import.meta.env.DEV ? endpoint : `${baseUrl}${endpoint}`;
    
    if (import.meta.env.DEV) {
      console.log('로그인 요청 URL:', url);
      console.log('프록시 대상:', 'http://localhost:8000');
      console.log('로그인 요청 데이터:', { email: data.email, password: '***' });
    }
    
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    
    if (!response.ok) {
      let errorData;
      try {
        errorData = await response.json();
      } catch {
        errorData = { detail: `서버 오류 (${response.status})` };
      }
      
      let errorMessage = errorData.detail || errorData.message || '로그인에 실패했습니다.';
      
      // 백엔드 에러 메시지를 한국어로 변환
      if (errorMessage.includes('Incorrect email or password') || 
          errorMessage.includes('email') || 
          errorMessage.includes('password')) {
        errorMessage = '이메일 또는 비밀번호가 올바르지 않습니다.';
      } else if (errorMessage.includes('Inactive user')) {
        errorMessage = '비활성화된 계정입니다. 관리자에게 문의해주세요.';
      }
      
      if (import.meta.env.DEV) {
        console.error('로그인 실패:', response.status, errorMessage);
      }
      
      const error = new Error(errorMessage) as Error & { status?: number };
      error.status = response.status;
      throw error;
    }
    
    const responseData: TokenResponse = await response.json();
    
    // 개발 모드에서만 로깅
    if (import.meta.env.DEV) {
      console.log('로그인 응답:', { 
        hasToken: !!responseData.access_token,
        tokenType: responseData.token_type 
      });
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
      const savedToken = localStorage.getItem('authToken');
      console.log('토큰 저장 완료:', savedToken ? '성공' : '실패');
    }
    
    return responseData;
  } catch (error: any) {
    // 네트워크 에러 처리
    if (error instanceof TypeError && error.message.includes('fetch')) {
      const networkError = new Error('서버에 연결할 수 없습니다. 백엔드 서버가 실행 중인지 확인해주세요.') as Error & { status?: number };
      networkError.status = 0;
      throw networkError;
    }
    
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

