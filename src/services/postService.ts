// src/services/postService.ts
// Post 타입 & 초기 더미 데이터 저장

// 댓글
export interface Comment {
    id: number;
    content: string;
    date: string;
}

export interface Post {
  id: number;
  title: string;
  preview: string;
  tags: string[];
  date: string;
  commentCount: number;
  hasCrisisFlag?: boolean;

  comments: Comment[]; // 댓글 리스트 추가
}

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

export const initialPosts: Post[] = [
  {
    id: 1,
    title: '노인 돌봄 경험 공유합니다',
    preview:
      '부모님 돌봄을 시작한 지 3년째입니다. 처음에는 많이 힘들었지만 지금은 여러 복지 서비스를 통해 많은 도움을 받고 있습니다...',
    tags: ['노인돌봄', '경험공유'],
    date: '2025.11.22',
    commentCount: 15,
    comments: initialComments
  },
  {
    id: 2,
    title: '장애인 활동지원 서비스 후기',
    preview:
      '활동지원사님이 오시면서 많은 부담이 줄었어요. 같은 상황의 분들께 도움이 되길 바라며 후기 남깁니다...',
    tags: ['장애인지원', '후기'],
    date: '2025.11.21',
    commentCount: 8,
    hasCrisisFlag: false,
    comments: initialComments
  },
  {
    id: 3,
    title: '요즘 너무 힘들어요',
    preview:
      '돌봄을 하다 보니 제 시간이 없고, 친구들도 만나지 못하고... 우울한 기분이 계속됩니다...',
    tags: ['고민상담'],
    date: '2025.11.21',
    commentCount: 23,
    hasCrisisFlag: true,
    comments: initialComments
  },
  {
    id: 4,
    title: '지역별 돌봄센터 정보 정리',
    preview:
      '서울 지역 돌봄센터 정보를 정리해봤습니다. 필요하신 분들께 도움이 되면 좋겠습니다...',
    tags: ['정보공유', '서울'],
    date: '2025.11.20',
    commentCount: 12,
    comments: initialComments
  },
];
