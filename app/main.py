from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.models.connection import init_db, SessionLocal
from app.api.endpoints import auth, chat, welfare, community
from app.ai_core.rag_engine import load_welfares_to_vector_db
import logging

logger = logging.getLogger(__name__)

# FastAPI 앱 생성
app = FastAPI(
    title="늘봄 API",
    description="AI 정서 지원 및 복지 정보 매칭 플랫폼",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인으로 제한
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
    logger.info("✓ 데이터베이스 초기화 완료")
    
    # 2. 벡터 DB 초기화 (DB 데이터를 FAISS 인덱스에 로드)
    try:
        db = SessionLocal()
        try:
            load_welfares_to_vector_db(db, force_rebuild=False)
        except Exception as e:
            logger.error(f"벡터 DB 초기화 실패: {e}")
            logger.warning("벡터 검색 기능이 제한될 수 있습니다.")
        finally:
            db.close()
    except Exception as e:
        logger.error(f"벡터 DB 초기화 중 오류: {e}")


# 라우터 등록
app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(welfare.router)
app.include_router(community.router)


# 헬스 체크
@app.get("/")
def root():
    return {"message": "늘봄 API 서버", "status": "running"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
