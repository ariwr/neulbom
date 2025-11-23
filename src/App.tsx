// App.tsx
import React, { useEffect, useState } from 'react';
import { Navbar } from './components/layout/Navbar';
import { Login } from './pages/Login';
import { Signup } from './pages/Signup';
import { Home } from './pages/Home';
import { Chat } from './pages/Chat';
import { Welfare } from './pages/Welfare';
import { WelfareDetail } from './pages/WelfareDetail';
import { Community } from './pages/Community';
import { PostDetail } from './pages/PostDetail';
import { PostSubmit } from './pages/PostSubmit';
import { MyPage } from './pages/MyPage';
import { AdminVerification } from './pages/AdminVerification';
import type { Page } from './types/page'

import {
  fetchPosts,
  toggleBookmark,
  toggleLike,
  initialComments,
  type Post,
} from './services/postService';

import {
  initialWelfares,
  type Welfare as WelfareType,
} from './services/welfareService';

export default function App() {
  const [currentPage, setCurrentPage] = useState<Page>('login');

  // setState를 한번 감싼 핸들러
  const handleNavigate = (page: Page) => {
    setCurrentPage(page);
  }

  // 커뮤니티 상태
  const [posts, setPosts] = useState<Post[]>([]);
  const [selectedPostId, setSelectedPostId] = useState<number | null>(null);

   // 앱 시작 시 게시글 불러오기 (나중에 API로 교체)
  useEffect(() => {
    fetchPosts().then((data) => {
      setPosts(data);
    });
  }, []);

  // 복지 목록 (나중에 여기를 API fetch 결과로 교체)
  const [welfares] = useState<WelfareType[]>(initialWelfares);

  // 어떤 복지를 선택했는지 (상세 페이지용)
  const [selectedWelfareId, setSelectedWelfareId] = useState<number | null>(null);

  // 어떤 것들이 북마크 됐는지 id 배열로 관리
  const [bookmarkedWelfareIds, setBookmarkedWelfareIds] = useState<number[]>([]);

  // 북마크 게시글 관리
  const bookmarkedPosts = posts.filter((p) => p.isBookmarked);

  // 북마크 토글 핸들러
  const toggleWelfareBookmark = (id: number) => {
    setBookmarkedWelfareIds((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id],
    );
  };

  // 게시글 좋아요 토글 (서비스 + 상태 반영)
  const handleTogglePostLike = async (postId: number) => {
    const updated = await toggleLike(postId); // postService에서 토글 후 업데이트 된 데이터 반환
    if (!updated) return;

    setPosts((prev) =>
      prev.map((p) => (p.id === postId ? updated : p)),
    );
  };

  // 게시글 북마크 토글 (서비스 + 상태 반영)
  const handleTogglePostBookmark = async (postId: number) => {
    const updated = await toggleBookmark(postId);
    if (!updated) return;

    setPosts((prev) =>
      prev.map((p) => (p.id === postId ? updated : p)),
    );
  };

  // 마이페이지에 넘길 북마크된 복지 목록
  const bookmarkedWelfares = welfares.filter((w) =>
    bookmarkedWelfareIds.includes(w.id),
  );

  // PostSubmit에서 사용
  const addPost = (data: { title: string; preview: string }) => {
    const nextId = posts.length ? posts[posts.length - 1].id + 1 : 1;

    const today = new Date();
    const dateString = `${today.getFullYear()}.${String(
      today.getMonth() + 1,
    ).padStart(2, '0')}.${String(today.getDate()).padStart(2, '0')}`;

    const newPost: Post = {
      id: nextId,
      title: data.title,
      preview: data.preview,
      date: dateString,
      commentCount: 0,
      comments: initialComments,

      // ✅ 새로 추가된 필드들 (postService의 Post 타입과 맞춰야 함)
      hasCrisisFlag: false,
      category: 'free',       // 기본값: 자유게시판 (UI에서 선택하게 바꿔도 됨)
      likeCount: 0,
      isLiked: false,
      isBookmarked: false,
    };

    setPosts((prev) => [newPost, ...prev]);
  };

  const addComment = (postId: number, content: string) => {
    const now = new Date();
    const date = `${now.getFullYear()}.${now.getMonth() + 1}.${now.getDate()} ${now.getHours()}:${now.getMinutes()}`;

    setPosts((prev) =>
      prev.map((post) =>
        post.id === postId
          ? {
              ...post,
              comments: [...post.comments, { id: Date.now(), content, date }],
              commentCount: post.commentCount + 1,
            }
          : post,
      ),
    );
  };

  // 복지 카드 클릭 시: id 저장 + 상세 페이지로 이동
  const handleSelectWelfare = (id: number) => {
    setSelectedWelfareId(id);
    handleNavigate('welfare-detail');
  };

  const renderPage = () => {
    switch (currentPage) {
      case 'login':
        return <Login onNavigate={handleNavigate} />;

      case 'signup':
        return <Signup onNavigate={handleNavigate} />;

      case 'home':
        return (
          <>
            <Navbar activePage="home" onNavigate={handleNavigate} />
            <Home
              onNavigate={handleNavigate}
              welfares={welfares}
              bookmarkedIds={bookmarkedWelfareIds}
              onToggleBookmark={toggleWelfareBookmark}
              // ⭐ 상세 이동용 콜백 추가
              onSelectWelfare={handleSelectWelfare}
            />
          </>
        );

      case 'chat':
        return (
          <>
            <Navbar activePage="chat" onNavigate={handleNavigate} />
            <Chat />
          </>
        );

      case 'welfare':
        return (
          <>
            <Navbar activePage="welfare" onNavigate={handleNavigate} />
            <Welfare
              onNavigate={handleNavigate}
              welfares={welfares}
              bookmarkedIds={bookmarkedWelfareIds}
              onToggleBookmark={toggleWelfareBookmark}
              // ⭐ 목록 화면에서도 상세 이동 콜백
              onSelectWelfare={handleSelectWelfare}
            />
          </>
        );

      case 'welfare-detail': {
        // 선택된 복지 데이터 찾기
        const selectedWelfare = welfares.find(
          (w) => w.id === selectedWelfareId,
        ) || null;

        if (!selectedWelfare) {
          // 새로고침 등으로 id가 없는 경우 안전 처리
          return (
            <>
              <Navbar activePage="welfare" onNavigate={handleNavigate} />
              <div className="max-w-4xl mx-auto p-4">
                <p>선택된 복지 정보가 없습니다.</p>
                <button
                  className="mt-4 underline"
                  onClick={() => handleNavigate('welfare')}
                >
                  복지 목록으로 돌아가기
                </button>
              </div>
            </>
          );
        }

        const isBookmarked = bookmarkedWelfareIds.includes(selectedWelfare.id);

        return (
          <>
            <Navbar activePage="welfare" onNavigate={handleNavigate} />
            <WelfareDetail
              onNavigate={handleNavigate}
              // data={selectedWelfare}              // ✅ 실제 선택된 데이터 전달
              isBookmarked={isBookmarked}         // ✅ 현재 북마크 여부
              onToggleBookmark={() =>
                toggleWelfareBookmark(selectedWelfare.id)
              }                                   // ✅ 이 복지에 대한 북마크 토글
            />
          </>
        );
      }

      case 'community':
        return (
          <>
            <Navbar activePage="community" onNavigate={handleNavigate} />
            <Community
              posts={posts}
              onToggleBookmark={handleTogglePostBookmark}
              onToggleLike={handleTogglePostLike}
              onNavigate={handleNavigate}
              onPostClick={(id) => {
                setSelectedPostId(id);
                handleNavigate('post-detail');
              }}
            />
          </>
        );

      case 'post-detail': {
        const post = posts.find((p) => p.id === selectedPostId) || null;
        return (
          <>
            <Navbar activePage="community" onNavigate={handleNavigate} />
            <PostDetail
              onNavigate={handleNavigate}
              post={post}
              onAddComment={addComment}
              onToggleLike={handleTogglePostLike}
              onToggleBookmark={handleTogglePostBookmark}
            />
          </>
        );
      }

      case 'post-submit':
        return (
          <>
            <Navbar activePage="community" onNavigate={handleNavigate} />
            <PostSubmit
              onNavigate={handleNavigate}
              onSubmit={(data) => {
                addPost(data);
                handleNavigate('community');
              }}
            />
          </>
        );

      case 'mypage':
        return (
          <>
            <Navbar activePage="mypage" onNavigate={handleNavigate} />
            <MyPage
              onNavigate={handleNavigate}
              bookmarkedWelfares={bookmarkedWelfares}
              onSelectWelfare={handleSelectWelfare}
              bookmarkedPosts={bookmarkedPosts}
              onSelectPost={(id) => {
                setSelectedPostId(id);
                handleNavigate('post-detail');
              }}
            />
          </>
        );

      case 'admin':
        return (
          <>
            <Navbar activePage="home" onNavigate={handleNavigate} />
            <AdminVerification />
          </>
        );

      default:
        return (
          <>
            <Navbar activePage="home" onNavigate={handleNavigate} />
            <Home
              onNavigate={handleNavigate}
              welfares={welfares}
              bookmarkedIds={bookmarkedWelfareIds}
              onToggleBookmark={toggleWelfareBookmark}
              onSelectWelfare={handleSelectWelfare}
            />
          </>
        );
    }
  };

  return <div className="min-h-screen">{renderPage()}</div>;
}