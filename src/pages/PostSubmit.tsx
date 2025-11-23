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
  onSubmit: (data: {title: string; preview: string; }) => void;
}

export function PostSubmit({ onNavigate, onSubmit }: PostSubmitProps) {
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [tags, setTags] = useState<string[]>([]);

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

                <TextArea
                  label="내용"
                  placeholder="내용을 입력하세요"
                  value={content}
                  onChange={(e) => setContent(e.target.value)}
                  rows={12}
                  fullWidth
                />
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
                });

                onNavigate('community')
              }}
              >
                게시하기
              </Button>
              <Button variant="outline" size="md" onClick={() => onNavigate('community')}>
                취소
              </Button>
            
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
