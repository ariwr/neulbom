# 늘봄 프론트엔드

AI 정서 지원 및 복지 정보 매칭 플랫폼 프론트엔드 (React + TypeScript + Vite)

## 기술 스택

- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite
- **UI Library**: Radix UI + Tailwind CSS
- **State Management**: React Hooks

## 프로젝트 구조

```
neulbom-frontend/
├── src/
│   ├── components/      # 재사용 가능한 컴포넌트
│   ├── pages/          # 페이지 컴포넌트
│   ├── services/        # API 서비스 레이어
│   ├── config/         # 설정 파일 (API 설정 등)
│   └── styles/         # 스타일 파일
├── package.json
└── vite.config.ts
```

## 설치 및 실행

### 1. 의존성 설치

```bash
npm install
```

### 2. 환경 변수 설정 (선택사항)

`.env` 파일을 생성하여 API 서버 주소를 설정할 수 있습니다:

```env
VITE_API_BASE_URL=http://localhost:8000
```

기본값은 `http://localhost:8000`입니다.

### 3. 개발 서버 실행

```bash
npm run dev
```

프론트엔드는 `http://localhost:3000`에서 실행됩니다.

### 4. 백엔드 서버 실행

별도 터미널에서 백엔드 서버를 실행해야 합니다:

```bash
cd ../neulbom-backend
# 가상환경 활성화 후
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API 연결

프론트엔드는 백엔드 API와 자동으로 연결됩니다:
- **개발 환경**: Vite 프록시를 통해 `/api` 요청이 `http://localhost:8000`으로 전달됩니다.
- **프로덕션**: `.env` 파일의 `VITE_API_BASE_URL`을 사용합니다.

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
- `GET /api/chat/rooms` - 채팅방 목록 조회
- 채팅방 관리 (생성/수정/삭제)

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
- 게시글 수정/삭제
- 좋아요/북마크 기능
- 댓글 기능

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

## 빌드

프로덕션 빌드:

```bash
npm run build
```

빌드된 파일은 `build/` 디렉토리에 생성됩니다.

## 개발 가이드

### API 서비스 추가

새로운 API 엔드포인트를 사용하려면 `src/services/` 디렉토리에 서비스 파일을 추가하고 `src/config/api.ts`의 헬퍼 함수를 사용하세요:

```typescript
import { apiGet, apiPost } from '../config/api';

export async function fetchData() {
  return apiGet<DataType>('/api/endpoint');
}
```

### 인증 토큰 관리

인증 토큰은 자동으로 localStorage에 저장되며, API 호출 시 자동으로 헤더에 포함됩니다.

```typescript
import { getAuthToken, setAuthToken } from '../config/api';

// 토큰 가져오기
const token = getAuthToken();

// 토큰 설정
setAuthToken('new-token');
```

## 문제 해결

### CORS 오류

백엔드 서버의 CORS 설정이 프론트엔드 포트(`http://localhost:3000`)를 허용하는지 확인하세요.

### API 연결 실패

1. 백엔드 서버가 실행 중인지 확인 (`http://localhost:8000`)
2. `.env` 파일의 `VITE_API_BASE_URL`이 올바른지 확인
3. 브라우저 개발자 도구의 Network 탭에서 요청 상태 확인

## 라이선스

MIT
