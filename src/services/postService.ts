// src/services/postService.ts

// 댓글
export interface Comment {
  id: number;
  content: string;
  date: string;
}

// 커뮤니티 카테고리
export type PostCategory = 'info' | 'counsel' | 'free';

export interface Post {
  id: number;
  title: string;
  preview: string;
  // tags: string[];
  date: string;          // 화면에 보이는 날짜 문자열
  commentCount: number;
  hasCrisisFlag?: boolean;

  comments: Comment[];   // 댓글 리스트

  // === 좋아요 / 북마크 / 카테고리 (백엔드 연동용) ===
  category: PostCategory;   // 'info' | 'counsel' | 'free'
  likeCount: number;        // 좋아요 수
  isLiked: boolean;         // 내가 좋아요 눌렀는지
  isBookmarked: boolean;    // 내가 북마크 했는지
}

// 초기 댓글
export const initialComments: Comment[] = [
  {
    id: 1,
    content: '저도 비슷한 경험을 했습니다. 힘내세요!',
    date: '2025.11.21 15:30',
  },
  {
    id: 2,
    content: '지역 복지센터에 문의해보시면 도움을 받으실 수 있을 거예요.',
    date: '2025.11.21 16:20',
  },
  {
    id: 3,
    content: '함께 이겨나가요. 혼자가 아니니까요.',
    date: '2025.11.21 17:45',
  },
];

// 내부에서 관리하는 더미 데이터 (나중에 API 응답으로 대체 예정)
let postsStore: Post[] = [
  {
    id: 1,
    title: '노인 돌봄 경험 공유합니다',
    preview:
      '부모님 돌봄을 시작한 지 3년째입니다. 처음에는 많이 힘들었지만 지금은 여러 복지 서비스를 통해 많은 도움을 받고 있습니다...',
    // tags: ['노인돌봄', '경험공유'],
    date: '2025.11.22',
    commentCount: 15,
    hasCrisisFlag: false,
    comments: initialComments,
    category: 'info',      // 정보공유 느낌
    likeCount: 32,
    isLiked: false,
    isBookmarked: false,
  },
  {
    id: 2,
    title: '장애인 활동지원 서비스 후기',
    preview:
      '활동지원사님이 오시면서 많은 부담이 줄었어요. 같은 상황의 분들께 도움이 되길 바라며 후기 남깁니다...',
    // tags: ['장애인지원', '후기'],
    date: '2025.11.21',
    commentCount: 8,
    hasCrisisFlag: false,
    comments: initialComments,
    category: 'info',      // 정보공유
    likeCount: 21,
    isLiked: false,
    isBookmarked: false,
  },
  {
    id: 3,
    title: '요즘 너무 힘들어요',
    preview:
      '돌봄을 하다 보니 제 시간이 없고, 친구들도 만나지 못하고... 우울한 기분이 계속됩니다...',
    // tags: ['고민상담'],
    date: '2025.11.21',
    commentCount: 23,
    hasCrisisFlag: true,
    comments: initialComments,
    category: 'counsel',   // 고민상담
    likeCount: 54,
    isLiked: false,
    isBookmarked: false,
  },
  {
    id: 4,
    title: '지역별 돌봄센터 정보 정리',
    preview:
      '서울 지역 돌봄센터 정보를 정리해봤습니다. 필요하신 분들께 도움이 되면 좋겠습니다...',
    // tags: ['정보공유', '서울'],
    date: '2025.11.20',
    commentCount: 12,
    hasCrisisFlag: false,
    comments: initialComments,
    category: 'info',      // 정보공유
    likeCount: 17,
    isLiked: false,
    isBookmarked: false,
  },
];

// ======================
// 서비스 함수들
// ======================

// 게시글 목록 가져오기
export async function fetchPosts(): Promise<Post[]> {
  // 나중에: const res = await axios.get('/api/posts'); return res.data;
  return Promise.resolve(postsStore);
}

// 좋아요 토글
export async function toggleLike(postId: number): Promise<Post | null> {
  // 나중에: const res = await axios.post(`/api/posts/${postId}/like`); return res.data;

  postsStore = postsStore.map((p) =>
    p.id === postId
      ? {
          ...p,
          isLiked: !p.isLiked,
          likeCount: p.isLiked ? p.likeCount - 1 : p.likeCount + 1,
        }
      : p,
  );
  const updated = postsStore.find((p) => p.id === postId) ?? null;
  return Promise.resolve(updated);
}

// 북마크 토글
export async function toggleBookmark(postId: number): Promise<Post | null> {
  // 나중에: const res = await axios.post(`/api/posts/${postId}/bookmark`); return res.data;

  postsStore = postsStore.map((p) =>
    p.id === postId ? { ...p, isBookmarked: !p.isBookmarked } : p,
  );
  const updated = postsStore.find((p) => p.id === postId) ?? null;
  return Promise.resolve(updated);
}