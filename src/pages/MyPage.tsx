import React from 'react';
import { User, Settings, Bookmark, MessageCircle, LogOut } from 'lucide-react';
import { Card } from '../components/ui/ThemedCard';
import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/ThemedButton';
import { colors } from '../styles/design-tokens';
import type { Post } from '../services/postService';
import type { Welfare } from '../services/welfareService';
import type { Page } from '../types/page';

interface MyPageProps {
  onNavigate?: (page: Page) => void;
  bookmarkedWelfares: Welfare[];
  bookmarkedPosts: Post[];      // 게시글 북마크 목록
  onSelectWelfare?: (id: number) => void;
  onSelectPost?: (id: number) => void;    // 게시글 클릭 콜백
}

// MyPage.tsx 안쪽, export 위/아래 아무 데나
interface BookmarkSectionProps<T> {
  title: string;
  icon: React.ReactNode;
  items: T[];
  emptyText: string;
  onViewAll?: () => void;
  onItemClick?: (item: T) => void;
  getPrimaryText: (item: T) => string;
  getSecondaryText?: (item: T) => string | undefined;
}

function BookmarkSection<T>({
  title,
  icon,
  items,
  emptyText,
  onViewAll,
  onItemClick,
  getPrimaryText,
  getSecondaryText,
}: BookmarkSectionProps<T>) {
  return (
    <Card variant="elevated" padding="lg" className="mb-6">
      <div className="space-y-4">
        {/* 헤더 */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            {icon}
            <h2 className="text-lg" style={{ color: colors.textDark }}>
              {title}
            </h2>
          </div>
          {onViewAll && (
            <button
              onClick={onViewAll}
              className="text-sm hover:opacity-70 transition-opacity"
              style={{ color: colors.mainGreen2 }}
            >
              전체보기
            </button>
          )}
        </div>

        {/* 내용 */}
        {items.length === 0 ? (
          <p className="text-xs" style={{ color: colors.textSub }}>
            {emptyText}
          </p>
        ) : (
          <div className="space-y-2">
            {items.map((item, index) => {
              const primary = getPrimaryText(item);
              const secondary = getSecondaryText?.(item);

              return (
                <div
                  key={index}
                  className="p-3 rounded-lg flex items-center justify-between cursor-pointer hover:opacity-80 transition-opacity"
                  style={{ backgroundColor: colors.lightGray }}
                  onClick={() => onItemClick?.(item)}
                >
                  <span className="text-sm" style={{ color: colors.textDark }}>
                    {primary}
                  </span>
                  {secondary && (
                    <span className="text-xs" style={{ color: colors.textSub }}>
                      {secondary}
                    </span>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>
    </Card>
  );
}

export function MyPage({
  onNavigate,
  bookmarkedWelfares,
  bookmarkedPosts,
  onSelectWelfare,
  onSelectPost,
 }: MyPageProps) {
  const [profile, setProfile] = React.useState({
    name: '김늘봄',
    age: '35세',
    region: '서울특별시 강남구',
    target: '부모님',
  });

  const [isEditing, setIsEditing] = React.useState(false);
  const [editForm, setEditForm] = React.useState(profile);
  const [isSettingsOpen, setIsSettingsOpen] = React.useState(false);

  return (
    <div className="min-h-screen pb-20" style={{ backgroundColor: colors.lightGray }}>
      {/* Header */}
      <section 
        className="py-12 px-4"
        style={{
          background: `linear-gradient(135deg, ${colors.mainGreen1} 0%, ${colors.mainGreen2} 100%)`,
        }}
      >
        <div className="max-w-4xl mx-auto text-center">
          <div 
            className="w-20 h-20 rounded-full mx-auto mb-4 flex items-center justify-center"
            style={{ backgroundColor: colors.white }}
          >
            <User size={32} style={{ color: colors.mainGreen2 }} />
          </div>
          <h1 className="text-xl text-white mb-2">
            김늘봄 님
          </h1>
        </div>
      </section>

      {/* Content */}
      <div className="max-w-4xl mx-auto px-4 -mt-8">
        {/* Profile Info */}
        <Card variant="elevated" padding="lg" className="mb-6">
          <div className="space-y-4">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg" style={{ color: colors.textDark }}>
                프로필 정보
              </h2>
              <button
                className="text-sm hover:opacity-70 transition-opacity"
                style={{ color: colors.mainGreen2 }}
                onClick={() => {
                  setEditForm(profile);   // 현재 값으로 폼 초기화
                  setIsEditing(true);
                }}  
              >
                수정
              </button>
            </div>

            {isEditing ? (
              // 수정 모드
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-xs mb-1" style={{ color: colors.textSub }}>
                      이름
                    </p>
                    <input
                      className="w-full px-3 py-2 rounded-lg text-sm border"
                      style={{ borderColor: colors.lightGray, color: colors.textDark }}
                      value={editForm.name}
                      onChange={(e) =>
                        setEditForm((prev) => ({ ...prev, name: e.target.value }))
                      }
                    />
                  </div>
                  <div>
                    <p className="text-xs mb-1" style={{ color: colors.textSub }}>
                      나이
                    </p>
                    <input
                      className="w-full px-3 py-2 rounded-lg text-sm border"
                      style={{ borderColor: colors.lightGray, color: colors.textDark }}
                      value={editForm.age}
                      onChange={(e) =>
                        setEditForm((prev) => ({ ...prev, age: e.target.value }))
                      }
                    />
                  </div>
                  <div>
                    <p className="text-xs mb-1" style={{ color: colors.textSub }}>
                      거주 지역
                    </p>
                    <input
                      className="w-full px-3 py-2 rounded-lg text-sm border"
                      style={{ borderColor: colors.lightGray, color: colors.textDark }}
                      value={editForm.region}
                      onChange={(e) =>
                        setEditForm((prev) => ({ ...prev, region: e.target.value }))
                      }
                    />
                  </div>
                  <div>
                    <p className="text-xs mb-1" style={{ color: colors.textSub }}>
                      돌봄 대상
                    </p>
                    <input
                      className="w-full px-3 py-2 rounded-lg text-sm border"
                      style={{ borderColor: colors.lightGray, color: colors.textDark }}
                      value={editForm.target}
                      onChange={(e) =>
                        setEditForm((prev) => ({ ...prev, target: e.target.value }))
                      }
                    />
                  </div>
                </div>

                <div className="flex justify-end space-x-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      setIsEditing(false);
                      setEditForm(profile); // 원래 값으로 되돌리기
                    }}
                  >
                    취소
                  </Button>
                  <Button
                    variant="primary"
                    size="sm"
                    onClick={() => {
                      setProfile(editForm);  // 실제 프로필 업데이트
                      setIsEditing(false);
                    }}
                  >
                    저장
                  </Button>
                </div>
              </div>
            ) : (
              //  보기 모드
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-xs mb-1" style={{ color: colors.textSub }}>
                    이름
                  </p>
                  <p className="text-sm" style={{ color: colors.textDark }}>
                    {profile.name}
                  </p>
                </div>
                <div>
                  <p className="text-xs mb-1" style={{ color: colors.textSub }}>
                    나이
                  </p>
                  <p className="text-sm" style={{ color: colors.textDark }}>
                    {profile.age}
                  </p>
                </div>
                <div>
                  <p className="text-xs mb-1" style={{ color: colors.textSub }}>
                    거주 지역
                  </p>
                  <p className="text-sm" style={{ color: colors.textDark }}>
                    {profile.region}
                  </p>
                </div>
                <div>
                  <p className="text-xs mb-1" style={{ color: colors.textSub }}>
                    돌봄 대상
                  </p>
                  <p className="text-sm" style={{ color: colors.textDark }}>
                    {profile.target}
                  </p>
                </div>
              </div>
            )}
          </div>
        </Card>

        {/* Bookmarked Welfare */}
        <BookmarkSection<Welfare>
          title="북마크한 복지 정보"
          icon={<Bookmark size={18} style={{ color: colors.mainGreen2 }} />}
          items={bookmarkedWelfares}
          emptyText="아직 북마크한 복지 정보가 없습니다."
          onViewAll={() => onNavigate?.('welfare')}
          onItemClick={(item) => {
            onSelectWelfare?.(item.id);
            onNavigate?.('welfare-detail');
          }}
          getPrimaryText={(item) => item.title}
          // Welfare 타입에 date가 있으면 이렇게:
          // getSecondaryText={(item) => item.date}
          getSecondaryText={() => undefined}
        />

        <BookmarkSection<Post>
          title="북마크한 게시글"
          icon={<MessageCircle size={18} style={{ color: colors.mainGreen2 }} />}
          items={bookmarkedPosts}
          emptyText="아직 북마크한 게시글이 없습니다."
          onViewAll={() => onNavigate?.('community')}
          onItemClick={(item) => {
            onSelectPost?.(item.id);
            onNavigate?.('post-detail');
          }}
          getPrimaryText={(item) => item.title}
          getSecondaryText={(item) => item.date}  // Post 타입에 date 필드 있다고 가정
        />
        
        {/* Settings & Logout → 설정 내부에 4개 메뉴 포함 */}
        <Card variant="elevated" padding="lg">
          <div className="space-y-3">
            {/* 설정 헤더 버튼 (펼치기/접기) */}
            <button
              className="w-full flex items-center justify-between p-3 rounded-lg hover:bg-opacity-50 transition-all"
              style={{ backgroundColor: colors.lightGray }}
              onClick={() => setIsSettingsOpen(prev => !prev)}
            >
              <div className="flex items-center space-x-3">
                <Settings size={18} style={{ color: colors.textSub }} />
                <span className="text-sm" style={{ color: colors.textDark }}>
                  설정
                </span>
              </div>
              <span className="text-xs" style={{ color: colors.textSub }}>
                {isSettingsOpen ? '접기' : '펼치기'}
              </span>
            </button>

            {/* 설정 상세 메뉴들 */}
            {isSettingsOpen && (
              <div className="space-y-2">
                {/* 1. 고객센터 문의 */}
                <button
                  className="w-full flex items-center justify-between p-3 rounded-lg hover:bg-opacity-60 transition-all"
                  style={{ backgroundColor: colors.lightGray }}
                  onClick={() => {
                    // 나중에 실제 문의 페이지/채팅 페이지로 이동하도록 교체
                    onNavigate?.('chat'); // 예시: 챗봇으로 연결
                  }}
                >
                  <span className="text-sm" style={{ color: colors.textDark }}>
                    고객센터 문의
                  </span>
                </button>

                {/* 2. 상담전화 가이드 */}
                <button
                  className="w-full flex items-center justify-between p-3 rounded-lg hover:bg-opacity-60 transition-all"
                  style={{ backgroundColor: colors.lightGray }}
                  onClick={() => {
                    // 예시: 안내 모달/페이지 연결
                    // 현재는 자리만 잡아두기
                    window.alert('상담전화: 0000-0000 (예시)');
                  }}
                >
                  <span className="text-sm" style={{ color: colors.textDark }}>
                    상담전화 가이드
                  </span>
                </button>

                {/* 3. 비밀번호 변경 */}
                <button
                  className="w-full flex items-center justify-between p-3 rounded-lg hover:bg-opacity-60 transition-all"
                  style={{ backgroundColor: colors.lightGray }}
                  onClick={() => {
                    // 나중에 비밀번호 변경 화면이 생기면 그 페이지로 이동
                    // 지금은 로그인 화면으로 보낸다든지 원하는 대로 임시 처리
                    onNavigate?.('login');
                  }}
                >
                  <span className="text-sm" style={{ color: colors.textDark }}>
                    비밀번호 변경
                  </span>
                </button>

                {/* 4. 로그아웃 */}
                <button
                  className="w-full flex items-center justify-between p-3 rounded-lg hover:bg-opacity-60 transition-all"
                  style={{ backgroundColor: colors.lightGray }}
                  onClick={() => {
                    // 토큰/세션 삭제 로직이 나중에 들어올 자리
                    onNavigate?.('login');
                  }}
                >
                  <div className="flex items-center space-x-3">
                    <LogOut size={18} style={{ color: colors.error }} />
                    <span className="text-sm" style={{ color: colors.error }}>
                      로그아웃
                    </span>
                  </div>
                </button>
              </div>
            )}
          </div>
        </Card>
      </div>
    </div>
  );
}
