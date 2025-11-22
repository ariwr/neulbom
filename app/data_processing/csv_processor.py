"""
CSV 파일 전처리 및 DB 저장 스크립트
한국사회보장정보원 복지서비스 정보 CSV를 전처리하여 DB에 저장합니다.
"""

import sys
import os
from pathlib import Path
import pandas as pd
from typing import List, Dict, Optional
from datetime import datetime
import re

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.models.connection import get_db, init_db
from app.models import models
from sqlalchemy.orm import Session
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def detect_encoding(file_path: str) -> str:
    """CSV 파일의 인코딩을 감지합니다."""
    import chardet
    
    with open(file_path, 'rb') as f:
        raw_data = f.read(10000)
        result = chardet.detect(raw_data)
        encoding = result['encoding']
        logger.info(f"감지된 인코딩: {encoding} (신뢰도: {result['confidence']:.2f})")
        return encoding


def clean_text(text: str) -> str:
    """텍스트를 정제합니다."""
    if pd.isna(text) or text is None:
        return ""
    
    text = str(text).strip()
    # HTML 태그 제거
    text = re.sub(r'<[^>]+>', '', text)
    # 연속된 공백 제거
    text = re.sub(r'\s+', ' ', text)
    return text


def extract_region(text: str) -> Optional[str]:
    """텍스트에서 지역 정보를 추출합니다."""
    if not text:
        return None
    
    # 주요 지역 키워드
    regions = [
        '서울', '부산', '대구', '인천', '광주', '대전', '울산', '세종',
        '경기', '강원', '충북', '충남', '전북', '전남', '경북', '경남', '제주',
        '전국', '수도권', '지역'
    ]
    
    for region in regions:
        if region in text:
            return region
    
    return None


def extract_age_range(text: str) -> tuple:
    """텍스트에서 나이 범위를 추출합니다."""
    if not text:
        return None, None
    
    # 나이 패턴 찾기 (예: "18세 이상", "65세 이상", "만 18세~65세")
    patterns = [
        r'(\d+)세\s*이상',
        r'만\s*(\d+)세\s*이상',
        r'(\d+)세\s*~\s*(\d+)세',
        r'(\d+)세\s*-\s*(\d+)세',
        r'(\d+)세\s*이상\s*(\d+)세\s*이하',
    ]
    
    age_min = None
    age_max = None
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            groups = match.groups()
            if len(groups) == 1:
                age_min = int(groups[0])
            elif len(groups) == 2:
                age_min = int(groups[0])
                age_max = int(groups[1])
            break
    
    return age_min, age_max


def parse_contact_info(contact_text: str) -> Dict[str, str]:
    """연락처 정보를 파싱합니다."""
    if not contact_text or pd.isna(contact_text):
        return {}
    
    contact_text = str(contact_text)
    # 전화번호 패턴
    phone_pattern = r'(\d{2,4}-\d{3,4}-\d{4}|\d{3,4}-\d{4}|\d{10,11})'
    phones = re.findall(phone_pattern, contact_text)
    
    return {
        'phone': phones[0] if phones else None,
        'all_phones': ', '.join(phones) if phones else None
    }


def parse_date(date_str: str) -> Optional[datetime]:
    """날짜 문자열을 파싱합니다."""
    if not date_str or pd.isna(date_str):
        return None
    
    try:
        # YYYY-MM-DD 형식
        return pd.to_datetime(date_str, format='%Y-%m-%d')
    except:
        try:
            # 다른 형식 시도
            return pd.to_datetime(date_str)
        except:
            return None


def process_csv_row(row: pd.Series) -> Dict:
    """CSV 행을 처리하여 Welfare 모델에 맞는 딕셔너리로 변환합니다."""
    # CSV 컬럼명 (실제 파일 확인 후 수정 필요)
    # 예상 컬럼: 서비스ID, 서비스명, 서비스URL, 서비스내용, 서비스기관, 연락처, 담당부서, 서비스대상, 기준년도, 기준일자
    
    service_id = str(row.iloc[0]) if len(row) > 0 else ""
    title = clean_text(row.iloc[1]) if len(row) > 1 else ""
    url = str(row.iloc[2]) if len(row) > 2 else ""
    content = clean_text(row.iloc[3]) if len(row) > 3 else ""
    organization = clean_text(row.iloc[4]) if len(row) > 4 else ""
    contact = clean_text(row.iloc[5]) if len(row) > 5 else ""
    department = clean_text(row.iloc[6]) if len(row) > 6 else ""
    target = clean_text(row.iloc[7]) if len(row) > 7 else ""
    year = str(row.iloc[8]) if len(row) > 8 else ""
    date = str(row.iloc[9]) if len(row) > 9 else ""
    
    # full_text 구성
    full_text_parts = []
    if title:
        full_text_parts.append(f"제목: {title}")
    if content:
        full_text_parts.append(f"내용: {content}")
    if target:
        full_text_parts.append(f"대상: {target}")
    if organization:
        full_text_parts.append(f"기관: {organization}")
    if contact:
        full_text_parts.append(f"연락처: {contact}")
    
    full_text = "\n".join(full_text_parts)
    
    # 지역 추출
    region = extract_region(full_text)
    
    # 나이 범위 추출
    age_min, age_max = extract_age_range(full_text)
    
    # 연락처 정보 파싱
    contact_info = parse_contact_info(contact)
    
    # 날짜 파싱
    apply_date = parse_date(date)
    
    return {
        'title': title,
        'summary': None,  # 나중에 LLM으로 생성
        'full_text': full_text,
        'source_link': url if url and url.startswith('http') else None,
        'region': region,
        'age_min': age_min,
        'age_max': age_max,
        'care_target': target if target else None,
        'apply_start': None,  # CSV에 신청기간 정보가 없으면 None
        'apply_end': None,
        'is_always': True,  # 기본값
        'status': 'active',
        'category': 'SERVICE',  # 실제 복지 서비스로 분류
        'embedding': None,  # 나중에 생성
    }


