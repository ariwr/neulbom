// src/services/welfareService.ts
export interface Welfare {
  id: number;
  title: string;
  summary: string;
  eligibility: string[];
  date: string;          // 최근 본 날짜나 등록일 등
}

export const initialWelfares: Welfare[] = [
  {
    id: 1,
    title: '노인 돌봄 서비스 지원',
    summary: '만 65세 이상 어르신을 대상으로 일상생활 지원 서비스를 제공합니다.',
    eligibility: ['65세 이상', '기초생활수급자'],
    date: '2025.11.20',
  },
  {
    id: 2,
    title: '장애인 활동지원 서비스',
    summary: '신체적·정신적 장애로 혼자 일상생활이 어려운 분들을 위한 활동 지원',
    eligibility: ['장애인', '소득기준 충족'],
    date: '2025.11.19',
  },
  {
    id: 3,
    title: '가족돌봄 휴가제도',
    summary: '가족 구성원의 질병, 사고 등으로 돌봄이 필요한 경우 사용 가능한 휴가',
    eligibility: ['근로자', '가족돌봄 필요'],
    date: '2025.11.18',
  },
];