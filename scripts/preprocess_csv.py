"""
CSV 전처리 실행 스크립트 (편의용)
"""

import sys
import os
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Windows에서 한글 출력을 위한 인코딩 설정
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from app.data_processing.preprocess import main

if __name__ == "__main__":
    # CSV 파일 경로 (프로젝트 루트 기준)
    csv_file = project_root.parent / "한국사회보장정보원_복지서비스정보_20250722.csv"
    
    if not csv_file.exists():
        print(f"오류: CSV 파일을 찾을 수 없습니다: {csv_file}")
        print("CSV 파일 경로를 확인하세요.")
        sys.exit(1)
    
    # sys.argv 설정
    import argparse
    
    parser = argparse.ArgumentParser(description='CSV 파일 전처리')
    parser.add_argument('--filter-youth', action='store_true', help='청년 관련 데이터만 필터링')
    parser.add_argument('--no-filter', action='store_true', help='필터링 하지 않음')
    parser.add_argument('--keywords', nargs='+', help='필터링 키워드')
    parser.add_argument('--output-dir', type=str, default='./data/preprocessed', help='출력 디렉토리')
    
    args = parser.parse_args()
    
    # sys.argv 재구성
    sys.argv = [
        "preprocess_csv.py",
        str(csv_file),
        "--output-dir", args.output_dir
    ]
    
    if args.filter_youth:
        sys.argv.append("--filter-youth")
    if args.no_filter:
        sys.argv.append("--no-filter")
    if args.keywords:
        sys.argv.extend(["--keywords"] + args.keywords)
    
    main()

