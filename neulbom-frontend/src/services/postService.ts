// src/services/postService.ts
import { apiGet, apiPost, apiPut, apiDelete } from '../config/api';

// 댓글
export interface Comment {
  id: number;
  content: string;
  date: string;
}

// 커뮤니티 카테고리
export type PostCategory = 'info' | 'counsel' | 'free';

// 백엔드 카테고리 매핑
const categoryMap: Record<PostCategory, string> = {
  info: 'information',
  counsel: 'worry',
  free: 'free',
};

const reverseCategoryMap: Record<string, PostCategory> = {
  information: 'info',
  worry: 'counsel',
  free: 'free',
};

export interface Post {
  id: number;
  title: string;
  content: string;
  preview?: string;
  date: string;
  commentCount: number;
  hasCrisisFlag?: boolean;
  comments?: Comment[];
  category: PostCategory;
  likeCount: number;
  isLiked: boolean;
  isBookmarked: boolean;
  authorId?: number; // 작성자 ID 추가
}

// 백엔드 PostResponse를 프론트엔드 Post로 변환
function transformPost(backendPost: any): Post {
  return {
    id: backendPost.id,
    title: backendPost.title,
    content: backendPost.content,
    preview: backendPost.content.substring(0, 100) + '...',
    date: new Date(backendPost.created_at).toLocaleDateString('ko-KR'),
    commentCount: backendPost.comment_count || 0,
    hasCrisisFlag: false, // 백엔드에서 제공하지 않으면 false
    category: reverseCategoryMap[backendPost.category] || 'free',
    likeCount: backendPost.like_count || 0,
    isLiked: backendPost.is_liked || false,
    isBookmarked: backendPost.is_bookmarked || false,
    authorId: backendPost.author_id, // 작성자 ID 매핑 (백엔드가 author_id를 보내준다면)
  };
}

// 게시글 목록 가져오기
export async function fetchPosts(category?: PostCategory, sort: 'latest' | 'popular' = 'latest'): Promise<Post[]> {
  try {
    const params = new URLSearchParams();
    if (category && categoryMap[category]) {
      params.append('category', categoryMap[category]);
    }
    params.append('sort', sort);
    params.append('limit', '100'); // 충분히 많은 게시글 가져오기

    const endpoint = `/api/community/posts?${params.toString()}`;
    const backendPosts = await apiGet<any[]>(endpoint);
    return backendPosts.map(transformPost);
  } catch (error) {
    console.error('게시글 목록 조회 실패:', error);
    throw error;
  }
}

// 게시글 상세 조회
export async function fetchPostDetail(postId: number): Promise<Post> {
  try {
    const backendPost = await apiGet<any>(`/api/community/posts/${postId}`);
    const post = transformPost(backendPost);
    
    // 댓글 목록도 함께 가져오기
    try {
      const comments = await apiGet<any[]>(`/api/community/posts/${postId}/comments`);
      post.comments = comments.map(c => ({
        id: c.id,
        content: c.content,
        date: new Date(c.created_at).toLocaleString('ko-KR'),
      }));
    } catch (error) {
      console.error('댓글 조회 실패:', error);
      post.comments = [];
    }
    
    return post;
  } catch (error) {
    console.error('게시글 상세 조회 실패:', error);
    throw error;
  }
}

// 게시글 작성
export async function createPost(title: string, content: string, category: PostCategory = 'free'): Promise<Post> {
  try {
    const backendPost = await apiPost<any>('/api/community/posts', {
      title,
      content,
      category: categoryMap[category],
    });
    return transformPost(backendPost);
  } catch (error: any) {
    console.error('게시글 작성 실패:', error);
    // 401 에러인 경우 더 명확한 메시지
    if (error?.status === 401) {
      const authError = new Error('로그인이 필요합니다.') as Error & { status?: number };
      authError.status = 401;
      throw authError;
    }
    throw error;
  }
}

// 게시글 수정
export async function updatePost(postId: number, title: string, content: string, category: PostCategory = 'free'): Promise<Post> {
  try {
    const backendPost = await apiPut<any>(`/api/community/posts/${postId}`, {
      title,
      content,
      category: categoryMap[category],
    });
    return transformPost(backendPost);
  } catch (error) {
    console.error('게시글 수정 실패:', error);
    throw error;
  }
}

// 게시글 삭제
export async function deletePost(postId: number): Promise<void> {
  try {
    await apiDelete(`/api/community/posts/${postId}`);
  } catch (error) {
    console.error('게시글 삭제 실패:', error);
    throw error;
  }
}

// 좋아요 토글
export async function toggleLike(postId: number): Promise<Post | null> {
  try {
    await apiPost(`/api/community/posts/${postId}/like`);
    // 좋아요 후 게시글 다시 조회
    return await fetchPostDetail(postId);
  } catch (error) {
    console.error('좋아요 토글 실패:', error);
    throw error;
  }
}

// 북마크 토글
export async function toggleBookmark(postId: number): Promise<Post | null> {
  try {
    await apiPost(`/api/community/posts/${postId}/bookmark`);
    // 북마크 후 게시글 다시 조회
    return await fetchPostDetail(postId);
  } catch (error) {
    console.error('북마크 토글 실패:', error);
    throw error;
  }
}

// 댓글 작성
export async function createComment(postId: number, content: string): Promise<Comment> {
  try {
    const response = await apiPost<any>(`/api/community/posts/${postId}/comments`, {
      content,
    });
    return {
      id: response.id,
      content: response.content,
      date: new Date(response.created_at).toLocaleString('ko-KR'),
    };
  } catch (error) {
    console.error('댓글 작성 실패:', error);
    throw error;
  }
}

// 초기 댓글 (더미 데이터)
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
