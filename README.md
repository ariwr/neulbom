# 삼위일체 - 늘봄

## 서비스 요약
늘봄 – 가족돌봄청년(영케어러)을 위한 AI 정서 지원 및 맞춤형 복지 정보 통합 플랫폼

## 주제 구분
C타입 복지의 사각지대에 놓인 사람들 위한 서비스 (ex. 위안부, 6,25 참전 용사, 미숙아 등)

## 팀원 소개
삼위일체 – 김시연, 이유진, 임정민

## 시연 영상
Youtube 링크 - https://youtube.com/channel/UCqw83Hrrls5O79R8MEme8XA?si=5_2WC3I_xzrIDLtX

## 서비스 소개

### 서비스 개요
본 서비스는 복지의 사각지대에 놓인 가족돌봄청년(영케어러)을 대상으로 함. LLM기반으로 청년들의 이야기를 24시간 들어주고 공감하는 AI정서 지원 챗봇, 흩어져 있는 정부 지자체 복지 정보를 RAG 기술로 맞춤형 AI요약, 익명 커뮤니티 제공을 통해 안전한 환경에서 정서적 유대감 및 정보 교류를 지원하고 이들의 심리적 경제적 고립문제를 해결하는 AI기반 통합 솔루션임.

### 타서비스와의 차별점
1. 영커에러(가족돌봄청년) 특화 서비스  
   일반 복지 플랫폼은 전체 국민 대상이지만 늘봄은 영케어러만을 집중적 지원  
   영케어의 심리,경제적 고립 문제를 중심으로 설계된 콘텐츠를 제공

2. 정서지원+복지정보+커뮤니티가 하나로 통합된 유일한 플랫폼  
   기존 서비스는 심리 상담 또는 정보 검색 중심 분리 운영됨. 늘봄은 한 플랫폼에서 모두 제공함으로써 이용자의 편의성과 접근성을 극대화함

3. 100% 익명 안전 커뮤니티 제공  
   다른 커뮤니티는 닉네임, 프로필 기반이라 노출 위험이 있지만 늘봄은 완전 익명으로 안전한 공간에서 전문 복지정보와 실제 경험 정보를 자유롭게 교류할 수 있음.

4. LLM기반 정서 공감형 챗봇 + RAG기반 맞춤 복지 추천  
   기존 챗봇은 FAQ수준의 규칙 기반이지만 늘봄은 LLM을 통해 감정 공감 중심 대화를 제공하고 RAG를 통해 공공기관 복지자료를 기반으로 정확한 최신정보 요약, 추천함

5. 즉시 행동 연계 가능  
   복지 정보 확인 -> AI 요약 -> 신청 링크 연결 -> 상담전화 연동까지 한번에 이어지는 UX 제공

### 구현 내용 및 결과물
1. 커뮤니티  
   - 완전 익명 기반으로 누구나 안전한 커뮤니티 제공  
   - 정보공유, 고민상담으로 카테고리 나누어 편리한 사용 가능  
   - 좋아요와 북마크, 댓글 기능으로 사용자 간 소통과 정보 저장 지원

2. 마이페이지  
   - 복지 상담 전화 가이드가 제공되어 필요 시 바로 이용 가능  
   - 개인 정보 관리와 서비스 이용 내역 확인 가능

3. 챗봇  
   - AI와 자연스럽게 대화하며 정서적 공감 및 복지 정보 습득 가능  
   - 챗봇 대화 기록 삭제와 대화 제목 수정을 통해 개인정보 보호 강화

4. 메인탭(복지 서비스 검색)  
   - 로그인 후 즉시 메인 화면으로 이동해 빠르게 복지 서비스 검색 가능  
   - 복지 서비스 클릭 시 AI 요약과 신청 링크 연결을 한번에 제공해 편의성 향상  
   - 벡터 검색 시스템으로 복지 정보 벡터화 및 저장하고 유사도 기반 검색 가능  
   - 사용자 프로필 기반 자동 필터링과 페이지네이션 지원  
   - 인기 복지 정보, 최근 본 복지 정보, 신청 가능한 복지 정보 자동 추천

### 구현 방식
- Frontend - React.js(vite)  
- Backend - FastAPI(Python)  
- Database - SQLite  
- AI/RAG - FAISS/ChromaDB

### 향후 개선 혹은 발전 방안
1. 익명커뮤니티 내 자동 악성 게시물 필터링  
   욕설이나 폭력 등 위험 요소를 자동 차단하기 위해 유해 글 자동 분류 기능과 AI 모더레이션 기능 도입

2. 모바일 앱 개발  
   현재는 웹 기반이지만 iOS/Android 앱을 출시해 접근성 높임

3. 오프라인 기관 연계 시스템 구축  
   지역 복지센터와 협력하여 전문 상담사 연결을 통해 실제 오프라인 지원 체계 구축

4. 영케어러 특화 심리 관리 기능 추가  
   대화 기반 감정 분석을 통해 스트레스 지표 추정 후 주간 감정 리포트 및 맞춤 관리  
   부정적 감정 토로 시 CBT(인지행동치료) 유도해 긍정 심리학 기반의 감사 일기 및 사고 전환 유도 프롬프트 적용

5. 장기적으로 영케어러 데이터 기반 정책 제안  
   익명 통계 기반으로 영케어러의 주요 어려움, 지역별 격차, 지원 필요성 등을 분석해 정부와 협력해 정책 개선에 기여 가능

# 늘봄 프론트엔드

AI 정서 지원 및 복지 정보 매칭 플랫폼 프론트엔드 (React + TypeScript + Vite)

## Youtube
https://youtube.com/channel/UCqw83Hrrls5O79R8MEme8XA?si=5_2WC3I_xzrIDLtX

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
