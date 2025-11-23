import React, { useState } from 'react';
import {
  ChevronLeft,
  Bookmark,
  Share2,
  ExternalLink,
  ChevronDown,
  ChevronUp,
} from 'lucide-react';

import { Card } from '../components/ui/ThemedCard';
import { Button } from '../components/ui/ThemedButton';
import { Badge } from '../components/ui/Badge';
import { colors } from '../styles/design-tokens';
import type { Page } from '../types/page';

/* ------------------------------------------------
   타입 정의
--------------------------------------------------*/
interface FaqItem {
  question: string;
  answer: string;
}

export interface WelfareDetailData {
  id: number;
  categoryTag: string;
  ageTag: string;
  title: string;
  aiSummary: string;
  eligibilityItems: string[];
  services: string[];
  faqs: FaqItem[];
  originalUrl: string;
}

/* ------------------------------------------------
   더미 데이터 (나중에 API 데이터로 교체)
--------------------------------------------------*/
const MOCK_WELFARE_DETAIL: WelfareDetailData = {
  id: 1,
  categoryTag: '노인돌봄',
  ageTag: '65세 이상',
  title: '노인 장기요양보험',
  aiSummary:
    '고령이나 노인성 질병 등으로 일상생활을 혼자서 수행하기 어려운 노인에게 ' +
    '신체활동, 가사활동 지원 등의 장기요양급여를 제공하여 건강증진 및 생활안정을 돕는 제도입니다.',
  eligibilityItems: [
    '만 65세 이상 노인 또는 치매, 뇌혈관질환 등 노인성 질병 보유자',
    '6개월 이상 일상생활 수행이 어려운 것으로 인정된 자',
  ],
  services: ['방문요양', '방문목욕', '방문간호', '주·야간보호', '단기보호', '복지용구'],
  faqs: [
    {
      question: '신청 자격이 어떻게 되나요?',
      answer: '만 65세 이상 또는 노인성 질병 보유 시 신청할 수 있습니다.',
    },
    {
      question: '어떻게 신청하나요?',
      answer: '국민건강보험공단 지사 방문 또는 온라인 접수 가능합니다.',
    },
    {
      question: '필요한 서류는 무엇인가요?',
      answer: '장기요양인정신청서, 의사소견서 등이 필요합니다.',
    },
    {
      question: '비용은 얼마나 드나요?',
      answer: '본인부담금은 서비스 비용의 15~20%입니다.',
    },
  ],
  originalUrl: 'https://www.longtermcare.or.kr',
};

/* ------------------------------------------------
   WelfareDetail UI Component
--------------------------------------------------*/

interface WelfareDetailProps {
  onNavigate?: (page: Page) => void;
  data?: WelfareDetailData;     // 나중에 API 연결하면 이걸 외부에서 넣어줌
  isBookmarked: boolean;        // 상위(App)에서 상태 관리
  onToggleBookmark: () => void; // 상위에서 북마크 업데이트
}

