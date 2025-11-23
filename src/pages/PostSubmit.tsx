import React, { useState } from 'react';
import { ChevronLeft, AlertTriangle } from 'lucide-react';
import { Card } from '../components/ui/ThemedCard';
import { Input } from '../components/ui/ThemedInput';
import { TextArea } from '../components/ui/ThemedTextArea';
import { Button } from '../components/ui/ThemedButton';
import { Badge } from '../components/ui/Badge';
import { colors } from '../styles/design-tokens';
import type { Page } from '../types/page';
import type { PostCategory } from '../services/postService';

interface PostSubmitProps {
  onNavigate: (page: Page) => void;
  onSubmit: (data: { title: string; preview: string; category: PostCategory }) => void;
  isLoggedIn: boolean;
}

export function PostSubmit({ onNavigate, onSubmit, isLoggedIn }: PostSubmitProps) {
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [category, setCategory] = useState<PostCategory>('free');

  const categories: { id: PostCategory; label: string }[] = [
    { id: 'info', label: '정보공유' },
    { id: 'counsel', label: '고민상담' },
    { id: 'free', label: '자유' },
  ];

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
                {/* 카테고리 선택 */}
                <div>
                  <label className="block text-sm font-medium mb-2" style={{ color: colors.textDark }}>
                    카테고리
                  </label>
                  <div className="flex space-x-2">
                    {categories.map((cat) => (
                      <button
                        key={cat.id}
                        onClick={() => setCategory(cat.id)}
                        className={`px-4 py-2 rounded-full text-sm transition-all ${
                          category === cat.id
                            ? 'text-white border-transparent'
                            : 'bg-white text-gray-600 hover:bg-gray-50 border border-gray-300'
                        }`}
                        style={{
                          backgroundColor: category === cat.id ? colors.mainGreen2 : undefined,
                          borderColor: category === cat.id ? undefined : colors.lightGray,
                        }}
                      >
                        {cat.label}
                      </button>
                    ))}
                  </div>
                </div>

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

            <div className="flex items-center justify-end space-x-3 mt-6">
              <Button 
                variant="primary"
                size="lg"
                className="w-32" // 고정 너비로 변경하여 크기 통일
                onClick={() => {
                  // 로그인 확인 (isLoggedIn prop 사용)
                  if (!isLoggedIn) {
                    alert('게시글을 작성하려면 로그인이 필요합니다.');
                    onNavigate('login');
                    return;
                  }

                  // 간단한 유효성 검사
                  if (!title.trim() || !content.trim()) {
                    alert('제목과 내용을 입력해주세요.');
                    return
                  }

                  onSubmit({
                    title,
                    preview: content,
                    category,
                  });

                  onNavigate('community')
                }}
              >
                게시하기
              </Button>
              <Button 
                variant="outline" 
                size="lg"
                className="w-32" // 고정 너비로 변경하여 크기 통일
                onClick={() => onNavigate('community')}
              >
                취소
              </Button>
            </div>
          </div>

          {/* Right Sidebar - Rules */}
          <div className="lg:col-span-1">
            <Card variant="outlined" padding="md" className="sticky top-24">
              <div className="flex items-center space-x-2 mb-4">
                <AlertTriangle size={20} style={{ color: colors.mainGreen2 }} />
                <h3 className="text-base font-bold" style={{ color: colors.textDark }}>
                  커뮤니티 규칙
                </h3>
              </div>
              <ul className="space-y-4">
                <li className="flex items-start space-x-2">
                  <span className="w-1.5 h-1.5 rounded-full mt-2 flex-shrink-0" style={{ backgroundColor: colors.textSub }}></span>
                  <span className="text-sm" style={{ color: colors.textSub }}>
                    타인을 존중하는 언어 사용
                  </span>
                </li>
                <li className="flex items-start space-x-2">
                  <span className="w-1.5 h-1.5 rounded-full mt-2 flex-shrink-0" style={{ backgroundColor: colors.textSub }}></span>
                  <span className="text-sm" style={{ color: colors.textSub }}>
                    개인정보 공유 금지
                  </span>
                </li>
                <li className="flex items-start space-x-2">
                  <span className="w-1.5 h-1.5 rounded-full mt-2 flex-shrink-0" style={{ backgroundColor: colors.textSub }}></span>
                  <span className="text-sm" style={{ color: colors.textSub }}>
                    광고성 게시물 금지
                  </span>
                </li>
                <li className="flex items-start space-x-2">
                  <span className="w-1.5 h-1.5 rounded-full mt-2 flex-shrink-0" style={{ backgroundColor: colors.textSub }}></span>
                  <span className="text-sm" style={{ color: colors.textSub }}>
                    허위 정보 유포 금지
                  </span>
                </li>
              </ul>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
