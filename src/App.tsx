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

export default function App() {
  const [currentPage, setCurrentPage] = useState('login');

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
            <Home onNavigate={setCurrentPage} />
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
            <Welfare onNavigate={setCurrentPage} />
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
            <Community onNavigate={setCurrentPage} />
          </>
        );
      case 'post-detail':
        return (
          <>
            <Navbar activePage="community" onNavigate={setCurrentPage} />
            <PostDetail onNavigate={setCurrentPage} />
          </>
        );
      case 'post-submit':
        return (
          <>
            <Navbar activePage="community" onNavigate={setCurrentPage} />
            <PostSubmit onNavigate={setCurrentPage} />
          </>
        );
      case 'mypage':
        return (
          <>
            <Navbar activePage="mypage" onNavigate={setCurrentPage} />
            <MyPage onNavigate={setCurrentPage} />
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
            <Home onNavigate={setCurrentPage} />
          </>
        );
    }
  };

  return <div className="min-h-screen">{renderPage()}</div>;
}
