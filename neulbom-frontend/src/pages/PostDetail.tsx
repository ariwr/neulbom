import React, { useState, useEffect } from 'react';
import { ChevronLeft, AlertTriangle, MessageCircle, MoreVertical, Edit, Trash2 } from 'lucide-react';
import { Card } from '../components/ui/ThemedCard';
import { Button } from '../components/ui/ThemedButton';
import { Badge } from '../components/ui/Badge';
import { TextArea } from '../components/ui/ThemedTextArea';
import { colors } from '../styles/design-tokens';
import type { Post } from '../services/postService'
import type { Page } from '../types/page';
import { getProfile } from '../services/authService';

interface PostDetailProps {
  post: Post | null;
  onNavigate: (page: Page) => void;
  onAddComment: (postId: number, content: string) => void;
  onToggleLike?: (postId: number) => void;
  onToggleBookmark?: (postId: number) => void;
}

export function PostDetail({ post, onNavigate, onAddComment, onToggleLike, onToggleBookmark }: PostDetailProps) {
  const [comment, setComment] = useState('');
  const [currentUserId, setCurrentUserId] = useState<number | null>(null);
  const [showMenu, setShowMenu] = useState(false);

  useEffect(() => {
    getProfile().then(user => {
      setCurrentUserId(user.id);
    }).catch(() => {
      // 로그인하지 않은 경우 무시
    });
  }, []);

  const isMine = post?.authorId === currentUserId;

  // post가 없을 시
  if (!post) {
    return (
      <div className="min-h-screen pb-20" style={{ backgroundColor: colors.lightGray }}>
        <div className="max-w-4xl mx-auto px-4 py-8">
          <button
            onClick={() => onNavigate('community')}
            className="mb-4 underline"
            title="커뮤니티로 돌아가기"
            aria-label="커뮤니티로 돌아가기"
          >
            커뮤니티로 돌아가기
          </button>
          <p>게시글을 찾을 수 없습니다.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen pb-20" style={{ backgroundColor: colors.lightGray }}>
      {/* Header */}
      <div className="bg-white border-b sticky top-16 z-30" style={{ borderColor: colors.lightGray }}>
        <div className="max-w-4xl mx-auto px-4 py-4">
          <button
            onClick={() => onNavigate('community')}
            className="flex items-center space-x-2 hover:opacity-70 transition-opacity"
            style={{ color: colors.textDark }}
            title="목록으로 돌아가기"
            aria-label="목록으로 돌아가기"
          >
            <ChevronLeft size={20} />
            <span>목록으로</span>
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-4xl mx-auto px-4 py-8">
        {/* Crisis Alert Banner */}
        {post.hasCrisisFlag && (
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
        )}

        {/* Post Content */}
        <Card variant="elevated" padding="lg" className="mb-6">
          <div className="space-y-4">
            {/* Meta */}
            <div
              className="flex items-center justify-between pb-4 border-b"
              style={{ borderColor: colors.lightGray }}
            >
              {/* Left: 익명 사용자 */}
              <div className="flex items-center space-x-3">
                <div
                  className="w-10 h-10 rounded-full flex items-center justify-center"
                  style={{ backgroundColor: colors.lightGray }}
                >
                  <span className="text-sm" style={{ color: colors.textSub }}>
                    익명
                  </span>
                </div>
                <div>
                  <p className="text-sm" style={{ color: colors.textDark }}>
                    익명 사용자
                  </p>
                  <p className="text-xs" style={{ color: colors.textSub }}>
                    {post.date}
                  </p>
                </div>
              </div>

              {/* Right: 좋아요/북마크 */}
              <div className="flex items-center space-x-4">
                {/* 좋아요 */}
                <button
                  onClick={() => onToggleLike?.(post.id)}
                  className="flex items-center space-x-1 hover:opacity-70 transition"
                  title={post.isLiked ? "좋아요 취소" : "좋아요"}
                  aria-label={post.isLiked ? "좋아요 취소" : "좋아요"}
                >
                  <svg
                    width="18"
                    height="18"
                    viewBox="0 0 24 24"
                    fill={post.isLiked ? colors.pointPink : "none"}
                    stroke={post.isLiked ? colors.pointPink : colors.textSub}
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  >
                    <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 1 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" />
                  </svg>
                  <span
                    className="text-sm"
                    style={{ color: post.isLiked ? colors.pointPink : colors.textSub }}
                  >
                    {post.likeCount}
                  </span>
                </button>

                {/* 북마크 */}
                <button
                  onClick={() => onToggleBookmark?.(post.id)}
                  className="hover:opacity-70 transition"
                  title={post.isBookmarked ? "북마크 취소" : "북마크"}
                  aria-label={post.isBookmarked ? "북마크 취소" : "북마크"}
                >
                  <svg
                    width="18"
                    height="18"
                    viewBox="0 0 24 24"
                    fill={post.isBookmarked ? colors.mainGreen2 : "none"}
                    stroke={post.isBookmarked ? colors.mainGreen2 : colors.textSub}
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  >
                    <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z" />
                  </svg>
                </button>
              </div>
            </div>

            {/* Title */}
            <h1 className="text-xl" style={{ color: colors.textDark }}>
              {post.title}
            </h1>

            {/* Content */}
            <div className="prose max-w-none">
              <p className="text-sm leading-relaxed" style={{ color: colors.textSub }}>
                {post.preview}
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
                댓글 {post.comments?.length || post.commentCount || 0}   
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
                <Button variant="primary"
                  size="sm"
                  onClick={() => {
                    if (!comment.trim()) return;
                    onAddComment(post.id, comment);
                    setComment('');
                  }}
                >
                  댓글 작성
                </Button>
              </div>
            </div>

            {/* Comments List */}
            <div className="space-y-4 pt-4 border-t" style={{ borderColor: colors.lightGray }}>
              {(post.comments && post.comments.length > 0) ? (
                post.comments.map((comment) => (
                  <div 
                    key={comment.id}
                    className="p-4 rounded-xl"
                    style={{ backgroundColor: colors.lightGray }}
                  >
                    <div className="flex items-start space-x-3">
                      {/* 익명 이름 표시 제거 */}
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
                ))
              ) : (
                <p className="text-sm text-center py-8" style={{ color: colors.textSub }}>
                  아직 댓글이 없습니다. 첫 번째 댓글을 남겨보세요!
                </p>
              )}
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
