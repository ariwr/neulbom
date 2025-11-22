"""
LangChain + FAISS 기반 복지 서비스 추천 엔진
전처리된 데이터를 사용하여 벡터 유사도 기반 검색을 제공합니다.
"""

import sys
import os
from pathlib import Path
from typing import List, Dict, Optional
import json
import pickle

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import numpy as np
from app.core.config import settings

# LangChain 임포트
try:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    print("경고: LangChain이 설치되지 않았습니다. pip install langchain을 실행하세요.")

# FAISS 임포트
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    print("경고: FAISS가 설치되지 않았습니다. pip install faiss-cpu를 실행하세요.")

# Upstage 임베딩 (llm_client 사용)
try:
    from app.ai_core.llm_client import llm_client
    UPSTAGE_AVAILABLE = True
except ImportError:
    UPSTAGE_AVAILABLE = False
    print("경고: llm_client를 임포트할 수 없습니다.")


class WelfareRecommendationEngine:
    """복지 서비스 추천 엔진"""
    
    def __init__(
        self,
        data_path: Optional[str] = None,
        index_path: Optional[str] = None
    ):
        """
        Args:
            data_path: 전처리된 JSON 파일 경로 (rag_welfare_data.json)
            index_path: FAISS 인덱스 저장 경로 (None이면 자동 생성)
        """
        self.index = None
        self.data = []
        self.id_to_data = {}  # 인덱스 ID -> 데이터 매핑
        
        # 데이터 경로 설정
        if data_path is None:
            data_path = project_root / "data" / "preprocessed" / "rag_welfare_data.json"
        self.data_path = Path(data_path)
        
        # 인덱스 경로 설정
        if index_path is None:
            index_path = project_root / "data" / "vector_db" / "welfare_faiss.index"
        self.index_path = Path(index_path)
        self.id_mapping_path = self.index_path.parent / "welfare_id_mapping.pkl"
        
        # 디렉토리 생성
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 데이터 로드 및 인덱스 구축
        self._load_data()
        self._build_index()
    
    def _get_embedding(self, text: str) -> List[float]:
        """텍스트를 벡터로 임베딩 (Upstage 사용)"""
        if not text or not text.strip():
            return [0.0] * settings.EMBEDDING_DIMENSION
        
        if not UPSTAGE_AVAILABLE:
            raise ValueError("Upstage API 키가 설정되지 않았습니다. .env 파일에 UPSTAGE_API_KEY를 설정하세요.")
        
        # llm_client의 get_text_embedding 메서드 사용
        return llm_client.get_text_embedding(text)
    
    def _load_data(self):
        """전처리된 JSON 데이터 로드"""
        if not self.data_path.exists():
            raise FileNotFoundError(
                f"데이터 파일을 찾을 수 없습니다: {self.data_path}\n"
                "먼저 preprocess.py를 실행하여 데이터를 전처리하세요."
            )
        
        with open(self.data_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        
        print(f"✓ 데이터 로드 완료: {len(self.data)}개 항목")
    
    def _build_index(self):
        """FAISS 인덱스 구축"""
        if not FAISS_AVAILABLE:
            raise ImportError("FAISS가 설치되지 않았습니다. pip install faiss-cpu를 실행하세요.")
        
        # 기존 인덱스가 있으면 로드
        if self.index_path.exists() and self.id_mapping_path.exists():
            print(f"기존 인덱스 로드 중: {self.index_path}")
            self.index = faiss.read_index(str(self.index_path))
            with open(self.id_mapping_path, 'rb') as f:
                self.id_to_data = pickle.load(f)
            print(f"✓ 인덱스 로드 완료: {self.index.ntotal}개 벡터")
            return
        
        # 새 인덱스 구축
        print("FAISS 인덱스 구축 중...")
        print("이 작업은 시간이 걸릴 수 있습니다...")
        
        # 임베딩 차원 (Upstage solar-embedding-1-large는 4096)
        dimension = settings.EMBEDDING_DIMENSION
        
        # L2 거리 기반 인덱스 생성
        self.index = faiss.IndexFlatL2(dimension)
        
        # 각 데이터의 search_content를 임베딩
        vectors = []
        for i, item in enumerate(self.data):
            search_content = item.get('search_content', '')
            if not search_content:
                # search_content가 없으면 title과 다른 필드 병합
                search_content = ' '.join([
                    item.get('title', ''),
                    item.get('target', ''),
                    item.get('organization', '')
                ])
            
            embedding = self._get_embedding(search_content)
            vectors.append(embedding)
            self.id_to_data[i] = item
            
            # 진행 상황 출력
            if (i + 1) % 10 == 0:
                print(f"  진행 중: {i + 1}/{len(self.data)}")
        
        # 벡터를 numpy 배열로 변환
        vectors_array = np.array(vectors).astype('float32')
        
        # 인덱스에 추가
        self.index.add(vectors_array)
        
        # 인덱스 저장
        faiss.write_index(self.index, str(self.index_path))
        with open(self.id_mapping_path, 'wb') as f:
            pickle.dump(self.id_to_data, f)
        
        print(f"✓ 인덱스 구축 완료: {self.index.ntotal}개 벡터")
        print(f"  저장 위치: {self.index_path}")
    
    def search(
        self,
        query: str,
        top_k: int = 3,
        min_score: Optional[float] = None
    ) -> List[Dict]:
        """
        사용자 질문에 대한 복지 서비스 검색
        
        Args:
            query: 사용자 질문 (예: "할머니 병원비 때문에 학교 다니기 힘들어")
            top_k: 반환할 상위 결과 수
            min_score: 최소 유사도 점수 (L2 거리, 낮을수록 유사)
        
        Returns:
            검색 결과 리스트 (서비스명, 요약 내용, 신청 URL 포함)
        """
        if self.index is None or self.index.ntotal == 0:
            return []
        
        # 쿼리 임베딩
        query_embedding = self._get_embedding(query)
        query_vector = np.array([query_embedding]).astype('float32')
        
        # FAISS 검색
        k = min(top_k, self.index.ntotal)
        distances, indices = self.index.search(query_vector, k)
        
        # 결과 구성
        results = []
        for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
            if idx in self.id_to_data:
                item = self.id_to_data[idx]
                
                # 최소 점수 필터링
                if min_score is not None and distance > min_score:
                    continue
                
                result = {
                    'rank': i + 1,
                    'service_name': item.get('title', '제목 없음'),
                    'summary': item.get('search_content', '')[:200] + '...' if len(item.get('search_content', '')) > 200 else item.get('search_content', ''),
                    'url': item.get('url', ''),
                    'target': item.get('target', ''),
                    'organization': item.get('organization', ''),
                    'contact': item.get('contact', ''),
                    'similarity_score': float(distance),  # L2 거리 (낮을수록 유사)
                }
                results.append(result)
        
        return results
    
    def format_results(self, results: List[Dict]) -> str:
        """검색 결과를 읽기 쉬운 형식으로 포맷팅"""
        if not results:
            return "검색 결과가 없습니다."
        
        formatted = []
        for result in results:
            formatted.append(f"""
{'='*80}
[순위 {result['rank']}] {result['service_name']}
{'='*80}
요약: {result['summary']}
대상: {result.get('target', '정보 없음')}
기관: {result.get('organization', '정보 없음')}
연락처: {result.get('contact', '정보 없음')}
신청 URL: {result['url'] if result['url'] else '정보 없음'}
유사도 점수: {result['similarity_score']:.4f} (낮을수록 유사)
""")
        
        return '\n'.join(formatted)


def main():
    """테스트 실행"""
    print("=" * 80)
    print("복지 서비스 추천 엔진 테스트")
    print("=" * 80)
    
    # 엔진 초기화
    try:
        engine = WelfareRecommendationEngine()
    except Exception as e:
        print(f"오류: {e}")
        return
    
    # 테스트 질문들
    test_queries = [
        "할머니 병원비 때문에 학교 다니기 힘들어",
        "가족 돌봄 때문에 취업 준비가 어려워",
        "학생인데 생활비가 부족해",
        "장학금을 받고 싶어",
        "의료비 지원이 필요해",
        "주거비 지원이 필요해",
    ]
    
    print("\n" + "=" * 80)
    print("테스트 질문으로 검색 실행")
    print("=" * 80)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n\n[테스트 {i}] 질문: {query}")
        print("-" * 80)
        
        try:
            results = engine.search(query, top_k=3)
            
            if results:
                print(f"\n검색 결과 ({len(results)}개):")
                print(engine.format_results(results))
            else:
                print("검색 결과가 없습니다.")
        
        except Exception as e:
            print(f"검색 중 오류 발생: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 80)
    print("테스트 완료!")
    print("=" * 80)


if __name__ == "__main__":
    main()

