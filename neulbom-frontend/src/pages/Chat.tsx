// Chat.tsx
import React, { useState, useEffect } from 'react';
import { Send, AlertTriangle } from 'lucide-react';
import { Card } from '../components/ui/ThemedCard';
import { Button } from '../components/ui/ThemedButton';
import { ChatBubble } from '../components/ChatBubble';
import { CrisisPanel } from '../components/CrisisPanel';
import { colors } from '../styles/design-tokens';

import {
  fetchConversations,
  fetchMessages,
  renameConversation,
  deleteConversation,
  sendMessage,
  createConversation,
  getLocalChats,
  createLocalChat,
  type ChatConversation,
  type ChatMessage,
  type ChatResponse,
} from '../services/chatService';
import { getAuthToken } from '../config/api';

export function Chat() {
  const [message, setMessage] = useState('');
  const [showCrisisPanel, setShowCrisisPanel] = useState(false);

  const [conversations, setConversations] = useState<ChatConversation[]>([]);
  const [activeConversationId, setActiveConversationId] = useState<number | null>(null);
  const [messages, setMessagesState] = useState<ChatMessage[]>([]); // 현재 active 대화의 메시지들
  const [isUserLoggedIn, setIsUserLoggedIn] = useState<boolean>(() => !!getAuthToken());

  // 채팅방 목록 로딩 함수
  const loadConversations = async () => {
    try {
      const data = await fetchConversations();
      setConversations(data);
      if (data.length && activeConversationId === null) {
        setActiveConversationId(data[0].id);
      }
    } catch (error) {
      // 에러는 조용히 처리
      console.log('채팅방 목록을 불러올 수 없습니다:', error);
    }
  };

  // 로그인 상태 감지
  useEffect(() => {
    const checkLoginStatus = () => {
      const loggedIn = !!getAuthToken();
      setIsUserLoggedIn(loggedIn);
      
      // 로그인 상태가 변경되면 채팅방 목록 새로고침
      loadConversations();
    };
    
    // 초기 로그인 상태 확인
    checkLoginStatus();
    
    // 주기적으로 로그인 상태 확인 (간단한 방법)
    const interval = setInterval(checkLoginStatus, 1000);
    return () => clearInterval(interval);
  }, []);

  // ---- 1) 초기 대화 목록 로딩 및 첫 대화 생성 (로그인 여부와 관계없이) ----
  useEffect(() => {
    const initializeChat = async () => {
      try {
        const loadedConversations = await fetchConversations();
        setConversations(loadedConversations);
        
        // 대화가 없으면 첫 대화 생성
        if (loadedConversations.length === 0) {
          try {
            const firstConv = await createConversation('새 대화');
            setConversations([firstConv]);
            setActiveConversationId(firstConv.id);
            setMessagesState([]);
          } catch (error) {
            console.log('초기 대화 생성 실패:', error);
          }
        } else {
          // 대화가 있으면 첫 번째 대화 선택 (activeConversationId가 null일 때만)
          if (activeConversationId === null) {
            setActiveConversationId(loadedConversations[0].id);
          }
        }
      } catch (error) {
        console.log('대화 목록 로드 실패:', error);
      }
    };
    initializeChat();
  }, []);

  // ---- 2) activeConversationId 변경될 때마다 메시지 로딩 ----
  useEffect(() => {
    if (activeConversationId == null) return;
    fetchMessages(activeConversationId).then((msgs) => setMessagesState(msgs));
  }, [activeConversationId]);

  // ---- 3) 대화 선택 ----
  const handleSelectConversation = (id: number) => {
    setActiveConversationId(id);
  };

  // 새 대화 만들기 (비회원도 가능)
  const handleNewConversation = async () => {
    try {
      const newConv = await createConversation();
      setConversations(prev => [newConv, ...prev]);
      setActiveConversationId(newConv.id);
      setMessagesState([]); // 새 대화라 메시지 없음
    } catch (error: any) {
      console.error('채팅방 생성 실패:', error);
      // 시연용: 에러가 나도 로컬 채팅방 생성으로 폴백
      try {
        const localChat = createLocalChat('새 대화');
        const newConv = {
          id: parseInt(localChat.id.replace('local_', '').split('_')[0]) || Date.now(),
          title: localChat.title,
          created_at: localChat.created_at,
        };
        setConversations(prev => [newConv, ...prev]);
        setActiveConversationId(newConv.id);
        setMessagesState([]);
      } catch (fallbackError) {
        console.error('로컬 채팅방 생성도 실패:', fallbackError);
        alert('채팅방 생성에 실패했습니다.');
      }
    }
  };

  // ---- 4) 제목 수정 (비회원도 가능) ----
  const handleRenameConversation = async (conversationId?: number) => {
    const targetId = conversationId || activeConversationId;
    if (targetId == null) return;
    const current = conversations.find((c) => c.id === targetId);
    const newTitle = window.prompt('대화 제목을 수정하세요', current?.title ?? '');
    if (!newTitle || !newTitle.trim()) return;

    try {
      await renameConversation(targetId, newTitle.trim());
      setConversations((prev) =>
        prev.map((c) =>
          c.id === targetId ? { ...c, title: newTitle.trim() } : c,
        ),
      );
    } catch (error: any) {
      console.error('제목 수정 실패:', error);
      alert('제목 수정에 실패했습니다.');
    }
  };

  // ---- 5) 대화 삭제 (비회원도 가능) ----
  const handleDeleteConversation = async (conversationId?: number) => {
    const targetId = conversationId || activeConversationId;
    if (targetId == null) return;

    try {
      await deleteConversation(targetId);
      const updatedConversations = conversations.filter((c) => c.id !== targetId);
      setConversations(updatedConversations);

      // 남은 대화 중 첫 번째로 이동, 없으면 null
      setMessagesState([]);
      if (targetId === activeConversationId) {
        setActiveConversationId(updatedConversations.length > 0 ? updatedConversations[0].id : null);
      }
    } catch (error: any) {
      console.error('대화 삭제 실패:', error);
      alert('대화 삭제에 실패했습니다.');
    }
  };

  // ---- 6) 메시지 전송 (비회원도 가능, 기록은 로그인 후에만 저장) ----
  const handleSend = async () => {
    if (!message.trim()) return;

    const text = message.trim();
    setMessage('');

    try {
      const response = await sendMessage(activeConversationId, text, messages);
      
      // 사용자 메시지 추가
      const userMsg: ChatMessage = {
        id: Date.now(), // 고유 ID 생성
        conversationId: activeConversationId || 0,
        content: text,
        isUser: true,
        timestamp: new Date().toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' }),
      };
      
      // 봇 응답 추가
      const botMsg: ChatMessage = {
        id: Date.now() + 1, // 고유 ID 생성 (사용자 메시지와 구분)
        conversationId: activeConversationId || 0,
        content: response.reply,
        isUser: false,
        timestamp: new Date().toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' }),
      };
      
      setMessagesState((prev) => [...prev, userMsg, botMsg]);
      
      // 위기 감지 처리
      if (response.is_crisis) {
        setShowCrisisPanel(true);
      }
      
      // room_id가 반환되면 저장 (새 채팅방 생성된 경우 - 로그인한 사용자만)
      if (response.room_id && activeConversationId === null && isUserLoggedIn) {
        setActiveConversationId(response.room_id);
        // 채팅방 목록 새로고침
        loadConversations();
      }
      
      // 비회원이고 새 채팅방이 생성된 경우 (로컬)
      if (!isUserLoggedIn && activeConversationId === null && response.room_id) {
        // sendMessage에서 이미 로컬 채팅방을 생성했으므로 목록만 새로고침
        loadConversations();
        // 새로 생성된 채팅방 ID로 설정
        const localChats = getLocalChats();
        if (localChats.length > 0) {
          const newChatId = parseInt(localChats[0].id.replace('local_', '').split('_')[0]) || 0;
          setActiveConversationId(newChatId);
        }
      }
    } catch (error) {
      console.error('메시지 전송 실패:', error);
      alert('메시지 전송에 실패했습니다. 다시 시도해주세요.');
      setMessage(text); // 실패한 메시지 복원
    }
  };

  const activeConversation = conversations.find(
    (c) => c.id === activeConversationId,
  );

  return (
    <div
      className="min-h-screen pb-20 flex"
      style={{ backgroundColor: colors.lightGray }}
    >
      {/* Left Sidebar - Conversation History */}
      <div
        className="w-80 bg-white border-r hidden lg:block"
        style={{ borderColor: colors.lightGray }}
      >
        <div className="p-4 border-b" style={{ borderColor: colors.lightGray }}>
          <h2 className="text-lg" style={{ color: colors.textDark }}>
            대화 기록
          </h2>
          {!isUserLoggedIn && (
            <p className="text-xs mt-1" style={{ color: colors.textSub }}>
              로그인하면 기록이 서버에 저장됩니다
            </p>
          )}
        </div>
        <div className="overflow-y-auto h-full">
          {conversations.map((conv) => (
            <div
              key={conv.id}
              className="p-4 border-b cursor-pointer hover:bg-opacity-50 transition-all relative group"
              style={{
                borderColor: colors.lightGray,
                backgroundColor:
                  conv.id === activeConversationId
                    ? colors.mainGreen1 + '20'
                    : 'transparent',
              }}
              onClick={() => handleSelectConversation(conv.id)}
            >
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <p className="text-sm mb-1" style={{ color: colors.textDark }}>
                    {conv.title}
                  </p>
                  <p className="text-xs" style={{ color: colors.textSub }}>
                    {conv.created_at ? new Date(conv.created_at).toLocaleDateString('ko-KR') : ''}
                  </p>
                </div>
                {/* 좌측 대화기록에서만 제목 수정/삭제 버튼 표시 */}
                {conv.id === activeConversationId && (
                  <div className="flex items-center space-x-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleRenameConversation(conv.id);
                      }}
                      className="p-1 rounded hover:bg-opacity-20"
                      style={{ backgroundColor: colors.lightGray }}
                      title="제목 수정"
                    >
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke={colors.textSub} strokeWidth="2">
                        <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                        <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                      </svg>
                    </button>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        if (window.confirm('이 대화를 삭제하시겠습니까?')) {
                          handleDeleteConversation(conv.id);
                        }
                      }}
                      className="p-1 rounded hover:bg-opacity-20"
                      style={{ backgroundColor: colors.lightGray }}
                      title="대화 삭제"
                    >
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke={colors.error} strokeWidth="2">
                        <path d="M3 6h18"></path>
                        <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                      </svg>
                    </button>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Center - Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div
          className="bg-white border-b p-4 flex items-center justify-between"
          style={{ borderColor: colors.lightGray }}
        >
          <div className="flex items-center space-x-3">
            <div
              className="w-10 h-10 rounded-full flex items-center justify-center"
              style={{ backgroundColor: colors.mainGreen1 }}
            >
              <span className="text-white">AI</span>
            </div>
            <div>
              <h3 className="text-base" style={{ color: colors.textDark }}>
                {activeConversation?.title ?? '늘봄 챗봇'}
              </h3>
              <p className="text-xs" style={{ color: colors.textSub }}>
                항상 함께합니다
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            {/* 새 대화 버튼 */}
            <Button variant="outline" size="sm" onClick={handleNewConversation}>
              새 대화
            </Button>

            {/* 제목 수정/삭제 버튼은 좌측 대화기록에서만 사용 가능하도록 제거 */}

            {showCrisisPanel && (
              <div
                className="flex items-center space-x-2 px-3 py-1 rounded-full"
                style={{ backgroundColor: colors.error + '20' }}
              >
                <AlertTriangle size={16} style={{ color: colors.error }} />
                <span className="text-xs" style={{ color: colors.error }}>
                  위기 감지됨
                </span>
              </div>
            )}
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-6">
          <div className="max-w-4xl mx-auto">
            {messages.map((msg, index) => (
              <ChatBubble
                key={msg.id ?? `msg-${index}-${msg.timestamp}`}
                message={msg.content}
                isUser={msg.isUser}
                timestamp={msg.timestamp}
              />
            ))}

            {messages.length === 0 && (
              <p className="text-sm text-center mt-8" style={{ color: colors.textSub }}>
                아직 메시지가 없습니다. 아래 입력창에서 대화를 시작해보세요.
              </p>
            )}
          </div>
        </div>

        {/* Input Area */}
        <div
          className="bg-white border-t p-4 sticky botton-0"
          style={{ borderColor: colors.lightGray }}
        >
          <div className="max-w-4xl mx-auto flex items-end space-x-3">
            <div className="flex-1">
              <textarea
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleSend();
                  }
                }}
                placeholder="메시지를 입력하세요... (Enter로 전송, Shift+Enter로 줄바꿈)"
                rows={3}
                className="w-full px-4 py-3 rounded-2xl outline-none border-2 resize-none"
                style={{
                  backgroundColor: colors.white,
                  borderColor: colors.lightGray,
                  color: colors.textDark,
                }}
              />
            </div>
            <button
              className="w-12 h-12 rounded-full flex items-center justify-center flex-shrink-0 hover:opacity-90 transition-opacity"
              style={{ backgroundColor: colors.mainGreen2 }}
              onClick={handleSend}
            >
              <Send size={20} color={colors.white} />
            </button>
          </div>
        </div>
      </div>

      {/* Right Sidebar - Crisis Detection Panel */}
      {showCrisisPanel && (
        <div
          className="w-80 bg-white border-l p-4 hidden xl:block"
          style={{ borderColor: colors.lightGray }}
        >
          <CrisisPanel />
        </div>
      )}
    </div>
  );
}
