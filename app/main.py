from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.models.connection import init_db
from app.api.endpoints import auth, chat, welfare, community

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
    init_db()


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
