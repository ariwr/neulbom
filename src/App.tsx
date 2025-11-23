// App.tsx
import React, { useEffect, useState, useCallback, useMemo } from 'react';
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
import { getAuthToken, setAuthToken } from './config/api';
import { logout as authLogout } from './services/authService';

import {
  fetchPosts,
  createPost, // createPost import 추가
  toggleBookmark,
  toggleLike,
  type Post,
} from './services/postService';

import type { Welfare as WelfareType } from './services/welfareService';

export default function App() {
  const [currentPage, setCurrentPage] = useState<Page>('home');
  const [isLoggedIn, setIsLoggedIn] = useState<boolean>(() => {
    // 초기 로그인 상태 확인
    return !!getAuthToken();
  });

  // setState를 한번 감싼 핸들러 (메모이제이션)
  const handleNavigate = useCallback((page: Page) => {
    // 커뮤니티 관련 페이지는 로그인 필수
    const communityPages: Page[] = ['community', 'post-detail', 'post-submit'];
    if (communityPages.includes(page)) {
      if (!isLoggedIn) {
        alert('커뮤니티를 이용하려면 로그인이 필요합니다.');
        // 로그인 페이지로 이동하지 않고 현재 페이지 유지
        return;
      }
    }
    setCurrentPage(page);
  }, [isLoggedIn]);

  // 로그인 상태 업데이트 함수 (메모이제이션)
  const updateLoginStatus = useCallback((token?: string) => {
    // 인자로 토큰이 전달되면 즉시 사용, 아니면 localStorage 확인
    const currentToken = token || getAuthToken();
    
    // 개발 모드에서만 로깅
    if (import.meta.env.DEV) {
      console.log('로그인 상태 업데이트:', currentToken ? '로그인됨' : '로그인 안됨', token ? '(토큰 전달됨)' : '(localStorage에서 읽음)');
    }
    
    // 토큰이 전달된 경우 localStorage에도 저장 (이중 안전장치)
    if (token) {
      setAuthToken(token);
      if (import.meta.env.DEV) {
        console.log('토큰을 localStorage에 저장 완료');
      }
    }
    
    setIsLoggedIn(!!currentToken);
  }, []);

  // 로그아웃 핸들러 (메모이제이션)
  const handleLogout = useCallback(() => {
    authLogout();
    setIsLoggedIn(false);
    setCurrentPage('home');
  }, []);

  // 커뮤니티 상태
  const [posts, setPosts] = useState<Post[]>([]);
  const [selectedPostId, setSelectedPostId] = useState<number | null>(null);

   // 앱 시작 시 게시글 불러오기 (로그인된 경우에만)
  useEffect(() => {
    // 토큰을 직접 확인하여 더 확실하게 검증
    const token = getAuthToken();
    if (isLoggedIn && token) {
      // 약간의 지연을 주어 상태 업데이트가 완료되도록 함
      const timer = setTimeout(() => {
        fetchPosts()
          .then((data) => {
            setPosts(data);
          })
          .catch((error: any) => {
            // 개발 모드에서만 로깅
            if (import.meta.env.DEV) {
              console.error('게시글 불러오기 실패:', error);
            }
            // 401 에러인 경우 로그인 상태를 false로 변경
            if (error.status === 401) {
              if (import.meta.env.DEV) {
                console.warn('인증 실패, 로그인 상태를 false로 변경');
              }
              setIsLoggedIn(false);
            }
          });
      }, 100);
      
      return () => clearTimeout(timer);
    } else {
      // 로그인하지 않은 경우 빈 배열로 설정
      setPosts([]);
    }
  }, [isLoggedIn]);

  // 어떤 복지를 선택했는지 (상세 페이지용)
  const [selectedWelfareId, setSelectedWelfareId] = useState<number | null>(null);

  // 어떤 것들이 북마크 됐는지 id 배열로 관리
  const [bookmarkedWelfareIds, setBookmarkedWelfareIds] = useState<number[]>([]);

  // 북마크 게시글 관리 (메모이제이션)
  const bookmarkedPosts = useMemo(() => posts.filter((p) => p.isBookmarked), [posts]);

  // 북마크 토글 핸들러 (메모이제이션)
  const toggleWelfareBookmark = useCallback((id: number) => {
    setBookmarkedWelfareIds((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id],
    );
  }, []);

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

  // 마이페이지에 넘길 북마크된 복지 목록 (빈 배열로 초기화, 나중에 API로 가져올 수 있음)
  const bookmarkedWelfares: WelfareType[] = [];

  // PostSubmit에서 사용
  const addPost = async (data: { title: string; preview: string; category: 'info' | 'counsel' | 'free' }) => {
    try {
      // 로그인 확인 (isLoggedIn state 사용)
      if (!isLoggedIn) {
        alert('게시글을 작성하려면 로그인이 필요합니다.');
        handleNavigate('login');
        return;
      }

      // API 호출로 게시글 생성
      const newPost = await createPost(data.title, data.preview, data.category);
      // 상태 업데이트 (최신글이 위로 오도록)
      setPosts((prev) => [newPost, ...prev]);
    } catch (error: any) {
      // 개발 모드에서만 로깅
      if (import.meta.env.DEV) {
        console.error('게시글 생성 실패:', error);
      }
      
      // 401 Unauthorized 에러 처리
      if (error.status === 401) {
        alert('로그인이 필요합니다. 로그인 페이지로 이동합니다.');
        setIsLoggedIn(false);
        handleNavigate('login');
        return;
      }
      
      // 기타 에러 처리
      const errorMessage = error.message || '게시글 작성에 실패했습니다.';
      alert(errorMessage);
    }
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

  // 복지 카드 클릭 시: id 저장 + 상세 페이지로 이동 (메모이제이션)
  const handleSelectWelfare = useCallback((id: number) => {
    setSelectedWelfareId(id);
    handleNavigate('welfare-detail');
  }, []);

  const renderPage = () => {
    switch (currentPage) {
      case 'login':
        return <Login onNavigate={handleNavigate} onLoginSuccess={updateLoginStatus} />;

      case 'signup':
        return <Signup onNavigate={handleNavigate} onSignupSuccess={updateLoginStatus} />;

      case 'home':
        return (
          <>
            <Navbar 
              activePage="home" 
              onNavigate={handleNavigate}
              isLoggedIn={isLoggedIn}
              onLoginClick={() => handleNavigate('login')}
              onLogoutClick={handleLogout}
              onCommunityClick={handleNavigate}
            />
            <Home
              onNavigate={handleNavigate}
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
            <Navbar 
              activePage="chat" 
              onNavigate={handleNavigate}
              isLoggedIn={isLoggedIn}
              onLoginClick={() => handleNavigate('login')}
              onLogoutClick={handleLogout}
              onCommunityClick={handleNavigate}
            />
            <Chat />
          </>
        );

      case 'welfare':
        return (
          <>
            <Navbar 
              activePage="welfare" 
              onNavigate={handleNavigate}
              isLoggedIn={isLoggedIn}
              onLoginClick={() => handleNavigate('login')}
              onLogoutClick={handleLogout}
            />
            <Welfare
              onNavigate={handleNavigate}
              bookmarkedIds={bookmarkedWelfareIds}
              onToggleBookmark={toggleWelfareBookmark}
              // ⭐ 목록 화면에서도 상세 이동 콜백
              onSelectWelfare={handleSelectWelfare}
            />
          </>
        );

      case 'welfare-detail': {
        // 선택된 복지 ID가 없으면 복지 목록으로 리다이렉트
        if (!selectedWelfareId) {
          return (
            <>
              <Navbar 
              activePage="welfare" 
              onNavigate={handleNavigate}
              isLoggedIn={isLoggedIn}
              onLoginClick={() => handleNavigate('login')}
              onLogoutClick={handleLogout}
              onCommunityClick={handleNavigate}
            />
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

        const isBookmarked = bookmarkedWelfareIds.includes(selectedWelfareId);

        return (
          <>
            <Navbar 
              activePage="welfare" 
              onNavigate={handleNavigate}
              isLoggedIn={isLoggedIn}
              onLoginClick={() => handleNavigate('login')}
              onLogoutClick={handleLogout}
              onCommunityClick={handleNavigate}
            />
            <WelfareDetail
              onNavigate={handleNavigate}
              welfareId={selectedWelfareId}
              isBookmarked={isBookmarked}
              onToggleBookmark={() =>
                toggleWelfareBookmark(selectedWelfareId)
              }
            />
          </>
        );
      }

      case 'community':
        return (
          <>
            <Navbar 
              activePage="community" 
              onNavigate={handleNavigate}
              isLoggedIn={isLoggedIn}
              onLoginClick={() => handleNavigate('login')}
              onLogoutClick={handleLogout}
              onCommunityClick={handleNavigate}
            />
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
            <Navbar 
              activePage="community" 
              onNavigate={handleNavigate}
              isLoggedIn={isLoggedIn}
              onLoginClick={() => handleNavigate('login')}
              onLogoutClick={handleLogout}
              onCommunityClick={handleNavigate}
            />
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
            <Navbar 
              activePage="community" 
              onNavigate={handleNavigate}
              isLoggedIn={isLoggedIn}
              onLoginClick={() => handleNavigate('login')}
              onLogoutClick={handleLogout}
              onCommunityClick={handleNavigate}
            />
            <PostSubmit
              onNavigate={handleNavigate}
              onSubmit={(data) => {
                addPost(data);
                handleNavigate('community');
              }}
              isLoggedIn={isLoggedIn}
            />
          </>
        );

      case 'mypage':
        return (
          <>
            <Navbar 
              activePage="mypage" 
              onNavigate={handleNavigate}
              isLoggedIn={isLoggedIn}
              onLoginClick={() => handleNavigate('login')}
              onLogoutClick={handleLogout}
              onCommunityClick={handleNavigate}
            />
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
            <Navbar 
              activePage="home" 
              onNavigate={handleNavigate}
              isLoggedIn={isLoggedIn}
              onLoginClick={() => handleNavigate('login')}
              onLogoutClick={handleLogout}
              onCommunityClick={handleNavigate}
            />
            <AdminVerification />
          </>
        );

      default:
        return (
          <>
            <Navbar 
              activePage="home" 
              onNavigate={handleNavigate}
              isLoggedIn={isLoggedIn}
              onLoginClick={() => handleNavigate('login')}
              onLogoutClick={handleLogout}
              onCommunityClick={handleNavigate}
            />
            <Home
              onNavigate={handleNavigate}
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