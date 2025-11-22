"""
RAG 엔진
- 벡터 검색 (FAISS/Chroma)
- 문서 검색 로직
"""

from typing import List, Optional
from sqlalchemy.orm import Session
import numpy as np
from app.core.config import settings
from app.models import models
from app.ai_core.llm_client import llm_client
from app.ai_core.prompts import WELFARE_SUMMARY_PROMPT

# TODO: 실제 벡터 DB 통합 필요
# 예: Chroma, Pinecone, 또는 FAISS 사용


def get_embedding(text: str) -> List[float]:
    """
    텍스트를 벡터로 임베딩
    - TODO: 실제 임베딩 모델 통합
    """
    # 실제 구현 시:
    # import openai
    # response = openai.Embedding.create(
    #     model=settings.EMBEDDING_MODEL,
    #     input=text
    # )
    # return response['data'][0]['embedding']
    
    # 임시 더미 임베딩
    return [0.0] * 1536  # OpenAI text-embedding-3-small 차원


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
    # TODO: 실제 벡터 DB 검색
    # 예: FAISS 인덱스 검색
    # index = faiss.read_index(settings.VECTOR_DB_PATH)
    # distances, indices = index.search(np.array([query_embedding]), limit)
    # return indices[0].tolist()
    
    return []


def search_welfare_rag(
    db: Session,
    query: str,
    region: Optional[str] = None,
    age: Optional[int] = None,
    limit: int = 10
) -> List[models.Welfare]:
    """
    RAG 기반 복지 정보 검색
    - 벡터 유사도 검색
    - 사용자 프로필 기반 필터링
    - LLM 요약 생성
    """
    # 쿼리 텍스트를 벡터로 임베딩
    query_embedding = get_embedding(query)
    
    # 벡터 DB에서 유사도 검색
    welfare_ids = similarity_search(query_embedding, limit=limit * 2)  # 필터링을 위해 더 많이 가져옴
    
    # DB에서 복지 정보 조회
    if welfare_ids:
        welfares = db.query(models.Welfare).filter(
            models.Welfare.id.in_(welfare_ids)
        ).all()
    else:
        # 벡터 검색 실패 시 키워드 검색으로 대체
        from app.models.crud import search_welfares
        welfares = search_welfares(
            db=db,
            keyword=query,
            region=region,
            age=age,
            limit=limit
        )
    
    # 지역/나이 필터링
    if region:
        welfares = [w for w in welfares if region in (w.region or "")]
    if age:
        welfares = [
            w for w in welfares
            if (w.age_min is None or w.age_min <= age) and
               (w.age_max is None or w.age_max >= age)
        ]
    
    # 상위 limit개만 반환
    welfares = welfares[:limit]
    
    # LLM을 사용하여 17세 수준으로 요약 생성
    for welfare in welfares:
        if not welfare.summary and welfare.full_text:
            welfare.summary = summarize_welfare(welfare.full_text)
    
    return welfares


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
    - TODO: 실제 벡터 DB 저장 로직
    """
    if welfare.embedding is None and welfare.full_text:
        embedding = get_embedding(welfare.full_text)
        welfare.embedding = embedding
        db.commit()
        
        # TODO: 벡터 DB에도 저장
        # index.add(np.array([embedding]))

