// services/chatService.ts
import { apiGet, apiPost, apiPut, apiDelete } from '../config/api';

export interface ChatConversation {
  id: number;
  title: string;
  created_at: string;
}

export interface ChatMessage {
  id?: number;
  conversationId: number;
  content: string;
  isUser: boolean;
  timestamp: string;
}

export interface ChatResponse {
  reply: string;
  is_crisis: boolean;
  crisis_info?: {
    phone?: string;
    message?: string;
  };
  room_id?: number;
}

// 채팅방 목록 가져오기 (로그인한 사용자만 가능)
export async function fetchConversations(): Promise<ChatConversation[]> {
  try {
    const response = await apiGet<{ items: ChatConversation[]; total: number }>('/api/chat/rooms');
    return response.items || [];
  } catch (error: any) {
    // 인증 오류(401) 또는 권한 없음(403)인 경우 빈 배열 반환 (조용히 처리)
    if (error?.status === 401 || error?.status === 403) {
      return [];
    }
    // 다른 오류는 콘솔에만 기록하고 빈 배열 반환
    console.error('채팅방 목록 조회 실패:', error);
    return [];
  }
}

// 채팅방 생성 (로그인한 사용자만 가능)
export async function createConversation(title?: string): Promise<ChatConversation> {
  try {
    const response = await apiPost<ChatConversation>('/api/chat/rooms', {
      title: title || '새 대화',
    });
    return response;
  } catch (error: any) {
    // 인증 오류인 경우 에러를 다시 throw하여 호출자가 처리할 수 있도록 함
    if (error?.status === 401 || error?.status === 403) {
      throw new Error('로그인이 필요합니다.');
    }
    throw error;
  }
}

// 채팅방 제목 수정 (로그인한 사용자만 가능)
export async function renameConversation(id: number, title: string): Promise<void> {
  try {
    await apiPut(`/api/chat/rooms/${id}`, { title });
  } catch (error: any) {
    if (error?.status === 401 || error?.status === 403) {
      throw new Error('로그인이 필요합니다.');
    }
    throw error;
  }
}

// 채팅방 삭제 (로그인한 사용자만 가능)
export async function deleteConversation(id: number): Promise<void> {
  try {
    await apiDelete(`/api/chat/rooms/${id}`);
  } catch (error: any) {
    if (error?.status === 401 || error?.status === 403) {
      throw new Error('로그인이 필요합니다.');
    }
    throw error;
  }
}

// 메시지 전송 (실제로는 메시지 히스토리를 직접 가져올 수 없으므로, 전송만 처리)
export async function sendMessage(
  conversationId: number | null,
  text: string,
  history: ChatMessage[] = []
): Promise<ChatResponse> {
  // 히스토리를 백엔드 형식으로 변환
  const formattedHistory = history.map(msg => ({
    role: msg.isUser ? 'user' : 'assistant',
    content: msg.content,
  }));

  const params = conversationId ? `?room_id=${conversationId}` : '';
  const response = await apiPost<ChatResponse>(`/api/chat/message${params}`, {
    message: text,
    history: formattedHistory,
  });

  return response;
}

// 메시지 목록 가져오기 (백엔드에 해당 API가 없으므로 빈 배열 반환)
// 실제 구현을 위해서는 백엔드에 메시지 히스토리 조회 API가 필요합니다
export async function fetchMessages(conversationId: number): Promise<ChatMessage[]> {
  // TODO: 백엔드에 메시지 히스토리 조회 API 추가 필요
  // 현재는 빈 배열 반환
  return Promise.resolve([]);
}
