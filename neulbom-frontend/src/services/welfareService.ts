// src/services/welfareService.ts
import { apiGet, apiPost } from '../config/api';

export interface Welfare {
  id: number;
  title: string;
  summary?: string;
  source_link?: string;
  region?: string;
  apply_start?: string;
  apply_end?: string;
  is_always: boolean;
  status: string;
  eligibility?: string[];
  date?: string;
}

export interface WelfareDetail {
  id: number;
  title: string;
  summary?: string;
  full_text?: string;  // 서비스 요약
  source_link?: string;
  region?: string;
  age_min?: number;
  age_max?: number;
  care_target?: string;
  apply_start?: string;
  apply_end?: string;
  is_always: boolean;
  status: string;
  category?: string;
}

export interface WelfareSearchParams {
  keyword?: string;
  region?: string;
  age?: number;
  care_target?: string;
  skip?: number;
  limit?: number;
}

// summary에서 챗봇 대화체 제거 함수
function cleanSummary(summary: string | undefined): string | undefined {
  if (!summary) return summary;
  
  let cleaned = summary.trim();
  
  // 챗봇 대화체 패턴 제거
  const chatbotPatterns = [
    /말씀해주셔서\s*감사해요\.?\s*더\s*자세히\s*들려주실\s*수\s*있나요\.?/gi,
    /말씀해주셔서\s*감사해요\.?/gi,
    /더\s*자세히\s*들려주실\s*수\s*있나요\.?/gi,
    /자세히\s*들려주실\s*수\s*있나요\.?/gi,
    /무엇을\s*도와드릴까요\.?/gi,
    /어떻게\s*도와드릴까요\.?/gi,
    /무엇을\s*도와드릴\s*수\s*있을까요\.?/gi,
    /도와드릴\s*수\s*있어요\.?/gi,
    /알려주세요\.?/gi,
    /문의해주세요\.?/gi,
    /감사해요\.?/gi,
  ];
  
  chatbotPatterns.forEach(pattern => {
    cleaned = cleaned.replace(pattern, '');
  });
  
  // 연속된 공백과 구두점 정리
  cleaned = cleaned.replace(/\s+/g, ' ').trim();
  cleaned = cleaned.replace(/^[.,\s]+|[.,\s]+$/g, '').trim();
  
  return cleaned || undefined;
}

// 복지 정보 검색
export async function searchWelfare(params: WelfareSearchParams = {}): Promise<Welfare[]> {
  try {
    const queryParams = new URLSearchParams();
    if (params.keyword) queryParams.append('keyword', params.keyword);
    if (params.region) queryParams.append('region', params.region);
    if (params.age) queryParams.append('age', params.age.toString());
    if (params.care_target) queryParams.append('care_target', params.care_target);
    
    // Pagination
    if (params.skip !== undefined) queryParams.append('skip', params.skip.toString());
    if (params.limit !== undefined) queryParams.append('limit', params.limit.toString());

    const queryString = queryParams.toString();
    const endpoint = `/api/welfare/search${queryString ? `?${queryString}` : ''}`;
    
    const welfares = await apiGet<Welfare[]>(endpoint);
    return welfares
      .map(w => ({
        ...w,
        summary: cleanSummary(w.summary) || undefined, // 챗봇 대화체 제거, 없으면 undefined
        date: w.apply_start || new Date().toISOString().split('T')[0],
        eligibility: [], // 백엔드에서 제공하지 않으면 빈 배열
      }))
      .filter(w => {
        // title이 있어야만 표시 (summary는 선택사항)
        return !!(w.title && w.title.trim() !== '');
      });
  } catch (error) {
    console.error('복지 정보 검색 실패:', error);
    throw error;
  }
}

// 복지 정보 북마크
export async function bookmarkWelfare(welfareId: number): Promise<void> {
  try {
    await apiPost(`/api/welfare/${welfareId}/bookmark`);
  } catch (error) {
    console.error('북마크 실패:', error);
    throw error;
  }
}

// 최근 본 복지 정보 조회 (로그인한 사용자만)
export async function getRecentWelfares(limit: number = 10): Promise<Welfare[]> {
  try {
    const welfares = await apiGet<Welfare[]>(`/api/welfare/recommend/recent?limit=${limit}`);
    return welfares
      .map(w => ({
        ...w,
        summary: cleanSummary(w.summary) || undefined, // 챗봇 대화체 제거, 없으면 undefined
        date: w.apply_start || new Date().toISOString().split('T')[0],
        eligibility: [],
      }))
      .filter(w => {
        // title이 있어야만 표시 (summary는 선택사항)
        return !!(w.title && w.title.trim() !== '');
      });
  } catch (error: any) {
    // 인증 오류인 경우 빈 배열 반환
    if (error?.status === 401 || error?.status === 403) {
      return [];
    }
    console.error('최근 본 복지 정보 조회 실패:', error);
    return [];
  }
}

// 인기 복지 정보 조회 (조회수 기준)
export async function getPopularWelfares(limit: number = 10): Promise<Welfare[]> {
  try {
    const welfares = await apiGet<Welfare[]>(`/api/welfare/recommend/popular?limit=${limit}`);
    return welfares
      .map(w => ({
        ...w,
        summary: cleanSummary(w.summary) || undefined, // 챗봇 대화체 제거, 없으면 undefined
        date: w.apply_start || new Date().toISOString().split('T')[0],
        eligibility: [],
      }))
      .filter(w => {
        // title이 있어야만 표시 (summary는 선택사항)
        return !!(w.title && w.title.trim() !== '');
      });
  } catch (error) {
    console.error('인기 복지 정보 조회 실패:', error);
    return [];
  }
}

// 복지 정보 상세 조회
export async function getWelfareDetail(welfareId: number): Promise<WelfareDetail> {
  try {
    const welfare = await apiGet<WelfareDetail>(`/api/welfare/${welfareId}`);
    return {
      ...welfare,
      summary: cleanSummary(welfare.summary), // 챗봇 대화체 제거
      full_text: welfare.full_text ? cleanSummary(welfare.full_text) : welfare.full_text, // full_text도 정리
    };
  } catch (error) {
    console.error('복지 정보 상세 조회 실패:', error);
    throw error;
  }
}

// 초기 더미 데이터 (백엔드 연결 전까지 사용)
export const initialWelfares: Welfare[] = [
  {
    id: 1,
    title: '노인 돌봄 서비스 지원',
    summary: '만 65세 이상 어르신을 대상으로 일상생활 지원 서비스를 제공합니다.',
    eligibility: ['65세 이상', '기초생활수급자'],
    date: '2025.11.20',
    is_always: false,
    status: 'active',
  },
  {
    id: 2,
    title: '장애인 활동지원 서비스',
    summary: '신체적·정신적 장애로 혼자 일상생활이 어려운 분들을 위한 활동 지원',
    eligibility: ['장애인', '소득기준 충족'],
    date: '2025.11.19',
    is_always: false,
    status: 'active',
  },
  {
    id: 3,
    title: '가족돌봄 휴가제도',
    summary: '가족 구성원의 질병, 사고 등으로 돌봄이 필요한 경우 사용 가능한 휴가',
    eligibility: ['근로자', '가족돌봄 필요'],
    date: '2025.11.18',
    is_always: false,
    status: 'active',
  },
];
