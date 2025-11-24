// services/chatService.ts
import { apiGet, apiPost, apiPut, apiDelete, getAuthToken } from '../config/api';

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

// 비회원 채팅방 타입 (로컬 저장용)
export interface LocalChatConversation {
  id: string; // 음수 ID 또는 UUID
  title: string;
  created_at: string;
  messages: ChatMessage[];
}

// 비회원 채팅방 관리 (localStorage)
const LOCAL_CHAT_STORAGE_KEY = 'neulbom_local_chats';

export function getLocalChats(): LocalChatConversation[] {
  try {
    const stored = localStorage.getItem(LOCAL_CHAT_STORAGE_KEY);
    return stored ? JSON.parse(stored) : [];
  } catch {
    return [];
  }
}

export function saveLocalChats(chats: LocalChatConversation[]): void {
  try {
    localStorage.setItem(LOCAL_CHAT_STORAGE_KEY, JSON.stringify(chats));
  } catch (error) {
    console.error('로컬 채팅 저장 실패:', error);
  }
}

export function createLocalChat(title: string = '새 대화'): LocalChatConversation {
  const chats = getLocalChats();
  const newId = `local_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  const newChat: LocalChatConversation = {
    id: newId,
    title,
    created_at: new Date().toISOString(),
    messages: [],
  };
  chats.unshift(newChat);
  saveLocalChats(chats);
  return newChat;
}

export function updateLocalChat(id: string, updates: Partial<LocalChatConversation>): void {
  const chats = getLocalChats();
  const index = chats.findIndex(c => c.id === id);
  if (index !== -1) {
    chats[index] = { ...chats[index], ...updates };
    saveLocalChats(chats);
  }
}

export function deleteLocalChat(id: string): void {
  const chats = getLocalChats();
  const filtered = chats.filter(c => c.id !== id);
  saveLocalChats(filtered);
}

export function addMessageToLocalChat(id: string, message: ChatMessage): void {
  const chats = getLocalChats();
  const chat = chats.find(c => c.id === id);
  if (chat) {
    chat.messages.push(message);
    saveLocalChats(chats);
  }
}

export function getLocalChatMessages(id: string): ChatMessage[] {
  const chats = getLocalChats();
  const chat = chats.find(c => c.id === id);
  return chat ? chat.messages : [];
}

// 로그인 상태 확인
export function isLoggedIn(): boolean {
  return !!getAuthToken();
}

// 채팅방 목록 가져오기 (로그인한 사용자는 서버에서, 비회원은 로컬에서)
export async function fetchConversations(): Promise<ChatConversation[]> {
  if (!isLoggedIn()) {
    // 비회원: 로컬 채팅방을 서버 형식으로 변환
    const localChats = getLocalChats();
    return localChats.map(chat => ({
      id: parseInt(chat.id.replace('local_', '').split('_')[0]) || 0, // 임시 ID
      title: chat.title,
      created_at: chat.created_at,
    }));
  }
  
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

// 채팅방 생성 (로그인한 사용자는 서버에, 비회원은 로컬에)
// 시연용: 항상 로그인된 상태이므로 서버에 생성 시도, 실패 시 로컬로 폴백
export async function createConversation(title?: string): Promise<ChatConversation> {
  // 시연용: 항상 로그인된 상태이므로 서버에 생성 시도
  try {
    const response = await apiPost<ChatConversation>('/api/chat/rooms', {
      title: title || '새 대화',
    });
    return response;
  } catch (error: any) {
    // 시연용: 서버 생성 실패 시 로컬 채팅방으로 폴백
    console.log('서버 채팅방 생성 실패, 로컬 채팅방으로 폴백:', error);
    const localChat = createLocalChat(title || '새 대화');
    return {
      id: parseInt(localChat.id.replace('local_', '').split('_')[0]) || Date.now(),
      title: localChat.title,
      created_at: localChat.created_at,
    };
  }
}

// 채팅방 제목 수정 (로그인한 사용자는 서버에서, 비회원은 로컬에서)
export async function renameConversation(id: number, title: string): Promise<void> {
  if (!isLoggedIn()) {
    // 비회원: 로컬 채팅방 제목 수정
    const localChats = getLocalChats();
    const localChat = localChats.find(c => c.id === `local_${id}` || c.id.startsWith('local_'));
    if (localChat) {
      updateLocalChat(localChat.id, { title });
      return;
    }
    throw new Error('채팅방을 찾을 수 없습니다.');
  }
  
  try {
    await apiPut(`/api/chat/rooms/${id}`, { title });
  } catch (error: any) {
    if (error?.status === 401 || error?.status === 403) {
      throw new Error('로그인이 필요합니다.');
    }
    throw error;
  }
}

// 채팅방 삭제 (로그인한 사용자는 서버에서, 비회원은 로컬에서)
export async function deleteConversation(id: number): Promise<void> {
  if (!isLoggedIn()) {
    // 비회원: 로컬 채팅방 삭제
    const localChats = getLocalChats();
    const localChat = localChats.find(c => c.id === `local_${id}` || c.id.startsWith('local_'));
    if (localChat) {
      deleteLocalChat(localChat.id);
      return;
    }
    throw new Error('채팅방을 찾을 수 없습니다.');
  }
  
  try {
    await apiDelete(`/api/chat/rooms/${id}`);
  } catch (error: any) {
    if (error?.status === 401 || error?.status === 403) {
      throw new Error('로그인이 필요합니다.');
    }
    throw error;
  }
}

// 메시지 전송 (로그인한 사용자는 서버에 저장, 비회원은 로컬에만 저장)
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

  const isLoggedInUser = isLoggedIn();
  
  // 비회원이고 conversationId가 null이면 로컬 채팅방 ID 사용
  let roomId = conversationId;
  if (!isLoggedInUser && conversationId === null) {
    // 비회원 새 채팅: 로컬 채팅방 생성
    const localChat = createLocalChat(text.substring(0, 30));
    roomId = parseInt(localChat.id.replace('local_', '').split('_')[0]) || 0;
  }

  // room_id 파라미터: 로그인한 사용자만 서버에 전달
  const params = (isLoggedInUser && roomId) ? `?room_id=${roomId}` : '';
  const response = await apiPost<ChatResponse>(`/api/chat/message${params}`, {
    message: text,
    history: formattedHistory,
  });

  // 비회원인 경우 로컬에 메시지 저장 (기록은 남지만 서버에는 저장 안됨)
  if (!isLoggedInUser && roomId) {
    const localChats = getLocalChats();
    const localChat = localChats.find(c => {
      const chatId = parseInt(c.id.replace('local_', '').split('_')[0]) || 0;
      return chatId === roomId;
    });
    
    if (localChat) {
      const userMsg: ChatMessage = {
        conversationId: roomId,
        content: text,
        isUser: true,
        timestamp: new Date().toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' }),
      };
      const botMsg: ChatMessage = {
        conversationId: roomId,
        content: response.reply,
        isUser: false,
        timestamp: new Date().toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' }),
      };
      addMessageToLocalChat(localChat.id, userMsg);
      addMessageToLocalChat(localChat.id, botMsg);
    }
  }

  return response;
}

// 메시지 목록 가져오기 (로그인한 사용자는 서버에서, 비회원은 로컬에서)
export async function fetchMessages(conversationId: number): Promise<ChatMessage[]> {
  if (!isLoggedIn()) {
    // 비회원: 로컬 채팅방에서 메시지 가져오기
    const localChats = getLocalChats();
    const localChat = localChats.find(c => {
      const chatId = parseInt(c.id.replace('local_', '').split('_')[0]) || 0;
      return chatId === conversationId;
    });
    return localChat ? localChat.messages : [];
  }
  
  // 로그인한 사용자: 백엔드에서 메시지 가져오기 (현재는 빈 배열)
  // TODO: 백엔드에 메시지 히스토리 조회 API 추가 필요
  return Promise.resolve([]);
}
