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
  fetchPostDetail,
  createPost, // createPost import 추가
  toggleBookmark,
  toggleLike,
  type Post,
} from './services/postService';

import type { Welfare as WelfareType } from './services/welfareService';
import { login } from './services/authService';
import { getWelfareDetail } from './services/welfareService';

export default function App() {
  const [currentPage, setCurrentPage] = useState<Page>('home');
  // 로그아웃 상태로 시작
  const [isLoggedIn, setIsLoggedIn] = useState<boolean>(() => {
    // localStorage에 토큰이 있으면 로그인 상태로 시작
    return !!getAuthToken();
  });

  // 페이지 변경 시 로그인 상태 동기화 (특히 로그인 후 home으로 이동할 때)
  useEffect(() => {
    const token = getAuthToken();
    const actuallyLoggedIn = !!token;
    if (actuallyLoggedIn !== isLoggedIn) {
      setIsLoggedIn(actuallyLoggedIn);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentPage]); // isLoggedIn 제거하여 무한 루프 방지

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
    // welfare 페이지가 아닌 곳으로 이동하면 검색어 초기화
    if (page !== 'welfare') {
      setWelfareSearchQuery('');
    }
  }, [isLoggedIn]);

  // 로그인 상태 업데이트 함수 (메모이제이션)
  const updateLoginStatus = useCallback((token?: string) => {
    // 토큰이 전달된 경우 저장
    if (token) {
      setAuthToken(token);
      // 상태 업데이트를 강제로 실행
      setIsLoggedIn(true);
    } else {
      // 토큰이 없으면 localStorage에서 확인
      const currentToken = getAuthToken();
      setIsLoggedIn(!!currentToken);
    }
  }, []);

  // 로그아웃 핸들러 (메모이제이션)
  const handleLogout = useCallback(() => {
    authLogout();
    setIsLoggedIn(false);
    setCurrentPage('home');
  }, []);

  // 로그인 클릭 핸들러 (메모이제이션)
  const handleLoginClick = useCallback(() => {
    handleNavigate('login');
  }, [handleNavigate]);

  // 커뮤니티 클릭 핸들러 (메모이제이션)
  const handleCommunityClick = useCallback((page: Page) => {
    handleNavigate(page);
  }, [handleNavigate]);

  // 커뮤니티 상태
  const [posts, setPosts] = useState<Post[]>([]);
  const [selectedPostId, setSelectedPostId] = useState<number | null>(null);
  const [selectedPost, setSelectedPost] = useState<Post | null>(null);

   // 앱 시작 시 게시글 불러오기 (로그인된 경우에만)
  useEffect(() => {
    // 토큰 확인으로 실제 로그인 상태 체크
    const token = getAuthToken();
    const actuallyLoggedIn = !!token;
    
    // 상태와 실제 토큰이 다르면 동기화
    if (actuallyLoggedIn !== isLoggedIn) {
      setIsLoggedIn(actuallyLoggedIn);
    }
    
    if (!actuallyLoggedIn) {
      setPosts([]);
      return;
    }
    
    // 약간의 지연을 주어 상태 업데이트가 완료되도록 함
    const timer = setTimeout(() => {
      fetchPosts()
        .then((data) => {
          setPosts(data);
        })
        .catch((error: any) => {
          // 개발 모드에서만 로깅
          if ((import.meta as any).env?.DEV) {
            console.error('게시글 불러오기 실패:', error);
          }
          // 401 에러인 경우 로그인 상태를 false로 변경
          if (error.status === 401) {
            setIsLoggedIn(false);
          }
        });
    }, 100);
    
    return () => clearTimeout(timer);
  }, [isLoggedIn]);

  // 어떤 복지를 선택했는지 (상세 페이지용)
  const [selectedWelfareId, setSelectedWelfareId] = useState<number | null>(null);
  
  // 복지서비스 검색어 상태 관리
  const [welfareSearchQuery, setWelfareSearchQuery] = useState<string>('');

  // 어떤 것들이 북마크 됐는지 id 배열로 관리
  const [bookmarkedWelfareIds, setBookmarkedWelfareIds] = useState<number[]>([]);
  
  // 북마크된 복지 정보 저장 (시연용: 빈 배열로 시작)
  const [bookmarkedWelfares, setBookmarkedWelfares] = useState<WelfareType[]>([]);

  // 북마크 게시글 관리 (메모이제이션)
  const bookmarkedPosts = useMemo(() => posts.filter((p) => p.isBookmarked), [posts]);

  // 북마크 토글 핸들러 (메모이제이션)
  // 복지 정보를 가져와서 북마크 목록에 추가/제거
  const toggleWelfareBookmark = useCallback(async (id: number) => {
    const isBookmarked = bookmarkedWelfareIds.includes(id);
    
    if (isBookmarked) {
      // 북마크 해제
      setBookmarkedWelfareIds((prev) => prev.filter((x) => x !== id));
      setBookmarkedWelfares((prev) => prev.filter((w) => w.id !== id));
    } else {
      // 북마크 추가 - 복지 정보 가져오기
      try {
        const welfareDetail = await getWelfareDetail(id);
        // WelfareDetail을 Welfare 타입으로 변환
        const welfare: WelfareType = {
          id: welfareDetail.id,
          title: welfareDetail.title,
          summary: welfareDetail.summary || '',
          source_link: welfareDetail.source_link,
          region: welfareDetail.region,
          apply_start: welfareDetail.apply_start,
          apply_end: welfareDetail.apply_end,
          is_always: welfareDetail.is_always,
          status: welfareDetail.status,
          eligibility: [],
        };
        setBookmarkedWelfareIds((prev) => [...prev, id]);
        setBookmarkedWelfares((prev) => [...prev, welfare]);
      } catch (error) {
        console.error('복지 정보 가져오기 실패:', error);
        // 에러가 나도 ID는 추가
        setBookmarkedWelfareIds((prev) => [...prev, id]);
      }
    }
  }, [bookmarkedWelfareIds]);

  // 게시글 좋아요 토글 (서비스 + 상태 반영)
  const handleTogglePostLike = async (postId: number) => {
    const updated = await toggleLike(postId); // postService에서 토글 후 업데이트 된 데이터 반환
    if (!updated) return;

    setPosts((prev) =>
      prev.map((p) => (p.id === postId ? updated : p)),
    );
    
    // 현재 선택된 게시글이면 업데이트
    if (selectedPost && selectedPost.id === postId) {
      setSelectedPost(updated);
    }
  };

  // 게시글 북마크 토글 (서비스 + 상태 반영)
  const handleTogglePostBookmark = async (postId: number) => {
    const updated = await toggleBookmark(postId);
    if (!updated) return;

    setPosts((prev) =>
      prev.map((p) => (p.id === postId ? updated : p)),
    );
    
    // 현재 선택된 게시글이면 업데이트
    if (selectedPost && selectedPost.id === postId) {
      setSelectedPost(updated);
    }
  };


  // PostSubmit에서 사용
  // 시연용: 로그인 체크 제거
  const addPost = async (data: { title: string; preview: string; category: 'info' | 'counsel' | 'free' }) => {
    try {
      // API 호출로 게시글 생성
      const newPost = await createPost(data.title, data.preview, data.category);
      // 상태 업데이트 (최신글이 위로 오도록)
      setPosts((prev) => [newPost, ...prev]);
    } catch (error: any) {
      // 개발 모드에서만 로깅
      if ((import.meta as any).env?.DEV) {
        console.error('게시글 생성 실패:', error);
      }
      
      // 시연용: 401 에러가 발생해도 계속 진행
      // 기타 에러 처리
      const errorMessage = error.message || '게시글 작성에 실패했습니다.';
      alert(errorMessage);
    }
  };

  const addComment = async (postId: number, content: string) => {
    try {
      // API를 통해 댓글 작성
      const { createComment } = await import('./services/postService');
      await createComment(postId, content);
      
      // 댓글 작성 후 게시글 상세 정보 다시 가져오기
      const updatedPost = await fetchPostDetail(postId);
      setSelectedPost(updatedPost);
      
      // posts 목록도 업데이트
      setPosts((prev) =>
        prev.map((post) =>
          post.id === postId
            ? {
                ...post,
                comments: updatedPost.comments || [],
                commentCount: updatedPost.commentCount || 0,
              }
            : post,
        ),
      );
    } catch (error) {
      console.error('댓글 작성 실패:', error);
      // 실패 시에도 로컬 상태 업데이트 (시연용)
      const now = new Date();
      const date = `${now.getFullYear()}.${now.getMonth() + 1}.${now.getDate()} ${now.getHours()}:${now.getMinutes()}`;

      setPosts((prev) =>
        prev.map((post) =>
          post.id === postId
            ? {
                ...post,
                comments: [...(post.comments || []), { id: Date.now(), content, date }],
                commentCount: (post.commentCount || 0) + 1,
              }
            : post,
        ),
      );
      
      if (selectedPost && selectedPost.id === postId) {
        setSelectedPost({
          ...selectedPost,
          comments: [...(selectedPost.comments || []), { id: Date.now(), content, date }],
          commentCount: (selectedPost.commentCount || 0) + 1,
        });
      }
    }
  };

  // 복지 카드 클릭 시: id 저장 + 상세 페이지로 이동 (메모이제이션)
  const handleSelectWelfare = useCallback((id: number) => {
    setSelectedWelfareId(id);
    handleNavigate('welfare-detail');
  }, [handleNavigate]);

  // 활성 페이지에 따라 Navbar의 activePage 결정 (login/signup 제외)
  const navbarActivePage = useMemo(() => {
    if (currentPage === 'login' || currentPage === 'signup') {
      return 'home';
    }
    if (currentPage === 'welfare-detail') {
      return 'welfare';
    }
    if (currentPage === 'post-detail' || currentPage === 'post-submit') {
      return 'community';
    }
    return currentPage;
  }, [currentPage]);

  // Navbar 표시 여부 (login/signup 페이지에서는 숨김)
  const showNavbar = currentPage !== 'login' && currentPage !== 'signup';

  const renderPage = () => {
    switch (currentPage) {
      case 'login':
        return <Login onNavigate={handleNavigate} onLoginSuccess={updateLoginStatus} />;

      case 'signup':
        return <Signup onNavigate={handleNavigate} onSignupSuccess={updateLoginStatus} />;

      case 'home':
        return (
          <Home
            onNavigate={handleNavigate}
            bookmarkedIds={bookmarkedWelfareIds}
            onToggleBookmark={toggleWelfareBookmark}
            onSelectWelfare={handleSelectWelfare}
            onSearchQuery={setWelfareSearchQuery}
          />
        );

      case 'chat':
        return <Chat />;

      case 'welfare':
        return (
          <Welfare
            onNavigate={handleNavigate}
            bookmarkedIds={bookmarkedWelfareIds}
            onToggleBookmark={toggleWelfareBookmark}
            onSelectWelfare={handleSelectWelfare}
            initialQuery={welfareSearchQuery}
          />
        );

      case 'welfare-detail': {
        // 선택된 복지 ID가 없으면 복지 목록으로 리다이렉트
        if (!selectedWelfareId) {
          return (
            <div className="max-w-4xl mx-auto p-4">
              <p>선택된 복지 정보가 없습니다.</p>
              <button
                className="mt-4 underline"
                onClick={() => handleNavigate('welfare')}
              >
                복지 목록으로 돌아가기
              </button>
            </div>
          );
        }

        const isBookmarked = bookmarkedWelfareIds.includes(selectedWelfareId);

        return (
          <WelfareDetail
            onNavigate={handleNavigate}
            welfareId={selectedWelfareId}
            isBookmarked={isBookmarked}
            onToggleBookmark={() =>
              toggleWelfareBookmark(selectedWelfareId)
            }
          />
        );
      }

      case 'community':
        return (
          <Community
            posts={posts}
            onToggleBookmark={handleTogglePostBookmark}
            onToggleLike={handleTogglePostLike}
            onNavigate={handleNavigate}
            onPostClick={async (id) => {
              setSelectedPostId(id);
              try {
                // 게시글 상세 정보 가져오기 (댓글 포함)
                const postDetail = await fetchPostDetail(id);
                setSelectedPost(postDetail);
                handleNavigate('post-detail');
              } catch (error) {
                console.error('게시글 상세 조회 실패:', error);
                // 실패해도 기본 게시글 정보로 표시
                setSelectedPost(posts.find((p) => p.id === id) || null);
                handleNavigate('post-detail');
              }
            }}
          />
        );

      case 'post-detail': {
        // selectedPost가 있으면 사용, 없으면 posts에서 찾기
        const post = selectedPost || posts.find((p) => p.id === selectedPostId) || null;
        return (
          <PostDetail
            onNavigate={handleNavigate}
            post={post}
            onAddComment={addComment}
            onToggleLike={handleTogglePostLike}
            onToggleBookmark={handleTogglePostBookmark}
          />
        );
      }

      case 'post-submit':
        return (
          <PostSubmit
            onNavigate={handleNavigate}
            onSubmit={(data) => {
              addPost(data);
              handleNavigate('community');
            }}
            isLoggedIn={isLoggedIn}
          />
        );

      case 'mypage':
        return (
          <MyPage
            onNavigate={handleNavigate}
            bookmarkedWelfares={bookmarkedWelfares}
            onSelectWelfare={handleSelectWelfare}
            bookmarkedPosts={bookmarkedPosts}
            onSelectPost={async (id) => {
              setSelectedPostId(id);
              try {
                // 게시글 상세 정보 가져오기 (댓글 포함)
                const postDetail = await fetchPostDetail(id);
                setSelectedPost(postDetail);
                handleNavigate('post-detail');
              } catch (error) {
                console.error('게시글 상세 조회 실패:', error);
                // 실패해도 기본 게시글 정보로 표시
                setSelectedPost(posts.find((p) => p.id === id) || null);
                handleNavigate('post-detail');
              }
            }}
          />
        );

      case 'admin':
        return <AdminVerification />;

      default:
        return (
          <Home
            onNavigate={handleNavigate}
            bookmarkedIds={bookmarkedWelfareIds}
            onToggleBookmark={toggleWelfareBookmark}
            onSelectWelfare={handleSelectWelfare}
            onSearchQuery={setWelfareSearchQuery}
          />
        );
    }
  };

  return (
    <div className="min-h-screen">
      {showNavbar && (
        <Navbar 
          activePage={navbarActivePage}
          onNavigate={handleNavigate}
          isLoggedIn={isLoggedIn}
          onLoginClick={handleLoginClick}
          onLogoutClick={handleLogout}
          onCommunityClick={handleCommunityClick}
        />
      )}
      {renderPage()}
    </div>
  );
}