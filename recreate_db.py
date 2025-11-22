"""
데이터베이스 재생성 스크립트
기존 DB를 삭제하고 새로운 스키마로 재생성합니다.
"""
import os
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.models.connection import init_db, engine
from app.core.config import settings

def recreate_database():
    """데이터베이스 재생성"""
    db_path = settings.DATABASE_URL.replace('sqlite:///', '')
    
    print("=" * 60)
    print("데이터베이스 재생성")
    print("=" * 60)
    
    # 기존 DB 파일이 있으면 백업
    if os.path.exists(db_path):
        backup_path = f"{db_path}.backup"
        print(f"\n기존 DB 파일 발견: {db_path}")
        print(f"백업 생성 중: {backup_path}")
        try:
            import shutil
            shutil.copy2(db_path, backup_path)
            print("✓ 백업 완료")
        except Exception as e:
            print(f"⚠ 백업 실패: {e}")
            response = input("\n백업 없이 계속하시겠습니까? (y/n): ")
            if response.lower() != 'y':
                print("취소되었습니다.")
                return
        
        # 기존 DB 파일 삭제
        print(f"\n기존 DB 파일 삭제 중: {db_path}")
        try:
            os.remove(db_path)
            print("✓ 삭제 완료")
        except Exception as e:
            print(f"✗ 삭제 실패: {e}")
            return
    
    # 새 DB 생성
    print(f"\n새 데이터베이스 생성 중...")
    try:
        init_db()
        print("✓ 데이터베이스 생성 완료!")
        print(f"\n새 DB 파일: {db_path}")
        print("\n이제 category 컬럼이 포함된 새로운 스키마로 생성되었습니다.")
    except Exception as e:
        print(f"✗ 데이터베이스 생성 실패: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n" + "=" * 60)
    print("데이터베이스 재생성 완료!")
    print("=" * 60)
    print("\n다음 단계:")
    print("1. 크롤링 실행: python -m app.crawlers.run_crawler --max-pages 100")
    print("2. 데이터 확인: python check_db.py")

if __name__ == "__main__":
    recreate_database()

