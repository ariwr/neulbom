// services/chatService.ts
export interface ChatConversation {
  id: number;
  title: string;
  createdAt: string;        // ISO 문자열
  // lastMessageAt?: string;
}

export interface ChatMessage {
  id: number;
  conversationId: number;
  content: string;
  isUser: boolean;
  timestamp: string;
}

// ---- 더미 데이터 (나중에 API 응답으로 교체) ----
const MOCK_CONVERSATIONS: ChatConversation[] = [
  { id: 1, title: '복지 서비스 문의', createdAt: '2025.11.20' },
  { id: 2, title: '돌봄 스트레스 상담', createdAt: '2025.11.19' },
  { id: 3, title: '지역 자원 안내',   createdAt: '2025.11.18' },
];

const MOCK_MESSAGES: ChatMessage[] = [
  { id: 1, conversationId: 1, content: '안녕하세요! 오늘은 어떤 도움이 필요하신가요?', isUser: false, timestamp: '14:30' },
  { id: 2, conversationId: 1, content: '요즘 부모님 돌봄이 너무 힘들어요. 어떤 지원을 받을 수 있을까요?', isUser: true, timestamp: '14:32' },
  { id: 3, conversationId: 1, content: '거주 지역과 부모님 연령대를 알려주시면 맞춤 복지 서비스를 안내해드릴게요.', isUser: false, timestamp: '14:33' },
  { id: 4, conversationId: 1, content: '서울 강남구이고, 어머니는 75세이십니다', isUser: true, timestamp: '14:35' },
];

// 실제로는 API 호출 자리가 될 함수들
export async function fetchConversations(): Promise<ChatConversation[]> {
  // return fetch('/api/conversations').then(r => r.json());
  return Promise.resolve(MOCK_CONVERSATIONS);
}

export async function fetchMessages(conversationId: number): Promise<ChatMessage[]> {
  // return fetch(`/api/conversations/${conversationId}/messages`).then(r => r.json());
  return Promise.resolve(
    MOCK_MESSAGES.filter((m) => m.conversationId === conversationId),
  );
}

export async function createConversation(title?: string): Promise<ChatConversation> {
  const now = new Date();
  const newConv: ChatConversation = {
    id: Date.now(), // 나중에 백엔드가 id 생성
    title: title || '새 대화',
    createdAt: now.toISOString(),
  };

  MOCK_CONVERSATIONS.unshift(newConv); // 맨 위에 추가
  return Promise.resolve(newConv);
}

export async function renameConversation(id: number, title: string): Promise<void> {
  // await fetch(`/api/conversations/${id}`, { method: 'PATCH', body: JSON.stringify({ title }) });
  const target = MOCK_CONVERSATIONS.find((c) => c.id === id);
  if (target) target.title = title;
}

export async function deleteConversation(id: number): Promise<void> {
  // await fetch(`/api/conversations/${id}`, { method: 'DELETE' });
  const idx = MOCK_CONVERSATIONS.findIndex((c) => c.id === id);
  if (idx >= 0) MOCK_CONVERSATIONS.splice(idx, 1);
}

export async function sendMessage(
  conversationId: number,
  text: string,
): Promise<ChatMessage[]> {
  // 1) 여기에서 백엔드에 user 메시지 보내고
  // 2) 백엔드가 만든 assistant 응답 함께 받아서 리턴하는 구조로 설계하면 좋음
  // const res = await fetch(`/api/conversations/${conversationId}/messages`, { ... });

  const userMsg: ChatMessage = {
    id: Date.now(),
    conversationId,
    content: text,
    isUser: true,
    timestamp: '15:00',
  };

  const botMsg: ChatMessage = {
    id: Date.now() + 1,
    conversationId,
    content: '테스트 응답입니다 (나중에 AI 응답으로 교체)',
    isUser: false,
    timestamp: '15:00',
  };

  MOCK_MESSAGES.push(userMsg, botMsg);
  return Promise.resolve([userMsg, botMsg]);
}
