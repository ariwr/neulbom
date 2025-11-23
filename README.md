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

## 주요 기능

### 인증
- 회원가입 (`/api/auth/signup`)
- 로그인 (`/api/auth/login`)
- 프로필 조회/수정 (`/api/users/me`)

### 챗봇
- 채팅방 목록 조회 (`/api/chat/rooms`)
- 메시지 전송 (`/api/chat/message`)
- 채팅방 관리 (생성/수정/삭제)

### 복지 정보
- 복지 정보 검색 (`/api/welfare/search`)
- 북마크 기능 (`/api/welfare/{id}/bookmark`)

### 커뮤니티
- 게시글 목록 조회 (`/api/community/posts`)
- 게시글 작성/수정/삭제
- 좋아요/북마크 기능
- 댓글 기능

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
