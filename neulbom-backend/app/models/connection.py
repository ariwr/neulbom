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
    # 마이그레이션: posts 테이블의 모든 필수 컬럼 확인 및 추가
    migrate_posts_table_columns()


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


def migrate_posts_table_columns():
    """posts 테이블의 모든 필수 컬럼을 확인하고 누락된 컬럼을 추가하는 통합 마이그레이션"""
    from sqlalchemy import inspect, text
    import logging
    
    logger = logging.getLogger(__name__)
    
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    if "posts" not in tables:
        logger.info("posts 테이블이 존재하지 않습니다. Base.metadata.create_all()에서 생성됩니다.")
        return
    
    columns = [col["name"] for col in inspector.get_columns("posts")]
    logger.info(f"현재 posts 테이블의 컬럼: {columns}")
    
    # Post 모델에 필요한 모든 컬럼 정의
    # SQLite는 BOOLEAN을 직접 지원하지 않으므로 INTEGER로 저장 (0=False, 1=True)
    required_columns = {
        "view_count": ("INTEGER", "DEFAULT 0", 0),
        "like_count": ("INTEGER", "DEFAULT 0", 0),
        "category": ("VARCHAR", "", "free"),
        "is_crisis": ("INTEGER", "DEFAULT 0", 0),  # SQLite에서는 INTEGER로 저장
        "crisis_checked": ("INTEGER", "DEFAULT 0", 0),  # SQLite에서는 INTEGER로 저장
        "anonymous_id": ("VARCHAR", "", None),
    }
    
    with engine.connect() as conn:
        try:
            added_columns = []
            for col_name, (col_type, default_clause, default_value) in required_columns.items():
                if col_name not in columns:
                    try:
                        # 컬럼 추가
                        if default_clause:
                            sql = f"ALTER TABLE posts ADD COLUMN {col_name} {col_type} {default_clause}"
                        else:
                            sql = f"ALTER TABLE posts ADD COLUMN {col_name} {col_type}"
                        
                        conn.execute(text(sql))
                        
                        # 기본값이 필요한 경우 기존 행 업데이트
                        if default_value is not None:
                            if isinstance(default_value, str):
                                conn.execute(text(f"UPDATE posts SET {col_name} = '{default_value}' WHERE {col_name} IS NULL"))
                            elif isinstance(default_value, bool):
                                conn.execute(text(f"UPDATE posts SET {col_name} = {1 if default_value else 0} WHERE {col_name} IS NULL"))
                            else:
                                conn.execute(text(f"UPDATE posts SET {col_name} = {default_value} WHERE {col_name} IS NULL"))
                        
                        added_columns.append(col_name)
                        logger.info(f"✓ posts 테이블에 {col_name} 컬럼이 추가되었습니다.")
                    except Exception as e:
                        logger.warning(f"⚠ {col_name} 컬럼 추가 중 오류 발생 (이미 존재할 수 있음): {e}")
            
            # 기존 컬럼의 NULL 값 업데이트
            for col_name, (col_type, default_clause, default_value) in required_columns.items():
                if col_name in columns and default_value is not None:
                    try:
                        if isinstance(default_value, str):
                            result = conn.execute(text(f"UPDATE posts SET {col_name} = '{default_value}' WHERE {col_name} IS NULL OR {col_name} = ''"))
                        elif isinstance(default_value, bool):
                            result = conn.execute(text(f"UPDATE posts SET {col_name} = {1 if default_value else 0} WHERE {col_name} IS NULL"))
                        else:
                            result = conn.execute(text(f"UPDATE posts SET {col_name} = {default_value} WHERE {col_name} IS NULL"))
                        
                        if result.rowcount > 0:
                            logger.info(f"✓ posts 테이블의 {result.rowcount}개 행에 {col_name} 기본값이 설정되었습니다.")
                    except Exception as e:
                        logger.warning(f"⚠ {col_name} 기본값 설정 중 오류 발생: {e}")
            
            conn.commit()
            
            if added_columns:
                logger.info(f"posts 테이블 마이그레이션 완료: {', '.join(added_columns)} 컬럼 추가됨")
            else:
                logger.info("posts 테이블의 모든 필수 컬럼이 이미 존재합니다.")
                
        except Exception as e:
            logger.error(f"posts 테이블 마이그레이션 중 오류 발생: {e}")
            conn.rollback()
            raise

