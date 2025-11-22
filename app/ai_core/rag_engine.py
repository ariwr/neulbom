"""
RAG 엔진
- 벡터 검색 (FAISS)
- 문서 검색 로직
- Upstage Embeddings 통합
"""

from typing import List, Optional
from sqlalchemy.orm import Session
import numpy as np
import os
from pathlib import Path
import json
import pickle
import logging

from app.core.config import settings
from app.models import models
from app.ai_core.llm_client import llm_client
from app.ai_core.prompts import WELFARE_SUMMARY_PROMPT

logger = logging.getLogger(__name__)

# FAISS 임포트
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    print("경고: FAISS가 설치되지 않았습니다. pip install faiss-cpu를 실행하세요.")


class VectorStore:
    """FAISS 기반 벡터 저장소"""
    
    def __init__(self, dimension: Optional[int] = None, index_path: Optional[str] = None):
        """
        dimension: 임베딩 차원 (None이면 설정에서 자동 감지)
        index_path: FAISS 인덱스 파일 경로
        """
        # 차원 자동 감지 (설정에서 가져오기)
        if dimension is None:
            dimension = settings.EMBEDDING_DIMENSION
        self.dimension = dimension
        self.index_path = index_path or os.path.join(settings.VECTOR_DB_PATH, "faiss.index")
        self.id_to_welfare_id_path = os.path.join(settings.VECTOR_DB_PATH, "id_mapping.pkl")
        
        # 디렉토리 생성
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        
        # FAISS 인덱스 초기화
        if FAISS_AVAILABLE:
            if os.path.exists(self.index_path):
                self.index = faiss.read_index(self.index_path)
                # ID 매핑 로드
                if os.path.exists(self.id_to_welfare_id_path):
                    with open(self.id_to_welfare_id_path, 'rb') as f:
                        self.id_to_welfare_id = pickle.load(f)
                else:
                    self.id_to_welfare_id = {}
            else:
                # L2 거리 기반 인덱스 생성
                self.index = faiss.IndexFlatL2(dimension)
                self.id_to_welfare_id = {}
        else:
            self.index = None
            self.id_to_welfare_id = {}
    
    def add_vectors(self, vectors: np.ndarray, welfare_ids: List[int]):
        """벡터와 welfare ID를 추가합니다."""
        if not FAISS_AVAILABLE or self.index is None:
            return
        
        if len(vectors) == 0:
            return
        
        # numpy 배열로 변환
        if not isinstance(vectors, np.ndarray):
            vectors = np.array(vectors).astype('float32')
        
        # 차원 확인
        if vectors.shape[1] != self.dimension:
            raise ValueError(f"벡터 차원이 맞지 않습니다. 예상: {self.dimension}, 실제: {vectors.shape[1]}")
        
        # 현재 인덱스 크기
        start_id = self.index.ntotal
        
        # 인덱스에 추가
        self.index.add(vectors)
        
        # ID 매핑 저장
        for i, welfare_id in enumerate(welfare_ids):
            self.id_to_welfare_id[start_id + i] = welfare_id
    
    def search(self, query_vector: np.ndarray, k: int = 10) -> List[int]:
        """
        유사도 검색
        - query_vector: 쿼리 벡터 (1차원 배열)
        - k: 반환할 결과 수
        - 반환: welfare ID 리스트
        """
        if not FAISS_AVAILABLE or self.index is None or self.index.ntotal == 0:
            return []
        
        # numpy 배열로 변환
        if not isinstance(query_vector, np.ndarray):
            query_vector = np.array([query_vector]).astype('float32')
        else:
            query_vector = query_vector.reshape(1, -1).astype('float32')
        
        # 검색
        distances, indices = self.index.search(query_vector, min(k, self.index.ntotal))
        
        # welfare ID로 변환
        welfare_ids = []
        for idx in indices[0]:
            if idx in self.id_to_welfare_id:
                welfare_ids.append(self.id_to_welfare_id[idx])
        
        return welfare_ids
    
    def save(self):
        """인덱스를 파일에 저장합니다."""
        if not FAISS_AVAILABLE or self.index is None:
            return
        
        faiss.write_index(self.index, self.index_path)
        
        # ID 매핑 저장
        with open(self.id_to_welfare_id_path, 'wb') as f:
            pickle.dump(self.id_to_welfare_id, f)
    
    def get_size(self) -> int:
        """저장된 벡터 수를 반환합니다."""
        if self.index is None:
            return 0
        return self.index.ntotal


