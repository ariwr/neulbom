import React, { useState } from 'react';
import { ChevronLeft, AlertTriangle, MessageCircle } from 'lucide-react';
import { Card } from '../components/ui/ThemedCard';
import { Button } from '../components/ui/ThemedButton';
import { Badge } from '../components/ui/Badge';
import { TextArea } from '../components/ui/ThemedTextArea';
import { colors } from '../styles/design-tokens';

interface PostDetailProps {
  onNavigate?: (page: string) => void;
}

export function PostDetail({ onNavigate }: PostDetailProps) {
  const [comment, setComment] = useState('');

  const comments = [
    {
      id: 1,
      content: '저도 비슷한 경험을 했습니다. 힘내세요!',
      date: '2025.11.21 15:30',
    },
    {
      id: 2,
      content: '지역 복지센터에 문의해보시면 도움을 받으실 수 있을 거예요.',
      date: '2025.11.21 16:20',
    },
    {
      id: 3,
      content: '함께 이겨나가요. 혼자가 아니니까요.',
      date: '2025.11.21 17:45',
    },
  ];

  return (
    <div className="min-h-screen pb-20" style={{ backgroundColor: colors.lightGray }}>
      {/* Header */}
      <div className="bg-white border-b sticky top-16 z-30" style={{ borderColor: colors.lightGray }}>
        <div className="max-w-4xl mx-auto px-4 py-4">
          <button
            onClick={() => onNavigate?.('community')}
            className="flex items-center space-x-2 hover:opacity-70 transition-opacity"
            style={{ color: colors.textDark }}
          >
            <ChevronLeft size={20} />
            <span>목록으로</span>
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-4xl mx-auto px-4 py-8">
        {/* Crisis Alert Banner */}
        <Card 
          variant="elevated" 
          padding="md" 
          className="mb-6"
          style={{ backgroundColor: colors.error + '10', borderLeft: `4px solid ${colors.error}` }}
        >
          <div className="flex items-start space-x-3">
            <AlertTriangle size={20} style={{ color: colors.error }} />
            <div className="flex-1">
              <h3 className="text-sm mb-1" style={{ color: colors.error }}>
                위기 상황이 감지되었습니다
              </h3>
              <p className="text-xs mb-2" style={{ color: colors.textSub }}>
                이 게시글의 작성자가 도움이 필요할 수 있습니다. 따뜻한 위로와 실질적인 정보를 공유해주세요.
              </p>
              <div className="flex items-center space-x-2">
                <span className="text-xs" style={{ color: colors.textSub }}>
                  긴급 상담: <strong>129</strong>
                </span>
              </div>
            </div>
          </div>
        </Card>

        {/* Post Content */}
        <Card variant="elevated" padding="lg" className="mb-6">
          <div className="space-y-4">
            {/* Meta */}
            <div className="flex items-center justify-between pb-4 border-b" style={{ borderColor: colors.lightGray }}>
              <div className="flex items-center space-x-3">
                <div 
                  className="w-10 h-10 rounded-full flex items-center justify-center"
                  style={{ backgroundColor: colors.lightGray }}
                >
                  <span className="text-sm" style={{ color: colors.textSub }}>익명</span>
                </div>
                <div>
                  <p className="text-sm" style={{ color: colors.textDark }}>익명 사용자</p>
                  <p className="text-xs" style={{ color: colors.textSub }}>2025.11.21 14:30</p>
                </div>
              </div>
              <div className="flex flex-wrap gap-2">
                <Badge variant="default" size="sm">#고민상담</Badge>
              </div>
            </div>

            {/* Title */}
            <h1 className="text-xl" style={{ color: colors.textDark }}>
              요즘 너무 힘들어요
            </h1>

            {/* Content */}
            <div className="prose max-w-none">
              <p className="text-sm leading-relaxed" style={{ color: colors.textSub }}>
                부모님을 돌본 지 2년째입니다. 처음에는 괜찮았는데 시간이 갈수록 제 시간이 하나도 없어지고, 
                친구들도 만나지 못하고... 매일 같은 일상의 반복에 우울한 기분이 계속됩니다.
              </p>
              <p className="text-sm leading-relaxed mt-4" style={{ color: colors.textSub }}>
                주변에서는 효자라고 칭찬해주시는데, 정작 제 마음은 너무 힘듭니다. 
                이런 마음을 갖는 제가 나쁜 사람인 것 같아서 더 괴롭습니다.
              </p>
              <p className="text-sm leading-relaxed mt-4" style={{ color: colors.textSub }}>
                비슷한 경험을 하신 분들이 계신가요? 어떻게 이겨내셨는지 듣고 싶습니다.
              </p>
            </div>
          </div>
        </Card>

        {/* Comments Section */}
        <Card variant="elevated" padding="lg">
          <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center space-x-2">
              <MessageCircle size={20} style={{ color: colors.mainGreen2 }} />
              <h2 className="text-lg" style={{ color: colors.textDark }}>
                댓글 {comments.length}
              </h2>
            </div>

            {/* Comment Input */}
            <div className="space-y-3">
              <TextArea
                placeholder="따뜻한 위로와 조언을 남겨주세요"
                value={comment}
                onChange={(e) => setComment(e.target.value)}
                rows={3}
                fullWidth
              />
              <div className="flex justify-end">
                <Button variant="primary" size="sm">
                  댓글 작성
                </Button>
              </div>
            </div>

            {/* Comments List */}
            <div className="space-y-4 pt-4 border-t" style={{ borderColor: colors.lightGray }}>
              {comments.map((comment) => (
                <div 
                  key={comment.id}
                  className="p-4 rounded-xl"
                  style={{ backgroundColor: colors.lightGray }}
                >
                  <div className="flex items-start space-x-3">
                    <div 
                      className="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0"
                      style={{ backgroundColor: colors.white }}
                    >
                      <span className="text-xs" style={{ color: colors.textSub }}>익명</span>
                    </div>
                    <div className="flex-1">
                      <p className="text-sm mb-2" style={{ color: colors.textDark }}>
                        {comment.content}
                      </p>
                      <p className="text-xs" style={{ color: colors.textSub }}>
                        {comment.date}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