export function WelfareDetail({
  onNavigate,
  data = MOCK_WELFARE_DETAIL, // 기본값: 더미데이터
  isBookmarked,
  onToggleBookmark,
}: WelfareDetailProps) {
  
  const [expandedFaq, setExpandedFaq] = useState<number | null>(null);

  return (
    <div className="min-h-screen pb-20" style={{ backgroundColor: colors.lightGray }}>

      {/* ---------------- Header ---------------- */}
      <div className="bg-white border-b sticky top-16 z-30" style={{ borderColor: colors.lightGray }}>
        <div className="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between">
          
          <button
            onClick={() => onNavigate?.('welfare')}
            className="flex items-center space-x-2 hover:opacity-70 transition-opacity"
            style={{ color: colors.textDark }}
          >
            <ChevronLeft size={20} />
            <span>목록으로</span>
          </button>

          <div className="flex items-center space-x-2">
            {/* 북마크 */}
            <button
              onClick={onToggleBookmark}
              className="p-2 rounded-full hover:bg-opacity-10 transition-all"
              style={{ backgroundColor: isBookmarked ? colors.pointYellow : colors.lightGray }}
            >
              <Bookmark
                size={20}
                fill={isBookmarked ? colors.textDark : 'none'}
                style={{ color: colors.textDark }}
              />
            </button>

            {/* 공유 */}
            <button
              className="p-2 rounded-full hover:bg-opacity-10 transition-all"
              style={{ backgroundColor: colors.lightGray }}
            >
              <Share2 size={20} style={{ color: colors.textDark }} />
            </button>
          </div>

        </div>
      </div>

      {/* ---------------- Content ---------------- */}
      <div className="max-w-4xl mx-auto px-4 py-8">

        {/* 타이틀 + AI 요약 */}
        <Card variant="elevated" padding="lg" className="mb-6">
          <div className="space-y-4">

            <div className="flex flex-wrap gap-2">
              <Badge variant="level2" size="sm">{data.categoryTag}</Badge>
              <Badge variant="default" size="sm">{data.ageTag}</Badge>
            </div>

            <h1 className="text-2xl" style={{ color: colors.textDark }}>
              {data.title}
            </h1>

            <div className="p-4 rounded-xl" style={{ backgroundColor: colors.mainGreen1 + '20' }}>
              <p className="text-sm" style={{ color: colors.textDark }}>
                <strong>AI 요약:</strong> {data.aiSummary}
              </p>
            </div>
          </div>
        </Card>

        {/* 지원 대상 */}
        <Card variant="elevated" padding="lg" className="mb-6">
          <h2 className="text-lg mb-4" style={{ color: colors.textDark }}>지원 대상</h2>
          <ul className="space-y-2">
            {data.eligibilityItems.map((item, idx) => (
              <li key={idx} className="flex items-start space-x-2">
                <span style={{ color: colors.mainGreen2 }}>•</span>
                <span className="text-sm" style={{ color: colors.textSub }}>{item}</span>
              </li>
            ))}
          </ul>
        </Card>

        {/* 제공 서비스 */}
        <Card variant="elevated" padding="lg" className="mb-6">
          <h2 className="text-lg mb-4" style={{ color: colors.textDark }}>제공 서비스</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {data.services.map((service) => (
              <div
                key={service}
                className="p-3 rounded-lg"
                style={{ backgroundColor: colors.lightGray }}
              >
                <p className="text-sm" style={{ color: colors.textDark }}>
                  {service}
                </p>
              </div>
            ))}
          </div>
        </Card>

        {/* FAQ */}
        <Card variant="elevated" padding="lg" className="mb-6">
          <h2 className="text-lg mb-4" style={{ color: colors.textDark }}>자주 묻는 질문</h2>
          <div className="space-y-3">
            {data.faqs.map((faq, index) => (
              <div
                key={index}
                className="border rounded-xl overflow-hidden"
                style={{ borderColor: colors.lightGray }}
              >
                <button
                  onClick={() => setExpandedFaq(expandedFaq === index ? null : index)}
                  className="w-full p-4 flex items-center justify-between hover:bg-opacity-50 transition-all"
                  style={{ backgroundColor: expandedFaq === index ? colors.lightGray : 'transparent' }}
                >
                  <span className="text-sm text-left" style={{ color: colors.textDark }}>
                    {faq.question}
                  </span>

                  {expandedFaq === index ? (
                    <ChevronUp size={18} style={{ color: colors.textSub }} />
                  ) : (
                    <ChevronDown size={18} style={{ color: colors.textSub }} />
                  )}
                </button>

                {expandedFaq === index && (
                  <div className="p-4 border-t" style={{ borderColor: colors.lightGray }}>
                    <p className="text-sm" style={{ color: colors.textSub }}>
                      {faq.answer}
                    </p>
                  </div>
                )}
              </div>
            ))}
          </div>
        </Card>

        {/* 원문 문서 보기 */}
        <Card variant="outlined" padding="md">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm mb-1" style={{ color: colors.textDark }}>
                원문 문서 보기
              </p>
              <p className="text-xs" style={{ color: colors.textSub }}>
                정확한 정보는 원문을 참고하세요
              </p>
            </div>

            <Button
              variant="outline"
              size="sm"
              icon={<ExternalLink size={16} />}
              onClick={() => window.open(data.originalUrl, '_blank')}
            >
              문서 열기
            </Button>
          </div>
        </Card>

        {/* Action Buttons */}
        <div className="flex items-center space-x-3 mt-6">
          <Button variant="primary" size="lg" fullWidth>
            신청하기
          </Button>
          <Button variant="secondary" size="lg" fullWidth>
            상담 문의
          </Button>
        </div>

      </div>
    </div>
  );
}
