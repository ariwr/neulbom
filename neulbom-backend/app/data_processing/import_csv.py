"""
CSV 파일을 DB에 임포트하고 벡터 임베딩을 생성하는 메인 스크립트
"""

import sys
import os
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.models.connection import get_db, init_db
from app.data_processing.csv_processor import process_csv_to_db
from app.ai_core.rag_engine import rebuild_vector_index, batch_store_embeddings
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """CSV 파일을 임포트하고 벡터 인덱스를 구축합니다."""
    import argparse
    
    parser = argparse.ArgumentParser(description='CSV 파일을 DB에 임포트하고 벡터 인덱스 구축')
    parser.add_argument('csv_path', type=str, help='CSV 파일 경로')
    parser.add_argument('--batch-size', type=int, default=100, help='배치 크기')
    parser.add_argument('--skip-import', action='store_true', help='CSV 임포트 건너뛰기 (벡터 인덱스만 재구축)')
    parser.add_argument('--skip-embedding', action='store_true', help='벡터 임베딩 생성 건너뛰기')
    
    args = parser.parse_args()
    
    # CSV 파일 경로 확인
    csv_path = Path(args.csv_path)
    if not csv_path.exists():
        logger.error(f"CSV 파일을 찾을 수 없습니다: {csv_path}")
        return
    
    # DB 초기화
    logger.info("데이터베이스 초기화 중...")
    init_db()
    db = next(get_db())
    
    try:
        # 1. CSV 파일 임포트
        if not args.skip_import:
            logger.info("=" * 60)
            logger.info("1단계: CSV 파일 임포트")
            logger.info("=" * 60)
            result = process_csv_to_db(str(csv_path), db, batch_size=args.batch_size)
            logger.info(f"\n임포트 완료!")
            logger.info(f"총: {result['total']}개")
            logger.info(f"저장: {result['saved']}개")
            logger.info(f"업데이트: {result['updated']}개")
            logger.info(f"에러: {result['errors']}개")
        else:
            logger.info("CSV 임포트를 건너뜁니다.")
        
        # 2. 벡터 임베딩 생성 및 인덱스 구축
        if not args.skip_embedding:
            logger.info("\n" + "=" * 60)
            logger.info("2단계: 벡터 임베딩 생성 및 인덱스 구축")
            logger.info("=" * 60)
            logger.info("이 작업은 시간이 걸릴 수 있습니다...")
            rebuild_vector_index(db)
            logger.info("\n벡터 인덱스 구축 완료!")
        else:
            logger.info("벡터 임베딩 생성을 건너뜁니다.")
        
        logger.info("\n" + "=" * 60)
        logger.info("모든 작업 완료!")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()

