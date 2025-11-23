from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.models.connection import init_db, SessionLocal
from app.api.endpoints import auth, chat, welfare, community
from app.ai_core.rag_engine import load_welfares_to_vector_db
import logging
import os

# 로깅 설정 (임시로 INFO로 변경하여 디버깅)
logging.basicConfig(
    level=logging.INFO,  # 임시로 INFO로 변경하여 토큰 검증 문제 디버깅
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# FastAPI 앱 생성
app = FastAPI(
    title="늘봄 API",
    description="AI 정서 지원 및 복지 정보 매칭 플랫폼",
    version="1.0.0"
)

# 정적 파일 및 템플릿 설정
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
static_dir = os.path.join(BASE_DIR, "static")
templates_dir = os.path.join(BASE_DIR, "templates")

# 디렉토리가 없으면 생성
os.makedirs(static_dir, exist_ok=True)
os.makedirs(templates_dir, exist_ok=True)

# 정적 파일 마운트
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# 템플릿 엔진 설정
templates = Jinja2Templates(directory=templates_dir)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # 프론트엔드 개발 서버
        "http://127.0.0.1:3000",
        "http://localhost:5173",  # Vite 기본 포트 (백업)
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 데이터베이스 초기화
@app.on_event("startup")
async def startup_event():
    """서버 시작 시 실행되는 초기화 함수"""
    # 1. 데이터베이스 초기화
    init_db()
    # 성능 최적화: INFO 로그 제거 (필요시만 WARNING/ERROR 로깅)
    
    # 2. LLM 클라이언트 초기화 확인
    from app.ai_core.llm_client import llm_client
    # 성능 최적화: INFO 로그 제거
    
    # 3. 벡터 DB 초기화 (DB 데이터를 FAISS 인덱스에 로드)
    # 빠른 시작을 위해 벡터 DB 로딩 임시 비활성화 (필요시 주석 해제)
    # 성능 최적화: INFO 로그 제거
    # try:
    #     db = SessionLocal()
    #     try:
    #         load_welfares_to_vector_db(db, force_rebuild=False)
    #     except Exception as e:
    #         logger.error(f"벡터 DB 초기화 실패: {e}")
    #         logger.warning("벡터 검색 기능이 제한될 수 있습니다.")
    #     finally:
    #         db.close()
    # except Exception as e:
    #     logger.error(f"벡터 DB 초기화 중 오류: {e}")


# 라우터 등록
app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(welfare.router)
app.include_router(community.router)


# 웹 UI 라우트
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """메인 웹 페이지"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health")
def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
