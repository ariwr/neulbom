import React, { useState } from 'react';
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
import { initialComments, initialPosts, type Post } from './services/postService';
import { initialWelfares, type Welfare as WelfareType } from './services/welfareService';

export default function App() {
  const [currentPage, setCurrentPage] = useState('login');

  // 커뮤니티 상태
  const [posts, setPosts] = useState<Post[]>(initialPosts);
  const [selectedPostId, setSelectedPostId] = useState<number | null>(null);

  const [welfares] = useState<WelfareType[]>(initialWelfares);
  // 어떤 것들이 북마크 됐는지 id 배열로 관리
  const [bookmarkedWelfareIds, setBookmarkedWelfareIds] = useState<number[]>([]);

  // 북마크 토글 핸들러
  const toggleWelfareBookmark = (id: number) => {
    setBookmarkedWelfareIds((prev) =>
      prev.includes(id)
        ? prev.filter((x) => x !== id)      // 있으면 해제
        : [...prev, id]                     // 없으면 추가
    );
  };

  // 마이페이지에 넘길 북마크된 복지 목록
  const bookmarkedWelfares = welfares.filter((w) =>
    bookmarkedWelfareIds.includes(w.id)
  );

  // PostSubmit에서 사용
  const addPost = (data: { title: string; preview: string; tags: string[] }) => {
    const nextId = posts.length ? posts[posts.length - 1].id + 1 : 1;

    const today = new Date();
    const dateString = `${today.getFullYear()}.${String(today.getMonth() + 1).padStart(2, '0')}.${String(
      today.getDate(),
    ).padStart(2, '0')}`;

    const newPost: Post = {
      id: nextId,
      title: data.title,
      preview: data.preview,
      tags: data.tags,
      date: dateString,
      commentCount: 0,
      comments: initialComments
    };

    setPosts((prev) => [newPost, ...prev]);
  };

  const addComment = (postId: number, content: string) => {
    const now = new Date();
    const date = `${now.getFullYear()}.${now.getMonth()+1}.${now.getDate()} ${now.getHours()}:${now.getMinutes()}`;

    setPosts(prev =>
      prev.map(post =>
        post.id === postId
          ? {
              ...post,
              comments: [
                ...post.comments,
                { id: Date.now(), content, date }
              ],
              commentCount: post.commentCount + 1,
            }
          : post
      )
    );
  };

  const renderPage = () => {
    switch (currentPage) {
      case 'login':
        return <Login onNavigate={setCurrentPage} />;
      case 'signup':
        return <Signup onNavigate={setCurrentPage} />;
      case 'home':
        return (
          <>
            <Navbar activePage="home" onNavigate={setCurrentPage} />
            <Home
              onNavigate={setCurrentPage}
              welfares={welfares}
              bookmarkedIds={bookmarkedWelfareIds}
              onToggleBookmark={toggleWelfareBookmark}
            />
          </>
        );
      case 'chat':
        return (
          <>
            <Navbar activePage="chat" onNavigate={setCurrentPage} />
            <Chat />
          </>
        );
      case 'welfare':
        return (
          <>
            <Navbar activePage="welfare" onNavigate={setCurrentPage} />
            <Welfare
              onNavigate={setCurrentPage}
              welfares={welfares}
              bookmarkedIds={bookmarkedWelfareIds}
              onToggleBookmark={toggleWelfareBookmark} 
            />
          </>
        );
      case 'welfare-detail':
        return (
          <>
            <Navbar activePage="welfare" onNavigate={setCurrentPage} />
            <WelfareDetail onNavigate={setCurrentPage} />
          </>
        );
      case 'community':
        return (
          <>
            <Navbar activePage="community" onNavigate={setCurrentPage} />
            <Community 
              posts={posts}
              onNavigate={setCurrentPage}
              onPostClick={(id) => {
                setSelectedPostId(id);
                setCurrentPage('post-detail');
              }}
              />
          </>
        );
      case 'post-detail': {
        const post = posts.find((p) => p.id === selectedPostId) || null;
        return (
          <>
            <Navbar activePage="community" onNavigate={setCurrentPage} />
            <PostDetail 
              onNavigate={setCurrentPage} 
              post={post}
              onAddComment={addComment}
            />
          </>
        );
      }
      case 'post-submit':
        return (
          <>
            <Navbar activePage="community" onNavigate={setCurrentPage} />
            <PostSubmit 
              onNavigate={setCurrentPage}
              onSubmit={(data) => {
                addPost(data);
                setCurrentPage('community');
              }}  
            />
          </>
        );
      case 'mypage':
        return (
          <>
            <Navbar activePage="mypage" onNavigate={setCurrentPage} />
            <MyPage
              onNavigate={setCurrentPage}
              bookmarkedWelfares={bookmarkedWelfares}  
            />
          </>
        );
      case 'admin':
        return (
          <>
            <Navbar activePage="home" onNavigate={setCurrentPage} />
            <AdminVerification />
          </>
        );
      default:
        return (
          <>
            <Navbar activePage="home" onNavigate={setCurrentPage} />
            <Home
              onNavigate={setCurrentPage}
              welfares={welfares}
              bookmarkedIds={bookmarkedWelfareIds}
              onToggleBookmark={toggleWelfareBookmark}
            />
          </>
        );
    }
  };

  return <div className="min-h-screen">{renderPage()}</div>;
}
