import React, { useState } from 'react';
import { ChevronLeft, AlertTriangle } from 'lucide-react';
import { Card } from '../components/ui/ThemedCard';
import { Input } from '../components/ui/ThemedInput';
import { TextArea } from '../components/ui/ThemedTextArea';
import { Button } from '../components/ui/ThemedButton';
import { Badge } from '../components/ui/Badge';
import { colors } from '../styles/design-tokens';
import type { Page } from '../types/page';

interface PostSubmitProps {
  onNavigate: (page: Page) => void;
  onSubmit: (data: {title: string; preview: string; tags: string[] }) => void;
}

export function PostSubmit({ onNavigate, onSubmit }: PostSubmitProps) {
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [tags, setTags] = useState<string[]>([]);
  const [aiSafetyCheck, setAiSafetyCheck] = useState(false);

  const suggestedTags = ['노인돌봄', '장애인지원', '아동돌봄', '정서지원', '정보공유', '후기', '고민상담'];

  return (
    <div className="min-h-screen pb-20" style={{ backgroundColor: colors.lightGray }}>
      {/* Header */}
      <div className="bg-white border-b sticky top-16 z-30" style={{ borderColor: colors.lightGray }}>
        <div className="max-w-4xl mx-auto px-4 py-4">
          <button
            onClick={() => onNavigate('community')}
            className="flex items-center space-x-2 hover:opacity-70 transition-opacity"
            style={{ color: colors.textDark }}
          >
            <ChevronLeft size={20} />
            <span>취소</span>
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Form */}
          <div className="lg:col-span-2 space-y-6">
            <div>
              <h1 className="text-2xl mb-2" style={{ color: colors.textDark }}>
                글쓰기
              </h1>
              <p className="text-sm" style={{ color: colors.textSub }}>
                커뮤니티 규칙을 준수하여 작성해주세요
              </p>
            </div>

            <Card variant="elevated" padding="lg">
              <div className="space-y-6">
                <Input
                  label="제목"
                  placeholder="제목을 입력하세요"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  fullWidth
                />

                <div>
                  <label className="block text-sm mb-2" style={{ color: colors.textDark }}>
                    태그 선택
                  </label>
                  <div className="flex flex-wrap gap-2">
                    {suggestedTags.map((tag) => (
                      <Badge 
                        key={tag}
                        variant={tags.includes(tag) ? 'level2' : 'default'}
                        size="sm"
                      >
                        <button onClick={() => {
                          if (tags.includes(tag)) {
                            setTags(tags.filter(t => t !== tag));
                          } else {
                            setTags([...tags, tag]);
                          }
                        }}>
                          #{tag}
                        </button>
                      </Badge>
                    ))}
                  </div>
                </div>

                <TextArea
                  label="내용"
                  placeholder="내용을 입력하세요"
                  value={content}
                  onChange={(e) => setContent(e.target.value)}
                  rows={12}
                  fullWidth
                />

                <div className="flex items-center justify-between pt-4">
                  <div className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      id="anonymous"
                      className="w-4 h-4 rounded"
                      style={{ accentColor: colors.mainGreen2 }}
                    />
                    <label htmlFor="anonymous" className="text-sm" style={{ color: colors.textSub }}>
                      익명으로 작성
                    </label>
                  </div>
                </div>
              </div>
            </Card>

            <div className="flex items-center space-x-3">
              <Button variant="primary"
              size="lg"
              fullWidth
              onClick={() => {
                // 간단한 유효성 검사
                if (!title.trim() || !content.trim()) {
                  alert('제목과 내용을 입력해주세요.');
                  return
                }

                onSubmit({
                  title,
                  preview: content,
                  tags,
                });

                onNavigate('community')
              }}
              >
                게시하기
              </Button>
              <Button variant="outline" size="lg" onClick={() => onNavigate('community')}>
                취소
              </Button>
            </div>
          </div>

          {/* AI Safety Preview Panel */}
          <div className="lg:col-span-1">
            <div className="sticky top-24 space-y-4">
              <Card variant="elevated" padding="md">
                <div className="space-y-4">
                  <div className="flex items-center space-x-2">
                    <AlertTriangle size={18} style={{ color: colors.mainGreen2 }} />
                    <h3 className="text-sm" style={{ color: colors.textDark }}>
                      AI 안전 검사
                    </h3>
                  </div>

                  {!aiSafetyCheck ? (
                    <div>
                      <p className="text-xs mb-3" style={{ color: colors.textSub }}>
                        작성 중인 글의 안전성을 AI가 자동으로 확인합니다.
                      </p>
                      <Button variant="outline" size="sm" fullWidth>
                        검사 시작
                      </Button>
                    </div>
                  ) : (
                    <div className="space-y-3">
                      <div 
                        className="p-3 rounded-lg"
                        style={{ backgroundColor: colors.success + '20' }}
                      >
                        <p className="text-xs" style={{ color: colors.success }}>
                          ✓ 안전한 내용입니다
                        </p>
                      </div>
                      <p className="text-xs" style={{ color: colors.textSub }}>
                        위기 감지: 없음<br />
                        부적절한 표현: 없음
                      </p>
                    </div>
                  )}
                </div>
              </Card>

              <Card variant="outlined" padding="md">
                <h3 className="text-sm mb-3" style={{ color: colors.textDark }}>
                  커뮤니티 규칙
                </h3>
                <ul className="space-y-2">
                  <li className="text-xs" style={{ color: colors.textSub }}>
                    • 타인을 존중하는 언어 사용
                  </li>
                  <li className="text-xs" style={{ color: colors.textSub }}>
                    • 개인정보 공유 금지
                  </li>
                  <li className="text-xs" style={{ color: colors.textSub }}>
                    • 광고성 게시물 금지
                  </li>
                  <li className="text-xs" style={{ color: colors.textSub }}>
                    • 허위 정보 유포 금지
                  </li>
                </ul>
              </Card>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
