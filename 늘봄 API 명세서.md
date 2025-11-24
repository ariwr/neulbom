# 늘봄 API 명세서

### 3.1 인증 (Auth)

- **POST** `/api/auth/signup`: 회원가입 (Level 2 부여).
- **POST** `/api/auth/login`: 로그인 (Access Token 발급).
- **GET** `/api/users/me`: 내 프로필(나이, 지역, 등급) 조회.

### 3.2 AI 챗봇 (Chat)

- **POST** `/api/chat/message`
    - **Body**: `{"message": "너무 힘들어", "history": [...]}`
    - **Response**:JSON
        
        `{
          "reply": "많이 지치셨군요... (공감 대화)",
          "is_crisis": true,
          "crisis_info": {"phone": "129", "message": "전문가의 도움이 필요해 보여요."}
        }`
        

### 3.3 복지 정보 (Welfare)

- **GET** `/api/welfare/search`
    - **Query**: `?keyword=장학금&region=서울`
    - **Response**:JSON
        
        `[
          {
            "id": 1,
            "title": "서울 희망 장학금",
            "summary": "서울 거주 대학생에게 학기당 100만원 지원. 성적 기준 없음.",
            "source_link": "http://..."
          }
        ]`
        
- **POST** `/api/welfare/{id}/bookmark`: 관심 정보 저장.

### 3.4 커뮤니티 (Community)

- **POST** `/api/community/verify`: 가입 심사글 제출 (Level 3 승급 요청).
- **POST** `/api/community/posts`: 게시글 작성 (AI 필터링 적용).
- **GET** `/api/community/posts`: 게시글 목록 조회.