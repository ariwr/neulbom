// API 설정 파일
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// 토큰 관리
export const getAuthToken = (): string | null => {
  return localStorage.getItem('authToken');
};

export const setAuthToken = (token: string | null): void => {
  if (token) {
    localStorage.setItem('authToken', token);
  } else {
    localStorage.removeItem('authToken');
  }
};

// API 호출 헬퍼 함수
export async function apiCall<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  const token = getAuthToken();
  
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...options.headers,
  };
  
  if (token) {
    // 토큰 앞뒤 공백 제거
    const cleanToken = token.trim();
    headers['Authorization'] = `Bearer ${cleanToken}`;
    // 개발 모드에서만 로깅
    if (import.meta.env.DEV) {
      console.log('API 호출:', endpoint, '토큰 포함됨', cleanToken.substring(0, 20) + '...');
    }
  } else {
    // 개발 모드에서만 로깅
    if (import.meta.env.DEV) {
      console.warn('API 호출:', endpoint, '토큰 없음');
    }
  }
  
  const config: RequestInit = {
    ...options,
    headers,
  };
  
  try {
    const response = await fetch(url, config);
    
    // 응답이 JSON인지 확인
    const contentType = response.headers.get('content-type');
    const isJson = contentType?.includes('application/json');
    
    if (!response.ok) {
      let errorMessage = '요청 실패';
      let statusCode = response.status;
      
      if (isJson) {
        const errorData = await response.json();
        errorMessage = errorData.detail || errorData.message || errorMessage;
      } else {
        errorMessage = await response.text() || errorMessage;
      }
      
      // 401 에러인 경우 토큰이 없거나 만료된 것일 수 있음
      if (statusCode === 401 && import.meta.env.DEV) {
        console.error('401 Unauthorized:', endpoint, '토큰:', token ? '있음' : '없음');
        // 토큰이 있는데 401이면 토큰이 만료되었을 수 있음
        if (token) {
          console.warn('토큰이 있지만 인증 실패. 토큰이 만료되었을 수 있습니다.');
        }
      }
      
      const error = new Error(errorMessage) as Error & { status?: number };
      error.status = statusCode;
      throw error;
    }
    
    if (isJson) {
      return await response.json();
    }
    
    return await response.text() as unknown as T;
  } catch (error) {
    // 개발 모드에서만 상세 로깅
    if (import.meta.env.DEV) {
      console.error('API 호출 오류:', error);
    }
    throw error;
  }
}

// GET 요청
export async function apiGet<T>(endpoint: string): Promise<T> {
  return apiCall<T>(endpoint, { method: 'GET' });
}

// POST 요청
export async function apiPost<T>(endpoint: string, data?: unknown): Promise<T> {
  return apiCall<T>(endpoint, {
    method: 'POST',
    body: data ? JSON.stringify(data) : undefined,
  });
}

// PUT 요청
export async function apiPut<T>(endpoint: string, data?: unknown): Promise<T> {
  return apiCall<T>(endpoint, {
    method: 'PUT',
    body: data ? JSON.stringify(data) : undefined,
  });
}

// DELETE 요청
export async function apiDelete<T>(endpoint: string): Promise<T> {
  return apiCall<T>(endpoint, { method: 'DELETE' });
}

