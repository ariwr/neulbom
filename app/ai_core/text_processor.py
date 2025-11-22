"""
텍스트 처리
- PDF 텍스트 추출
- 텍스트 청킹 (Chunking)
- 전처리
"""

from typing import List
import re


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    PDF에서 텍스트 추출
    - TODO: PyPDF2 또는 pdfplumber 사용
    """
    # TODO: 실제 PDF 추출 구현
    # import PyPDF2
    # with open(pdf_path, 'rb') as file:
    #     reader = PyPDF2.PdfReader(file)
    #     text = ""
    #     for page in reader.pages:
    #         text += page.extract_text()
    #     return text
    
    return ""


def extract_text_from_hwp(hwp_path: str) -> str:
    """
    HWP에서 텍스트 추출
    - TODO: olefile 또는 pyhwp 사용
    """
    # TODO: 실제 HWP 추출 구현
    return ""


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """
    텍스트를 청크로 분할
    - chunk_size: 각 청크의 최대 길이
    - overlap: 청크 간 겹치는 부분
    """
    # 문장 단위로 분할
    sentences = re.split(r'[.!?]\s+', text)
    
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        # 현재 청크에 문장 추가 시 길이 초과 여부 확인
        if len(current_chunk) + len(sentence) > chunk_size:
            if current_chunk:
                chunks.append(current_chunk.strip())
            
            # overlap을 고려하여 이전 청크의 끝부분 포함
            if overlap > 0 and chunks:
                prev_chunk = chunks[-1]
                overlap_text = prev_chunk[-overlap:] if len(prev_chunk) > overlap else prev_chunk
                current_chunk = overlap_text + " " + sentence
            else:
                current_chunk = sentence
        else:
            current_chunk += " " + sentence if current_chunk else sentence
    
    # 마지막 청크 추가
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks


def clean_text(text: str) -> str:
    """
    텍스트 전처리
    - 불필요한 공백 제거
    - 특수 문자 정리
    """
    # 연속된 공백 제거
    text = re.sub(r'\s+', ' ', text)
    
    # 앞뒤 공백 제거
    text = text.strip()
    
    return text


def preprocess_welfare_text(text: str) -> str:
    """
    복지 정보 텍스트 전처리
    - 특화된 전처리 로직
    """
    # 기본 정리
    text = clean_text(text)
    
    # 불필요한 헤더/푸터 제거 (필요시)
    # text = re.sub(r'^.*?본문.*?\n', '', text, flags=re.DOTALL)
    
    return text

