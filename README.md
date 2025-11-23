# 늘봄 백엔드 API

AI 정서 지원 및 복지 정보 매칭 플랫폼 백엔드 서버

## 기술 스택

- **Framework**: FastAPI
- **Database**: SQLite (SQLAlchemy ORM)
- **Authentication**: JWT (JSON Web Token)
- **AI**: Gemini / Upstage (챗봇, RAG)

## 프로젝트 구조

```
neulbom-backend/
├── app/
│   ├── main.py              # FastAPI 앱 진입점
│   ├── database.py          # DB 연결 설정
│   ├── models.py            # DB 모델 정의
│   ├── schemas.py           # Pydantic 스키마
│   ├── crud.py              # CRUD 함수
│   ├── core/
│   │   ├── config.py        # 환경변수 설정
│   │   └── security.py      # JWT 인증
│   ├── routers/
│   │   ├── auth.py          # 인증 API
│   │   ├── chat.py          # 챗봇 API
│   │   ├── welfare.py       # 복지 정보 API
│   │   └── community.py     # 커뮤니티 API
│   └── services/
│       ├── llm_chat.py      # AI 챗봇 로직
│       └── rag_search.py    # RAG 검색 로직
├── data/                    # RAG용 데이터
├── requirements.txt         # Python 의존성
└── .env.example            # 환경변수 예시
```

## 설치 및 실행

### 1. 가상환경 생성 및 활성화

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 2. 의존성 설치

```bash
pip install -r requirements.txt
```

### 3. 환경변수 설정

`.env.example`을 참고하여 `.env` 파일을 생성하고 필요한 값들을 설정하세요:

```bash
# .env 파일 생성
cp .env.example .env

# .env 파일 편집
# GEMINI_API_KEY=your-gemini-api-key
# UPSTAGE_API_KEY=your-upstage-api-key
# DEFAULT_LLM_PROVIDER=gemini  # 또는 upstage
# SECRET_KEY=your-secret-key
```

### 4. 데이터베이스 초기화

앱을 실행하면 자동으로 SQLite 데이터베이스가 생성됩니다.

### 5. 서버 실행

```bash
# 개발 모드
uvicorn app.main:app --reload

# 또는
python -m uvicorn app.main:app --reload
```

서버는 `http://localhost:8000`에서 실행됩니다.

### 6. 프론트엔드와 함께 실행

프론트엔드와 함께 실행하려면:

1. **백엔드 서버 실행** (현재 터미널):
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **프론트엔드 서버 실행** (새 터미널):
   ```bash
   cd ../neulbom-frontend
   npm install
   npm run dev
   ```

프론트엔드는 `http://localhost:3000`에서 실행되며, 백엔드 API(`http://localhost:8000`)와 자동으로 연결됩니다.

### 7. API 문서 확인

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API 엔드포인트

### 인증 (Auth)

- `POST /api/auth/signup` - 회원가입 (Level 2 부여)
- `POST /api/auth/login` - 로그인 (JWT 토큰 발급)
- `GET /api/users/me` - 내 프로필 조회
- `PUT /api/users/me` - 내 프로필 수정

### AI 챗봇 (Chat)

- `POST /api/chat/message` - 챗봇 메시지 전송
  - Level 1 (비회원) 이상 접근 가능

### 복지 정보 (Welfare)

- `GET /api/welfare/search` - 복지 정보 검색
  - Level 1 (비회원) 이상 접근 가능
- `POST /api/welfare/{id}/bookmark` - 북마크 저장
  - Level 2 (일반 회원) 이상 접근 가능

### 커뮤니티 (Community)

- `POST /api/community/verify` - 커뮤니티 심사 제출
  - Level 2 (일반 회원) 이상 접근 가능
- `POST /api/community/posts` - 게시글 작성
  - Level 3 (검증 회원) 이상 접근 가능
- `GET /api/community/posts` - 게시글 목록 조회
  - Level 3 (검증 회원) 이상 접근 가능

## 등급 시스템

- **Level 1 (비회원)**: 챗봇, 복지 검색 접근 가능
- **Level 2 (일반 회원)**: Level 1 기능 + 복지 정보 북마크 기능
- **Level 3 (검증 회원)**: Level 2 기능 + 커뮤니티 접근 가능

## 주요 기능

### 1. 웹 UI 통합
- **단일 서버**: 백엔드 API와 프론트엔드 웹 UI가 하나의 서버에서 실행
- **반응형 디자인**: 모바일과 데스크톱 모두 지원
- **실시간 상호작용**: JavaScript를 통한 API 호출 및 동적 UI 업데이트

### 2. JWT 인증
- 회원가입/로그인 시 JWT 토큰 발급
- 토큰 기반 인증으로 API 접근 제어
- 웹 UI에서 자동 토큰 관리 및 사용자 상태 유지

### 3. AI 챗봇
- 공감형 대화 생성
- 위기 감지 시스템 (키워드 기반)
- 고위험 상황 시 전문기관 연결 안내
- 웹 UI에서 실시간 채팅 인터페이스 제공

### 4. 복지 정보 검색
- 키워드/지역/나이 기반 검색
- 사용자 프로필 기반 맞춤형 필터링
- 북마크 기능 (Level 2 이상)

### 5. 커뮤니티
- 익명 게시판
- AI 기반 위기 감지 모니터링
- 등급 기반 접근 제어 (Level 3 이상)

## LLM API 설정

### 지원하는 LLM Provider
- **Gemini** (Google): 기본 제공자
- **Upstage**: 한국어 최적화 LLM

### 사용 방법
1. `.env` 파일에 API 키 설정:
   ```env
   GEMINI_API_KEY=your-gemini-api-key
   UPSTAGE_API_KEY=your-upstage-api-key
   DEFAULT_LLM_PROVIDER=gemini  # 또는 upstage
   ```

2. 코드에서 특정 provider 지정 (선택사항):
   ```python
   # Gemini 사용
   response = llm_client.generate_chat_response(
       message="안녕하세요",
       history=[],
       system_prompt="...",
       provider="gemini"
   )
   
   # Upstage 사용
   response = llm_client.generate_chat_response(
       message="안녕하세요",
       history=[],
       system_prompt="...",
       provider="upstage"
   )
   ```

## TODO

- [x] LLM API 통합 (Gemini/Upstage)
- [ ] RAG 벡터 DB 구축 (Chroma/FAISS)
- [ ] 복지 정보 크롤링 및 데이터 파이프라인
- [ ] AI 심사 프로세스 구현
- [ ] 관리자 알림 시스템
- [ ] 프로덕션 환경 설정

## 라이선스

MIT