# 전역 벡터 저장소 인스턴스
_vector_store: Optional[VectorStore] = None


def get_vector_store() -> VectorStore:
    """벡터 저장소 싱글톤 인스턴스를 반환합니다."""
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore()
    return _vector_store


def get_embedding(text: str, is_query: bool = False, provider: Optional[str] = None) -> List[float]:
    """
    텍스트를 벡터로 임베딩
    - Upstage 또는 Gemini Embeddings API 사용
    - 텍스트 정제 후 임베딩 생성
    
    Args:
        text: 임베딩할 텍스트
        is_query: True이면 쿼리 모델 사용 (검색용), False이면 문서 모델 사용 (저장용)
        provider: "upstage" 또는 "gemini" (None이면 설정값 사용)
    """
    if not text or not text.strip():
        # 기본 차원
        return [0.0] * settings.EMBEDDING_DIMENSION
    
    # llm_client의 get_text_embedding 메서드 사용
    try:
        return llm_client.get_text_embedding(text, is_query=is_query, provider=provider)
    except Exception as e:
        logger.error(f"임베딩 생성 실패: {e}")
        raise ValueError(
            f"임베딩 생성 실패: {e}. "
            ".env 파일에 UPSTAGE_API_KEY를 확인하세요."
        )


def similarity_search(
    query_embedding: List[float],
    limit: int = 10
) -> List[int]:
    """
    벡터 유사도 검색
    - query_embedding: 쿼리 벡터
    - limit: 반환할 결과 수
    - 반환: welfare ID 리스트
    """
    vector_store = get_vector_store()
    return vector_store.search(np.array(query_embedding), k=limit)


