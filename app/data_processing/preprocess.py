"""
CSV 파일 전처리 스크립트
- 컬럼 분석
- 텍스트 병합 (search_content 생성)
- 청년 필터링 (옵션)
- JSON/CSV 저장
"""

import sys
import os
from pathlib import Path
import pandas as pd
import json
import chardet
from typing import List, Optional, Dict
import re

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def detect_encoding(file_path: str) -> str:
    """CSV 파일의 인코딩을 감지합니다."""
    with open(file_path, 'rb') as f:
        raw_data = f.read(10000)
        result = chardet.detect(raw_data)
        encoding = result['encoding']
        logger.info(f"감지된 인코딩: {encoding} (신뢰도: {result['confidence']:.2f})")
        return encoding


def analyze_columns(df: pd.DataFrame) -> Dict:
    """컬럼 구조를 분석합니다."""
    logger.info("=" * 80)
    logger.info("컬럼 분석")
    logger.info("=" * 80)
    
    columns_info = {
        'total_columns': len(df.columns),
        'column_names': df.columns.tolist(),
        'column_types': df.dtypes.to_dict(),
        'null_counts': df.isnull().sum().to_dict(),
        'sample_data': {}
    }
    
    logger.info(f"\n총 컬럼 수: {len(df.columns)}")
    logger.info(f"\n컬럼 목록:")
    for i, col in enumerate(df.columns, 1):
        null_count = df[col].isnull().sum()
        null_pct = (null_count / len(df)) * 100
        logger.info(f"  {i:2d}. {col:20s} | Null: {null_count:4d} ({null_pct:5.1f}%)")
        
        # 샘플 데이터 (첫 번째 non-null 값)
        sample = df[col].dropna().iloc[0] if not df[col].dropna().empty else None
        if sample:
            sample_str = str(sample)[:50] + "..." if len(str(sample)) > 50 else str(sample)
            columns_info['sample_data'][col] = sample_str
    
    # 주요 컬럼 찾기
    column_lower = {col.lower(): col for col in df.columns}
    
    key_columns = {
        'service_id': None,
        'service_name': None,
        'service_purpose': None,
        'target': None,
        'criteria': None,
        'service_url': None,
        'service_content': None,
        'organization': None,
        'contact': None,
    }
    
    # 서비스ID 찾기
    for key in ['서비스id', '서비스id', 'id', 'service_id', 'serviceid', '서비스id']:
        if key in column_lower:
            key_columns['service_id'] = column_lower[key]
            break
    
    # 서비스명 찾기
    for key in ['서비스명', 'service_name', 'servicename', 'title', '제목']:
        if key in column_lower:
            key_columns['service_name'] = column_lower[key]
            break
    
    # 서비스목적 찾기
    for key in ['서비스목적', 'service_purpose', 'purpose', '목적']:
        if key in column_lower:
            key_columns['service_purpose'] = column_lower[key]
            break
    
    # 지원대상 찾기
    for key in ['지원대상', '서비스대상', '대상', 'target', 'support_target', 'service_target', '서비스대상']:
        if key in column_lower:
            key_columns['target'] = column_lower[key]
            break
    
    # 선정기준 찾기
    for key in ['선정기준', 'criteria', 'selection_criteria', '기준']:
        if key in column_lower:
            key_columns['criteria'] = column_lower[key]
            break
    
    # 서비스URL 찾기
    for key in ['서비스url', 'url', 'service_url', 'link', '링크']:
        if key in column_lower:
            key_columns['service_url'] = column_lower[key]
            break
    
    # 서비스내용 찾기
    for key in ['서비스내용', 'content', 'service_content', '내용', '설명']:
        if key in column_lower:
            key_columns['service_content'] = column_lower[key]
            break
    
    # 서비스기관 찾기
    for key in ['서비스기관', '기관', 'organization', 'org', '담당부서', '서비스기관']:
        if key in column_lower:
            key_columns['organization'] = column_lower[key]
            break
    
    # 연락처 찾기
    for key in ['연락처', 'contact', '전화', 'phone']:
        if key in column_lower:
            key_columns['contact'] = column_lower[key]
            break
    
    columns_info['key_columns'] = {k: v for k, v in key_columns.items() if v is not None}
    
    logger.info(f"\n주요 컬럼 매핑:")
    for key, col in key_columns.items():
        if col:
            logger.info(f"  {key:20s} -> {col}")
    
    return columns_info


