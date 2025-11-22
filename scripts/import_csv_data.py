"""
CSV 데이터 임포트 실행 스크립트 (편의용)
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

from app.data_processing.import_csv import main

if __name__ == "__main__":
    # CSV 파일 경로 (프로젝트 루트 기준)
    csv_file = project_root.parent / "한국사회보장정보원_복지서비스정보_20250722.csv"
    
    if not csv_file.exists():
        print(f"오류: CSV 파일을 찾을 수 없습니다: {csv_file}")
        print("CSV 파일 경로를 확인하세요.")
        sys.exit(1)
    
    # sys.argv 설정
    sys.argv = [
        "import_csv_data.py",
        str(csv_file),
        "--batch-size", "100"
    ]
    
    main()