def search_welfare_rag(
    db: Session,
    query: str,
    region: Optional[str] = None,
    age: Optional[int] = None,
    limit: int = 10
) -> List[models.Welfare]:
    """
    하이브리드 검색 (Hybrid Search)
    - Semantic Search (벡터 유사도) + Keyword Search 결합
    - Metadata Filtering (지역/나이 필터)
    - LLM 요약 생성
    """
    from app.models.crud import search_welfares
    
    # 빈 쿼리 처리
    if not query or not query.strip():
        logger.warning("빈 쿼리로 검색 시도")
        return []
    
    query = query.strip()
    
    try:
        # 1. 벡터 유사도 검색 (Semantic Search)
        try:
            query_embedding = get_embedding(query, is_query=True)
            vector_welfare_ids = similarity_search(query_embedding, limit=limit * 3)
            logger.debug(f"벡터 검색 결과: {len(vector_welfare_ids)}개")
        except Exception as e:
            logger.error(f"벡터 검색 실패: {e}")
            vector_welfare_ids = []
        
        # 2. 키워드 검색 (Keyword Search)
        try:
            keyword_welfares = search_welfares(
                db=db,
                keyword=query,
                region=None,  # 필터링은 나중에
                age=None,
                skip=0,
                limit=limit * 3
            )
            keyword_welfare_ids = [w.id for w in keyword_welfares]
            logger.debug(f"키워드 검색 결과: {len(keyword_welfare_ids)}개")
        except Exception as e:
            logger.error(f"키워드 검색 실패: {e}")
            keyword_welfare_ids = []
    
        
        # 3. 하이브리드 점수 계산을 위한 통합 ID 리스트
        all_welfare_ids = list(set(vector_welfare_ids + keyword_welfare_ids))
        
        if not all_welfare_ids:
            # 검색 결과가 없으면 빈 리스트 반환
            logger.info(f"검색 결과 없음: '{query}'")
            return []
        
        # 4. DB에서 복지 정보 조회
        try:
            welfares = db.query(models.Welfare).filter(
                models.Welfare.id.in_(all_welfare_ids)
            ).all()
            
            if not welfares:
                logger.warning(f"DB에서 복지 정보를 찾을 수 없음: {len(all_welfare_ids)}개 ID")
                return []
        except Exception as e:
            logger.error(f"DB 조회 실패: {e}")
            return []
        
        # 5. 하이브리드 점수 계산 및 정렬
        welfare_dict = {w.id: w for w in welfares}
        scored_welfares = []
        
        for welfare_id in all_welfare_ids:
            if welfare_id not in welfare_dict:
                continue
            
            welfare = welfare_dict[welfare_id]
            
            # 벡터 검색 점수 (순위 기반, 높을수록 좋음)
            vector_score = 0.0
            if welfare_id in vector_welfare_ids:
                vector_rank = vector_welfare_ids.index(welfare_id)
                vector_score = 1.0 / (vector_rank + 1)  # 순위가 높을수록 점수 높음
            
            # 키워드 검색 점수 (순위 기반)
            keyword_score = 0.0
            if welfare_id in keyword_welfare_ids:
                keyword_rank = keyword_welfare_ids.index(welfare_id)
                keyword_score = 1.0 / (keyword_rank + 1)
            
            # 키워드 매칭 보너스 (제목/요약에 직접 포함된 경우)
            keyword_bonus = 0.0
            query_lower = query.lower()
            if welfare.title and query_lower in welfare.title.lower():
                keyword_bonus += 0.5
            if welfare.summary and query_lower in welfare.summary.lower():
                keyword_bonus += 0.3
            
            # 하이브리드 점수 (벡터 60% + 키워드 40% + 보너스)
            hybrid_score = (vector_score * 0.6) + (keyword_score * 0.4) + keyword_bonus
            
            scored_welfares.append((hybrid_score, welfare))
        
        # 점수 순으로 정렬
        scored_welfares.sort(key=lambda x: x[0], reverse=True)
        welfares = [w for _, w in scored_welfares]
        
        # 6. 지역/나이 필터링 (Metadata Filtering)
        if region:
            before_filter = len(welfares)
            welfares = [w for w in welfares if region in (w.region or "")]
            logger.debug(f"지역 필터링: {before_filter}개 -> {len(welfares)}개")
        
        if age:
            before_filter = len(welfares)
            welfares = [
                w for w in welfares
                if (w.age_min is None or w.age_min <= age) and
                   (w.age_max is None or w.age_max >= age)
            ]
            logger.debug(f"나이 필터링: {before_filter}개 -> {len(welfares)}개")
        
        # 7. 상위 limit개만 반환
        welfares = welfares[:limit]
        
        # 8. LLM을 사용하여 17세 수준으로 3줄 요약 생성
        for welfare in welfares:
            if not welfare.summary and welfare.full_text:
                try:
                    welfare.summary = summarize_welfare(welfare.full_text)
                except Exception as e:
                    logger.error(f"요약 생성 오류 (ID: {welfare.id}): {e}")
                    # 요약 실패 시 기본 요약 사용
                    welfare.summary = welfare.full_text[:200] + "..." if len(welfare.full_text) > 200 else welfare.full_text
        
        logger.info(f"하이브리드 검색 완료: '{query}' -> {len(welfares)}개 결과")
        return welfares
    
    except Exception as e:
        logger.error(f"하이브리드 검색 중 오류 발생: {e}", exc_info=True)
        # 오류 발생 시 키워드 검색으로 대체
        try:
            logger.info(f"키워드 검색으로 대체 시도: '{query}'")
            return search_welfares(
                db=db,
                keyword=query,
                region=region,
                age=age,
                skip=0,
                limit=limit
            )
        except Exception as fallback_error:
            logger.error(f"키워드 검색 대체도 실패: {fallback_error}")
            return []


def summarize_welfare(text: str, target_level: str = "17세") -> str:
    """
    복지 정보를 17세 수준으로 요약
    - LLM API 통합
    """
    prompt = WELFARE_SUMMARY_PROMPT.format(
        target_level=target_level,
        text=text
    )
    
    # LLM API 호출
    summary = llm_client.summarize_text(text, target_level)
    
    return summary


def store_welfare_embedding(db: Session, welfare: models.Welfare):
    """
    복지 정보의 임베딩을 생성하여 저장
    - DB에 임베딩 저장
    - 벡터 DB에도 저장
    """
    if not welfare.full_text:
        return
    
    # 임베딩 생성
    embedding = get_embedding(welfare.full_text)
    
    # DB에 저장
    welfare.embedding = embedding
    db.commit()
    
    # 벡터 DB에 추가
    vector_store = get_vector_store()
    vector_store.add_vectors(
        np.array([embedding]).astype('float32'),
        [welfare.id]
    )
    vector_store.save()