def clean_text(text) -> str:
    """텍스트를 정제합니다."""
    if pd.isna(text) or text is None:
        return ""
    
    text = str(text).strip()
    # HTML 태그 제거
    text = re.sub(r'<[^>]+>', '', text)
    # 연속된 공백 제거
    text = re.sub(r'\s+', ' ', text)
    return text


def merge_text_columns(df: pd.DataFrame, columns_info: Dict) -> pd.DataFrame:
    """여러 컬럼의 텍스트를 병합하여 search_content를 생성합니다."""
    logger.info("\n" + "=" * 80)
    logger.info("텍스트 병합 (search_content 생성)")
    logger.info("=" * 80)
    
    key_cols = columns_info['key_columns']
    
    # 병합할 컬럼 목록
    merge_columns = []
    
    if key_cols.get('service_name'):
        merge_columns.append(key_cols['service_name'])
    if key_cols.get('service_purpose'):
        merge_columns.append(key_cols['service_purpose'])
    if key_cols.get('target'):
        merge_columns.append(key_cols['target'])
    if key_cols.get('service_content'):
        merge_columns.append(key_cols['service_content'])
    if key_cols.get('criteria'):
        merge_columns.append(key_cols['criteria'])
    
    logger.info(f"\n병합할 컬럼: {merge_columns}")
    
    # search_content 생성
    def merge_row(row):
        parts = []
        for col in merge_columns:
            if col in row.index:
                text = clean_text(row[col])
                if text:
                    parts.append(text)
        return " ".join(parts)
    
    df['search_content'] = df.apply(merge_row, axis=1)
    
    # 빈 search_content 확인
    empty_count = df['search_content'].str.strip().eq('').sum()
    logger.info(f"\n생성된 search_content:")
    logger.info(f"  - 총 행 수: {len(df)}")
    logger.info(f"  - 빈 내용: {empty_count}개 ({(empty_count/len(df)*100):.1f}%)")
    logger.info(f"  - 평균 길이: {df['search_content'].str.len().mean():.1f}자")
    
    # 샘플 출력
    logger.info(f"\n샘플 search_content (처음 3개):")
    for idx, content in enumerate(df['search_content'].head(3), 1):
        preview = content[:100] + "..." if len(content) > 100 else content
        logger.info(f"  {idx}. {preview}")
    
    return df


def filter_youth_related(df: pd.DataFrame, keywords: Optional[List[str]] = None) -> pd.DataFrame:
    """청년 관련 키워드로 필터링합니다."""
    if keywords is None:
        keywords = ['청년', '학생', '장학', '생계', '의료', '돌봄', '가족', '청소년', '대학생', 
                   '취업', '주거', '주택', '생활', '지원', '급여', '수당', '보조금']
    
    logger.info("\n" + "=" * 80)
    logger.info(f"청년 관련 필터링 (키워드: {', '.join(keywords)})")
    logger.info("=" * 80)
    
    original_count = len(df)
    
    # search_content에 키워드가 포함된 행 찾기
    mask = df['search_content'].str.contains('|'.join(keywords), case=False, na=False)
    df_filtered = df[mask].copy()
    
    filtered_count = len(df_filtered)
    logger.info(f"\n필터링 결과:")
    logger.info(f"  - 원본: {original_count}개")
    logger.info(f"  - 필터링 후: {filtered_count}개")
    logger.info(f"  - 제거: {original_count - filtered_count}개 ({(1-filtered_count/original_count)*100:.1f}%)")
    
    return df_filtered