def load_and_process_csv(csv_path: str) -> pd.DataFrame:
    """CSV 파일을 로드하고 전처리합니다."""
    logger.info(f"CSV 파일 로드 중: {csv_path}")
    
    # 인코딩 감지
    try:
        encoding = detect_encoding(csv_path)
        # CP949가 감지되면 EUC-KR도 시도
        if encoding.lower() in ['cp949', 'euc-kr']:
            encodings_to_try = ['cp949', 'euc-kr', 'utf-8-sig']
        else:
            encodings_to_try = [encoding, 'utf-8-sig', 'cp949']
    except:
        encodings_to_try = ['cp949', 'euc-kr', 'utf-8-sig']
    
    df = None
    for enc in encodings_to_try:
        try:
            df = pd.read_csv(csv_path, encoding=enc)
            logger.info(f"성공적으로 로드됨 (인코딩: {enc})")
            break
        except Exception as e:
            logger.warning(f"인코딩 {enc} 실패: {e}")
            continue
    
    if df is None:
        raise ValueError("CSV 파일을 읽을 수 없습니다. 인코딩 문제일 수 있습니다.")
    
    logger.info(f"총 {len(df)}개의 행이 로드되었습니다.")
    logger.info(f"컬럼: {df.columns.tolist()}")
    
    return df


def save_to_db(db: Session, welfare_data: Dict, service_id: str = None) -> models.Welfare:
    """복지 정보를 DB에 저장합니다."""
    # service_id로 중복 체크 (source_link 기반)
    existing = None
    if service_id:
        # source_link에서 service_id 추출하여 검색
        existing = db.query(models.Welfare).filter(
            models.Welfare.source_link.like(f'%{service_id}%')
        ).first()
    
    if existing:
        # 업데이트
        for key, value in welfare_data.items():
            if value is not None:
                setattr(existing, key, value)
        existing.updated_at = datetime.now()
        db.commit()
        db.refresh(existing)
        return existing
    else:
        # 새로 생성
        welfare = models.Welfare(**welfare_data)
        db.add(welfare)
        db.commit()
        db.refresh(welfare)
        return welfare


def process_csv_to_db(csv_path: str, db: Session, batch_size: int = 100):
    """CSV 파일을 처리하여 DB에 저장합니다."""
    df = load_and_process_csv(csv_path)
    
    saved_count = 0
    updated_count = 0
    error_count = 0
    
    for idx, row in df.iterrows():
        try:
            service_id = str(row.iloc[0]) if len(row) > 0 else None
            welfare_data = process_csv_row(row)
            
            # 기존 데이터 확인
            existing = None
            if service_id:
                existing = db.query(models.Welfare).filter(
                    models.Welfare.source_link.like(f'%{service_id}%')
                ).first()
            
            if existing:
                # 업데이트
                for key, value in welfare_data.items():
                    if value is not None:
                        setattr(existing, key, value)
                existing.updated_at = datetime.now()
                updated_count += 1
            else:
                # 새로 생성
                welfare = models.Welfare(**welfare_data)
                db.add(welfare)
                saved_count += 1
            
            # 배치 커밋
            if (idx + 1) % batch_size == 0:
                db.commit()
                logger.info(f"진행 중: {idx + 1}/{len(df)} (저장: {saved_count}, 업데이트: {updated_count}, 에러: {error_count})")
        
        except Exception as e:
            error_count += 1
            logger.error(f"행 {idx + 1} 처리 중 오류: {e}")
            continue
    
    # 마지막 커밋
    db.commit()
    
    logger.info(f"처리 완료: 총 {len(df)}개 중 저장 {saved_count}개, 업데이트 {updated_count}개, 에러 {error_count}개")
    
    return {
        'total': len(df),
        'saved': saved_count,
        'updated': updated_count,
        'errors': error_count
    }


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='CSV 파일을 DB에 저장')
    parser.add_argument('csv_path', type=str, help='CSV 파일 경로')
    parser.add_argument('--batch-size', type=int, default=100, help='배치 크기')
    
    args = parser.parse_args()
    
    # DB 초기화
    init_db()
    db = next(get_db())
    
    try:
        result = process_csv_to_db(args.csv_path, db, batch_size=args.batch_size)
        print(f"\n처리 완료!")
        print(f"총: {result['total']}개")
        print(f"저장: {result['saved']}개")
        print(f"업데이트: {result['updated']}개")
        print(f"에러: {result['errors']}개")
    except Exception as e:
        logger.error(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

