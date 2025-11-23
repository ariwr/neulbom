from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.models.connection import init_db, SessionLocal
from app.api.endpoints import auth, chat, welfare, community, users
from app.ai_core.rag_engine import load_welfares_to_vector_db
import logging
import traceback

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# FastAPI 앱 생성
app = FastAPI(
    title="늘봄 API",
    description="AI 정서 지원 및 복지 정보 매칭 플랫폼",
    version="1.0.0"
)

# CORS 설정
from app.core.config import settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 전역 예외 핸들러 추가
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """전역 예외 핸들러 - 예상치 못한 오류 처리"""
    logger.error(f"예상치 못한 오류 발생: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "서버 내부 오류가 발생했습니다.",
            "error": str(exc) if logger.level <= logging.DEBUG else None
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """요청 검증 오류 핸들러"""
    logger.warning(f"요청 검증 오류: {exc}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "body": exc.body}
    )

# 데이터베이스 초기화
@app.on_event("startup")
async def startup_event():
    """서버 시작 시 실행되는 초기화 함수"""
    try:
        # 1. 데이터베이스 초기화
        logger.info("데이터베이스 초기화 중...")
        init_db()
        logger.info("데이터베이스 초기화 완료")
        
        # 2. LLM 클라이언트 초기화 확인 (에러가 나도 서버는 시작)
        try:
            from app.ai_core.llm_client import llm_client
            logger.info("LLM 클라이언트 초기화 완료")
        except Exception as e:
            logger.warning(f"LLM 클라이언트 초기화 실패 (서버는 계속 실행): {e}")
        
        # 3. 벡터 DB 초기화는 비활성화 (빠른 시작을 위해)
        logger.info("서버 시작 완료")
    except Exception as e:
        logger.error(f"서버 시작 중 오류 발생: {e}", exc_info=True)
        # 데이터베이스 초기화 실패해도 서버는 시작 (일부 기능만 제한)
        logger.warning("일부 기능이 제한될 수 있습니다.")


# 라우터 등록
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(chat.router)
app.include_router(welfare.router)
app.include_router(community.router)


# API 루트 엔드포인트
@app.get("/")
def root():
    """API 서버 정보"""
    return {
        "message": "늘봄 API 서버",
        "status": "running",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
