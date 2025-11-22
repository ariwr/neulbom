import React, { useState } from 'react';
import { PenSquare, Search, TrendingUp } from 'lucide-react';
import { Card } from '../components/ui/ThemedCard';
import { Button } from '../components/ui/ThemedButton';
import { Badge } from '../components/ui/Badge';
import { PostCard } from '../components/PostCard';
import { colors } from '../styles/design-tokens';

interface CommunityProps {
  onNavigate?: (page: string) => void;
}

export function Community({ onNavigate }: CommunityProps) {
  const [activeTab, setActiveTab] = useState('all');

  const tabs = [
    { id: 'all', label: '전체' },
    { id: 'popular', label: '인기글' },
    { id: 'recent', label: '최신글' },
  ];

  const posts = [
    {
      title: '노인 돌봄 경험 공유합니다',
      preview: '부모님 돌봄을 시작한 지 3년째입니다. 처음에는 많이 힘들었지만 지금은 여러 복지 서비스를 통해 많은 도움을 받고 있습니다...',
      tags: ['노인돌봄', '경험공유'],
      date: '2025.11.22',
      commentCount: 15,
    },
    {
      title: '장애인 활동지원 서비스 후기',
      preview: '활동지원사님이 오시면서 많은 부담이 줄었어요. 같은 상황의 분들께 도움이 되길 바라며 후기 남깁니다...',
      tags: ['장애인지원', '후기'],
      date: '2025.11.21',
      commentCount: 8,
      hasCrisisFlag: false,
    },
    {
      title: '요즘 너무 힘들어요',
      preview: '돌봄을 하다 보니 제 시간이 없고, 친구들도 만나지 못하고... 우울한 기분이 계속됩니다...',
      tags: ['고민상담'],
      date: '2025.11.21',
      commentCount: 23,
      hasCrisisFlag: true,
    },
    {
      title: '지역별 돌봄센터 정보 정리',
      preview: '서울 지역 돌봄센터 정보를 정리해봤습니다. 필요하신 분들께 도움이 되면 좋겠습니다...',
      tags: ['정보공유', '서울'],
      date: '2025.11.20',
      commentCount: 12,
    },
  ];

  return (
    <div className="min-h-screen pb-20" style={{ backgroundColor: colors.lightGray }}>
      {/* Header */}
      <section 
        className="py-12 px-4"
        style={{
          background: `linear-gradient(135deg, ${colors.pointPink} 0%, ${colors.pointYellow} 100%)`,
        }}
      >
        <div className="max-w-4xl mx-auto">
          <h1 className="text-2xl text-white mb-6 text-center">
            익명 커뮤니티
          </h1>
          
          {/* Search */}
          <Card variant="elevated" padding="sm">
            <div className="flex items-center space-x-3">
              <Search size={20} style={{ color: colors.textSub }} />
              <input
                type="text"
                placeholder="게시글 검색"
                className="flex-1 outline-none text-base"
                style={{ color: colors.textDark }}
              />
            </div>
          </Card>
        </div>
      </section>

      {/* Content */}
      <div className="max-w-4xl mx-auto px-4 py-6">
        {/* Access Info */}
        <Card variant="outlined" padding="md" className="mb-6" style={{ backgroundColor: colors.mainGreen1 + '20' }}>
          <div className="flex items-start space-x-3">
            <Badge variant="level2" size="md">Level 2</Badge>
            <div className="flex-1">
              <p className="text-sm mb-2" style={{ color: colors.textDark }}>
                현재 읽기 전용 모드입니다
              </p>
              <p className="text-xs" style={{ color: colors.textSub }}>
                글 작성을 원하시면 Level 3 인증이 필요합니다
              </p>
            </div>
          </div>
        </Card>

        {/* Tabs & Write Button */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-2">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className="px-4 py-2 rounded-full text-sm transition-all"
                style={{
                  backgroundColor: activeTab === tab.id ? colors.mainGreen2 : colors.lightGray,
                  color: activeTab === tab.id ? colors.white : colors.textSub,
                }}
              >
                {tab.label}
              </button>
            ))}
          </div>
          
          <Button 
            variant="primary" 
            size="sm"
            icon={<PenSquare size={16} />}
            onClick={() => onNavigate?.('post-submit')}
          >
            글쓰기
          </Button>
        </div>

        {/* Hot Topics */}
        <Card variant="elevated" padding="md" className="mb-6">
          <div className="flex items-center space-x-2 mb-3">
            <TrendingUp size={18} style={{ color: colors.pointPink }} />
            <h3 className="text-sm" style={{ color: colors.textDark }}>
              인기 주제
            </h3>
          </div>
          <div className="flex flex-wrap gap-2">
            {['#노인돌봄', '#장애인지원', '#정서지원', '#정보공유', '#후기'].map((tag) => (
              <Badge key={tag} variant="default" size="sm">
                {tag}
              </Badge>
            ))}
          </div>
        </Card>

        {/* Post List */}
        <div className="space-y-4">
          {posts.map((post, index) => (
            <PostCard
              key={index}
              title={post.title}
              preview={post.preview}
              tags={post.tags}
              date={post.date}
              commentCount={post.commentCount}
              hasCrisisFlag={post.hasCrisisFlag}
              onClick={() => onNavigate?.('post-detail')}
            />
          ))}
        </div>

        {/* Pagination */}
        <div className="flex items-center justify-center space-x-2 mt-8">
          {[1, 2, 3, 4, 5].map((page) => (
            <button
              key={page}
              className="w-10 h-10 rounded-full text-sm transition-all"
              style={{
                backgroundColor: page === 1 ? colors.mainGreen2 : colors.lightGray,
                color: page === 1 ? colors.white : colors.textSub,
              }}
            >
              {page}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