def save_results(df: pd.DataFrame, output_dir: Path, columns_info: Dict):
    """전처리된 데이터를 JSON과 CSV로 저장합니다."""
    logger.info("\n" + "=" * 80)
    logger.info("결과 저장")
    logger.info("=" * 80)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. CSV 저장
    csv_path = output_dir / "preprocessed_welfare_data.csv"
    df.to_csv(csv_path, index=False, encoding='utf-8-sig')
    logger.info(f"✓ CSV 저장: {csv_path}")
    
    # 2. JSON 저장 (각 행을 객체로)
    json_path = output_dir / "preprocessed_welfare_data.json"
    records = df.to_dict('records')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(records, f, ensure_ascii=False, indent=2)
    logger.info(f"✓ JSON 저장: {json_path}")
    
    # 3. RAG용 간소화 JSON (search_content 중심)
    rag_json_path = output_dir / "rag_welfare_data.json"
    rag_records = []
    key_cols = columns_info['key_columns']
    
    for _, row in df.iterrows():
        record = {
            'id': str(row.get(key_cols.get('service_id', ''), '')),
            'title': clean_text(row.get(key_cols.get('service_name', ''), '')),
            'search_content': row.get('search_content', ''),
            'url': str(row.get(key_cols.get('service_url', ''), '')),
        }
        
        # 추가 정보
        if key_cols.get('target'):
            record['target'] = clean_text(row.get(key_cols['target'], ''))
        if key_cols.get('organization'):
            record['organization'] = clean_text(row.get(key_cols['organization'], ''))
        if key_cols.get('contact'):
            record['contact'] = clean_text(row.get(key_cols['contact'], ''))
        
        rag_records.append(record)
    
    with open(rag_json_path, 'w', encoding='utf-8') as f:
        json.dump(rag_records, f, ensure_ascii=False, indent=2)
    logger.info(f"✓ RAG용 JSON 저장: {rag_json_path}")
    
    # 4. 통계 정보 저장
    stats_path = output_dir / "preprocessing_stats.json"
    stats = {
        'total_records': len(df),
        'columns_info': columns_info,
        'search_content_stats': {
            'avg_length': float(df['search_content'].str.len().mean()),
            'min_length': int(df['search_content'].str.len().min()),
            'max_length': int(df['search_content'].str.len().max()),
            'empty_count': int(df['search_content'].str.strip().eq('').sum()),
        }
    }
    
    with open(stats_path, 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    logger.info(f"✓ 통계 정보 저장: {stats_path}")
    
    logger.info(f"\n모든 파일이 저장되었습니다: {output_dir}")


def main():
    """메인 실행 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description='CSV 파일 전처리')
    parser.add_argument('csv_path', type=str, help='CSV 파일 경로')
    parser.add_argument('--output-dir', type=str, default='./data/preprocessed', help='출력 디렉토리')
    parser.add_argument('--filter-youth', action='store_true', help='청년 관련 데이터만 필터링')
    parser.add_argument('--keywords', nargs='+', help='필터링 키워드 (기본값: 청년, 학생, 장학 등)')
    parser.add_argument('--no-filter', action='store_true', help='필터링 하지 않음')
    
    args = parser.parse_args()
    
    csv_path = Path(args.csv_path)
    if not csv_path.exists():
        logger.error(f"CSV 파일을 찾을 수 없습니다: {csv_path}")
        return
    
    output_dir = Path(args.output_dir)
    
    try:
        # 1. CSV 파일 로드
        logger.info("=" * 80)
        logger.info("CSV 파일 로드")
        logger.info("=" * 80)
        
        encoding = detect_encoding(str(csv_path))
        encodings_to_try = [encoding, 'cp949', 'euc-kr', 'utf-8-sig']
        
        df = None
        for enc in encodings_to_try:
            try:
                df = pd.read_csv(csv_path, encoding=enc)
                logger.info(f"✓ 성공적으로 로드됨 (인코딩: {enc})")
                break
            except Exception as e:
                logger.warning(f"인코딩 {enc} 실패: {e}")
                continue
        
        if df is None:
            logger.error("CSV 파일을 읽을 수 없습니다.")
            return
        
        logger.info(f"총 {len(df)}개의 행이 로드되었습니다.")
        
        # 2. 컬럼 분석
        columns_info = analyze_columns(df)
        
        # 3. 텍스트 병합
        df = merge_text_columns(df, columns_info)
        
        # 4. 청년 필터링 (옵션)
        if args.filter_youth and not args.no_filter:
            df = filter_youth_related(df, args.keywords)
        elif args.keywords and not args.no_filter:
            df = filter_youth_related(df, args.keywords)
        
        # 5. 결과 저장
        save_results(df, output_dir, columns_info)
        
        logger.info("\n" + "=" * 80)
        logger.info("전처리 완료!")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

