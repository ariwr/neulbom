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
  type ChatConversation,
  type ChatMessage,
} from '../services/chatService';

export function Chat() {
  const [message, setMessage] = useState('');
  const [showCrisisPanel, setShowCrisisPanel] = useState(false);

  const [conversations, setConversations] = useState<ChatConversation[]>([]);
  const [activeConversationId, setActiveConversationId] = useState<number | null>(null);
  const [messages, setMessagesState] = useState<ChatMessage[]>([]); // 현재 active 대화의 메시지들

  // ---- 1) 초기 대화 목록 로딩 ----
  useEffect(() => {
    fetchConversations().then((data) => {
      setConversations(data);
      if (data.length && activeConversationId === null) {
        setActiveConversationId(data[0].id);
      }
    });
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

  // 새 대화 만들기
  const handleNewConversation = async () => {
    const newConv = await createConversation();
    setConversations(prev => [newConv, ...prev]);
    setActiveConversationId(newConv.id);
    setMessagesState([]); // 새 대화라 메시지 없음
  };

  // ---- 4) 제목 수정 ----
  const handleRenameConversation = async () => {
    if (activeConversationId == null) return;
    const current = conversations.find((c) => c.id === activeConversationId);
    const newTitle = window.prompt('대화 제목을 수정하세요', current?.title ?? '');
    if (!newTitle || !newTitle.trim()) return;

    await renameConversation(activeConversationId, newTitle.trim());
    setConversations((prev) =>
      prev.map((c) =>
        c.id === activeConversationId ? { ...c, title: newTitle.trim() } : c,
      ),
    );
  };

  // ---- 5) 대화 삭제 ----
  const handleDeleteConversation = async () => {
    if (activeConversationId == null) return;
    const ok = window.confirm('이 대화를 삭제하시겠습니까?');
    if (!ok) return;

    await deleteConversation(activeConversationId);
    setConversations((prev) => prev.filter((c) => c.id !== activeConversationId));

    // 남은 대화 중 첫 번째로 이동, 없으면 null
    setMessagesState([]);
    setActiveConversationId((prevId) => {
      const rest = conversations.filter((c) => c.id !== prevId);
      return rest.length ? rest[0].id : null;
    });
  };

  // ---- 6) 메시지 전송 ----
  const handleSend = async () => {
    if (!message.trim() || activeConversationId == null) return;

    const text = message.trim();
    setMessage('');

    const newMsgs = await sendMessage(activeConversationId, text);
    setMessagesState((prev) => [...prev, ...newMsgs]);

    // TODO: 위기 탐지 로직은 나중에 AI 응답 기반으로 설정
    // setShowCrisisPanel(위기감지여부);
  };

  const activeConversation = conversations.find(
    (c) => c.id === activeConversationId,
  );

  return (
    <div className="h-screen flex" style={{ backgroundColor: colors.lightGray }}>
      {/* Left Sidebar - Conversation History */}
      <div
        className="w-80 bg-white border-r hidden lg:block"
        style={{ borderColor: colors.lightGray }}
      >
        <div className="p-4 border-b" style={{ borderColor: colors.lightGray }}>
          <h2 className="text-lg" style={{ color: colors.textDark }}>
            대화 기록
          </h2>
        </div>
        <div className="overflow-y-auto h-full">
          {conversations.map((conv) => (
            <div
              key={conv.id}
              className="p-4 border-b cursor-pointer hover:bg-opacity-50 transition-all"
              style={{
                borderColor: colors.lightGray,
                backgroundColor:
                  conv.id === activeConversationId
                    ? colors.mainGreen1 + '20'
                    : 'transparent',
              }}
              onClick={() => handleSelectConversation(conv.id)}
            >
              <p className="text-sm mb-1" style={{ color: colors.textDark }}>
                {conv.title}
              </p>
              <p className="text-xs" style={{ color: colors.textSub }}>
                {conv.createdAt}
              </p>
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

            {/* 현재 선택된 대화가 있을 때만 제목 수정/삭제 노출 */}
            {activeConversation && (
              <>
                <Button variant="outline" size="sm" onClick={handleRenameConversation}>
                  제목 수정
                </Button>
                <Button variant="outline" size="sm" onClick={handleDeleteConversation}>
                  대화 삭제
                </Button>
              </>
            )}

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
            {messages.map((msg) => (
              <ChatBubble
                key={msg.id}
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
          className="bg-white border-t p-4"
          style={{ borderColor: colors.lightGray }}
        >
          <div className="max-w-4xl mx-auto flex items-end space-x-3">
            <div className="flex-1">
              <textarea
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="메시지를 입력하세요..."
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
