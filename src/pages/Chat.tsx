import React, { useState } from 'react';
import { Send, AlertTriangle } from 'lucide-react';
import { Card } from '../components/ui/ThemedCard';
import { Button } from '../components/ui/ThemedButton';
import { ChatBubble } from '../components/ChatBubble';
import { CrisisPanel } from '../components/CrisisPanel';
import { colors } from '../styles/design-tokens';

export function Chat() {
  const [message, setMessage] = useState('');
  const [showCrisisPanel, setShowCrisisPanel] = useState(false);

  const conversations = [
    { id: 1, title: '복지 서비스 문의', date: '2025.11.20', active: true },
    { id: 2, title: '돌봄 스트레스 상담', date: '2025.11.19', active: false },
    { id: 3, title: '지역 자원 안내', date: '2025.11.18', active: false },
  ];

  const messages = [
    { id: 1, message: '안녕하세요! 오늘은 어떤 도움이 필요하신가요?', isUser: false, timestamp: '14:30' },
    { id: 2, message: '요즘 부모님 돌봄이 너무 힘들어요. 어떤 지원을 받을 수 있을까요?', isUser: true, timestamp: '14:32' },
    { id: 3, message: '돌봄의 어려움을 말씀해주셔서 감사합니다. 거주 지역과 부모님 연령대를 알려주시면 맞춤 복지 서비스를 안내해드릴게요.', isUser: false, timestamp: '14:33' },
    { id: 4, message: '서울 강남구이고, 어머니는 75세이십니다', isUser: true, timestamp: '14:35' },
  ];

  return (
    <div className="h-screen flex" style={{ backgroundColor: colors.lightGray }}>
      {/* Left Sidebar - Conversation History */}
      <div className="w-80 bg-white border-r hidden lg:block" style={{ borderColor: colors.lightGray }}>
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
                backgroundColor: conv.active ? colors.mainGreen1 + '20' : 'transparent',
              }}
            >
              <p className="text-sm mb-1" style={{ color: colors.textDark }}>
                {conv.title}
              </p>
              <p className="text-xs" style={{ color: colors.textSub }}>
                {conv.date}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* Center - Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="bg-white border-b p-4 flex items-center justify-between" style={{ borderColor: colors.lightGray }}>
          <div className="flex items-center space-x-3">
            <div 
              className="w-10 h-10 rounded-full flex items-center justify-center"
              style={{ backgroundColor: colors.mainGreen1 }}
            >
              <span className="text-white">AI</span>
            </div>
            <div>
              <h3 className="text-base" style={{ color: colors.textDark }}>
                늘봄 챗봇
              </h3>
              <p className="text-xs" style={{ color: colors.textSub }}>
                항상 함께합니다
              </p>
            </div>
          </div>
          
          {showCrisisPanel && (
            <div className="flex items-center space-x-2 px-3 py-1 rounded-full" style={{ backgroundColor: colors.error + '20' }}>
              <AlertTriangle size={16} style={{ color: colors.error }} />
              <span className="text-xs" style={{ color: colors.error }}>
                위기 감지됨
              </span>
            </div>
          )}
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-6">
          <div className="max-w-4xl mx-auto">
            {messages.map((msg) => (
              <ChatBubble
                key={msg.id}
                message={msg.message}
                isUser={msg.isUser}
                timestamp={msg.timestamp}
              />
            ))}
          </div>
        </div>

        {/* Input Area */}
        <div className="bg-white border-t p-4" style={{ borderColor: colors.lightGray }}>
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
            >
              <Send size={20} color={colors.white} />
            </button>
          </div>
        </div>
      </div>

      {/* Right Sidebar - Crisis Detection Panel */}
      {showCrisisPanel && (
        <div className="w-80 bg-white border-l p-4 hidden xl:block" style={{ borderColor: colors.lightGray }}>
          <CrisisPanel />
        </div>
      )}
    </div>
  );
}
