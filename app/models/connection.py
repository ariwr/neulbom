from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False}  # SQLite only
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """데이터베이스 세션 의존성"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """데이터베이스 초기화 (테이블 생성)"""
    Base.metadata.create_all(bind=engine)
    # 마이그레이션: name 컬럼 추가 (기존 테이블에 없을 경우)
    migrate_add_name_column()
    # 마이그레이션: view_count 컬럼 추가 (기존 테이블에 없을 경우)
    migrate_add_view_count_column()


def migrate_add_name_column():
    """users 테이블에 name 컬럼이 없으면 추가하는 마이그레이션"""
    from sqlalchemy import inspect, text
    
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    if "users" in tables:
        columns = [col["name"] for col in inspector.get_columns("users")]
        if "name" not in columns:
            # name 컬럼 추가
            with engine.connect() as conn:
                try:
                    conn.execute(text("ALTER TABLE users ADD COLUMN name VARCHAR"))
                    conn.commit()
                    print("✓ users 테이블에 name 컬럼이 추가되었습니다.")
                except Exception as e:
                    print(f"⚠ name 컬럼 추가 중 오류 발생 (이미 존재할 수 있음): {e}")
                    conn.rollback()


def migrate_add_view_count_column():
    """welfares 테이블에 view_count 컬럼이 없으면 추가하는 마이그레이션"""
    from sqlalchemy import inspect, text
    import logging
    
    logger = logging.getLogger(__name__)
    
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    if "welfares" in tables:
        columns = [col["name"] for col in inspector.get_columns("welfares")]
        if "view_count" not in columns:
            # view_count 컬럼 추가
            with engine.connect() as conn:
                try:
                    conn.execute(text("ALTER TABLE welfares ADD COLUMN view_count INTEGER DEFAULT 0 NOT NULL"))
                    conn.commit()
                    logger.info("welfares 테이블에 view_count 컬럼이 추가되었습니다.")
                except Exception as e:
                    logger.warning(f"view_count 컬럼 추가 중 오류 발생 (이미 존재할 수 있음): {e}")
                    conn.rollback()

