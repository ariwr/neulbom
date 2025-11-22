import React from 'react';
import { colors } from '../styles/design-tokens';

interface ChatBubbleProps {
  message: string;
  isUser: boolean;
  timestamp?: string;
  hasCrisisDetection?: boolean;
}

export function ChatBubble({ message, isUser, timestamp, hasCrisisDetection }: ChatBubbleProps) {
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div className={`max-w-[70%] ${isUser ? 'order-2' : 'order-1'}`}>
        {/* Avatar placeholder */}
        {!isUser && (
          <div 
            className="w-8 h-8 rounded-full mb-2 flex items-center justify-center"
            style={{ backgroundColor: colors.mainGreen1 }}
          >
            <span className="text-xs text-white">AI</span>
          </div>
        )}
        
        {/* Message bubble */}
        <div
          className="rounded-2xl px-4 py-3 shadow-sm"
          style={{
            backgroundColor: isUser ? colors.mainGreen2 : colors.white,
            color: isUser ? colors.white : colors.textDark,
          }}
        >
          <p className="text-sm">{message}</p>
          
          {hasCrisisDetection && (
            <div 
              className="mt-2 pt-2 border-t text-xs"
              style={{ borderColor: colors.error, color: colors.error }}
            >
              ⚠️ 위기 상황 감지
            </div>
          )}
        </div>

        {/* Timestamp */}
        {timestamp && (
          <p className="text-xs mt-1 px-2" style={{ color: colors.textSub }}>
            {timestamp}
          </p>
        )}
      </div>
    </div>
  );
}