def batch_store_embeddings(db: Session, batch_size: int = 100):
    """
    모든 복지 정보의 임베딩을 일괄 생성하여 저장
    - DB에서 임베딩이 없는 복지 정보를 가져와서 처리
    """
    # 임베딩이 없는 복지 정보 조회
    welfares = db.query(models.Welfare).filter(
        models.Welfare.embedding.is_(None),
        models.Welfare.full_text.isnot(None)
    ).limit(batch_size).all()
    
    if not welfares:
        return 0
    
    vectors = []
    welfare_ids = []
    
    for welfare in welfares:
        if welfare.full_text:
            embedding = get_embedding(welfare.full_text)
            welfare.embedding = embedding
            vectors.append(embedding)
            welfare_ids.append(welfare.id)
    
    # DB 커밋
    db.commit()
    
    # 벡터 DB에 일괄 추가
    if vectors:
        vector_store = get_vector_store()
        vector_store.add_vectors(
            np.array(vectors).astype('float32'),
            welfare_ids
        )
        vector_store.save()
    
    return len(welfare_ids)


def load_welfares_to_vector_db(db: Session, force_rebuild: bool = False):
    """
    DB에 있는 복지 정보를 벡터 DB(FAISS)에 로드
    - 서버 시작 시 호출
    - 이미 인덱스가 있고 force_rebuild=False이면 기존 인덱스 사용
    
    Args:
        db: 데이터베이스 세션
        force_rebuild: True이면 기존 인덱스를 삭제하고 재구축
    """
    vector_store = get_vector_store()
    
    # 기존 인덱스가 있고 재구축이 필요 없으면 스킵
    if not force_rebuild and vector_store.get_size() > 0:
        logger.info(f"✓ 기존 벡터 인덱스 사용: {vector_store.get_size()}개 벡터")
        return
    
    # 재구축이 필요한 경우 기존 인덱스 삭제
    if force_rebuild:
        logger.info("기존 벡터 인덱스 삭제 중...")
        global _vector_store
        vector_store_path = os.path.join(settings.VECTOR_DB_PATH, "faiss.index")
        id_mapping_path = os.path.join(settings.VECTOR_DB_PATH, "id_mapping.pkl")
        if os.path.exists(vector_store_path):
            os.remove(vector_store_path)
        if os.path.exists(id_mapping_path):
            os.remove(id_mapping_path)
        _vector_store = None
        vector_store = get_vector_store()
    
    # DB에서 복지 정보 조회
    welfares = db.query(models.Welfare).filter(
        models.Welfare.full_text.isnot(None)
    ).all()
    
    if not welfares:
        logger.warning("벡터 DB에 로드할 복지 정보가 없습니다.")
        return
    
    logger.info(f"🔄 벡터 DB 초기화 중... (총 {len(welfares)}개 항목)")
    
    vectors = []
    welfare_ids = []
    new_embeddings_count = 0
    
    for i, welfare in enumerate(welfares):
        if welfare.full_text:
            # 이미 임베딩이 있으면 사용, 없으면 생성 (비용 절감)
            if not welfare.embedding:
                try:
                    embedding = get_embedding(welfare.full_text)
                    welfare.embedding = embedding
                    new_embeddings_count += 1
                except Exception as e:
                    logger.error(f"임베딩 생성 실패 (ID: {welfare.id}): {e}")
                    continue
            else:
                embedding = welfare.embedding
            
            vectors.append(embedding)
            welfare_ids.append(welfare.id)
            
            # 배치로 벡터 DB에 추가 (100개씩)
            if len(vectors) >= 100:
                vector_store.add_vectors(
                    np.array(vectors).astype('float32'),
                    welfare_ids
                )
                vectors = []
                welfare_ids = []
                logger.info(f"  진행 중: {i + 1}/{len(welfares)} (새 임베딩: {new_embeddings_count}개)")
    
    # 남은 벡터 추가
    if vectors:
        vector_store.add_vectors(
            np.array(vectors).astype('float32'),
            welfare_ids
        )
    
    # 인덱스 저장
    vector_store.save()
    
    # DB 커밋 (새로 생성한 임베딩 저장)
    if new_embeddings_count > 0:
        try:
            db.commit()
            logger.info(f"✓ {new_embeddings_count}개의 새 임베딩을 DB에 저장했습니다.")
        except Exception as e:
            logger.error(f"DB 커밋 실패: {e}")
            db.rollback()
    
    logger.info(f"✅ 벡터 DB 초기화 완료: {vector_store.get_size()}개 벡터 저장됨")


def rebuild_vector_index(db: Session):
    """
    벡터 인덱스를 재구축합니다.
    - 모든 복지 정보의 임베딩을 다시 생성하여 벡터 DB에 저장
    """
    load_welfares_to_vector_db(db, force_rebuild=True)
