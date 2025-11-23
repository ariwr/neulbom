import React, { useState, useEffect } from 'react';
import {
  ChevronLeft,
  Bookmark,
  Share2,
  ExternalLink,
} from 'lucide-react';

import { Card } from '../components/ui/ThemedCard';
import { Button } from '../components/ui/ThemedButton';
import { Badge } from '../components/ui/Badge';
import { colors } from '../styles/design-tokens';
import type { Page } from '../types/page';
import { getWelfareDetail, type WelfareDetail as WelfareDetailType } from '../services/welfareService';

interface WelfareDetailProps {
  onNavigate?: (page: Page) => void;
  welfareId: number;            // 복지 정보 ID
  isBookmarked: boolean;        // 상위(App)에서 상태 관리
  onToggleBookmark: () => void; // 상위에서 북마크 업데이트
}

export function WelfareDetail({
  onNavigate,
  welfareId,
  isBookmarked,
  onToggleBookmark,
}: WelfareDetailProps) {
  
  const [welfare, setWelfare] = useState<WelfareDetailType | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // API에서 복지 정보 가져오기
  useEffect(() => {
    const loadWelfare = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const data = await getWelfareDetail(welfareId);
        setWelfare(data);
      } catch (err: any) {
        console.error('복지 정보 상세 조회 실패:', err);
        setError('복지 정보를 불러올 수 없습니다.');
      } finally {
        setIsLoading(false);
      }
    };

    loadWelfare();
  }, [welfareId]);

  // full_text에서 정보 추출
  const parseFullText = (fullText?: string) => {
    if (!fullText) return { summary: '', eligibility: [], services: [], department: '', organization: '', contact: '' };
    
    const lines = fullText.split('\n');
    let summary = '';
    let department = '';
    let organization = '';
    let contact = '';
    const eligibility: string[] = [];
    const services: string[] = [];
    
    for (const line of lines) {
      const trimmedLine = line.trim();
      if (trimmedLine.startsWith('제목:')) {
        continue;
      } else if (trimmedLine.startsWith('내용:') || trimmedLine.startsWith('서비스요약:')) {
        summary = trimmedLine.replace(/^(내용|서비스요약):/, '').trim();
      } else if (trimmedLine.startsWith('대상:')) {
        const targetText = trimmedLine.replace('대상:', '').trim();
        if (targetText) {
          eligibility.push(...targetText.split(/[,，]/).map(s => s.trim()).filter(s => s));
        }
      } else if (trimmedLine.startsWith('소관부처명:')) {
        department = trimmedLine.replace('소관부처명:', '').trim();
      } else if (trimmedLine.startsWith('소관조직명:')) {
        organization = trimmedLine.replace('소관조직명:', '').trim();
      } else if (trimmedLine.startsWith('연락처:') || trimmedLine.startsWith('대표문의:')) {
        contact = trimmedLine.replace(/^(연락처|대표문의):/, '').trim();
      }
    }
    
    // summary가 없으면 full_text 전체를 요약으로 사용 (기존 로직 유지하되, 키워드가 없는 경우에만)
    if (!summary && fullText && !fullText.includes('내용:') && !fullText.includes('서비스요약:')) {
      summary = fullText.replace(/제목:|내용:|대상:|기관:|연락처:|소관부처명:|소관조직명:|대표문의:/g, '').trim();
    }
    
    return { summary, eligibility, services, department, organization, contact };
  };

  if (isLoading) {
    return (
      <div className="min-h-screen pb-20 flex items-center justify-center" style={{ backgroundColor: colors.lightGray }}>
        <p className="text-sm" style={{ color: colors.textSub }}>로딩 중...</p>
      </div>
    );
  }

  if (error || !welfare) {
    return (
      <div className="min-h-screen pb-20" style={{ backgroundColor: colors.lightGray }}>
        <div className="max-w-4xl mx-auto px-4 py-8">
          <Card variant="elevated" padding="lg">
            <p className="text-sm text-center" style={{ color: colors.error }}>
              {error || '복지 정보를 찾을 수 없습니다.'}
            </p>
            <div className="mt-4 text-center">
              <Button variant="outline" onClick={() => onNavigate?.('welfare')}>
                목록으로 돌아가기
              </Button>
            </div>
          </Card>
        </div>
      </div>
    );
  }

  const { summary, eligibility, services, department, organization, contact } = parseFullText(welfare.full_text);
  
  // 나이 태그 생성
  const ageTag = welfare.age_min && welfare.age_max
    ? `${welfare.age_min}세 ~ ${welfare.age_max}세`
    : welfare.age_min
    ? `${welfare.age_min}세 이상`
    : welfare.age_max
    ? `${welfare.age_max}세 이하`
    : null;

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

        {/* 타이틀 + 서비스 요약 */}
        <Card variant="elevated" padding="lg" className="mb-6">
          <div className="space-y-4">

            <div className="flex flex-wrap gap-2">
              {welfare.category && (
                <Badge variant="level2" size="sm">{welfare.category}</Badge>
              )}
              {welfare.region && (
                <Badge variant="default" size="sm">{welfare.region}</Badge>
              )}
              {ageTag && (
                <Badge variant="default" size="sm">{ageTag}</Badge>
              )}
              {welfare.care_target && (
                <Badge variant="default" size="sm">{welfare.care_target}</Badge>
              )}
            </div>

            <h1 className="text-2xl" style={{ color: colors.textDark }}>
              {welfare.title}
            </h1>

            {summary && (
              <div className="p-4 rounded-xl" style={{ backgroundColor: colors.mainGreen1 + '20' }}>
                <p className="text-sm" style={{ color: colors.textDark }}>
                  <strong>서비스 요약:</strong> {summary}
                </p>
              </div>
            )}

            <div className="grid grid-cols-2 gap-4 mt-2">
              {department && (
                <div className="p-3 rounded-lg bg-white border" style={{ borderColor: colors.lightGray }}>
                  <p className="text-xs text-gray-500 mb-1">소관부처명</p>
                  <p className="text-sm text-gray-800 font-medium">{department}</p>
                </div>
              )}
              {organization && (
                <div className="p-3 rounded-lg bg-white border" style={{ borderColor: colors.lightGray }}>
                  <p className="text-xs text-gray-500 mb-1">소관조직명</p>
                  <p className="text-sm text-gray-800 font-medium">{organization}</p>
                </div>
              )}
              {contact && (
                <div className="col-span-2 p-3 rounded-lg bg-white border" style={{ borderColor: colors.lightGray }}>
                  <p className="text-xs text-gray-500 mb-1">대표문의</p>
                  <p className="text-sm text-gray-800 font-medium">{contact}</p>
                </div>
              )}
            </div>
          </div>
        </Card>

        {/* 지원 대상 */}
        {eligibility.length > 0 && (
          <Card variant="elevated" padding="lg" className="mb-6">
            <h2 className="text-lg mb-4" style={{ color: colors.textDark }}>지원 대상</h2>
            <ul className="space-y-2">
              {eligibility.map((item, idx) => (
                <li key={idx} className="flex items-start space-x-2">
                  <span style={{ color: colors.mainGreen2 }}>•</span>
                  <span className="text-sm" style={{ color: colors.textSub }}>{item}</span>
                </li>
              ))}
            </ul>
          </Card>
        )}

        {/* 제공 서비스 */}
        {services.length > 0 && (
          <Card variant="elevated" padding="lg" className="mb-6">
            <h2 className="text-lg mb-4" style={{ color: colors.textDark }}>제공 서비스</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {services.map((service, idx) => (
                <div
                  key={idx}
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
        )}

        {/* 원문 문서 보기 */}
        {welfare.source_link && (
          <Card variant="outlined" padding="md" className="mb-6">
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
                onClick={() => window.open(welfare.source_link!, '_blank')}
              >
                문서 열기
              </Button>
            </div>
          </Card>
        )}

        {/* Action Buttons */}
        <div className="mt-6">
          {welfare.source_link ? (
            <Button 
              variant="primary" 
              size="lg" 
              fullWidth
              onClick={() => window.open(welfare.source_link!, '_blank')}
            >
              신청하기
            </Button>
          ) : (
            <Card variant="outlined" padding="md">
              <p className="text-sm text-center" style={{ color: colors.textSub }}>
                신청 링크 정보가 없습니다.
              </p>
            </Card>
          )}
        </div>

      </div>
    </div>
  );
}
