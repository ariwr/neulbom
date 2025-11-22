"""
CSV 파일 구조 분석 스크립트
"""

import pandas as pd
import chardet
from pathlib import Path

# CSV 파일 경로
csv_path = Path(__file__).parent.parent.parent.parent / "한국사회보장정보원_복지서비스정보_20250722.csv"

# 인코딩 감지
print("인코딩 감지 중...")
with open(csv_path, 'rb') as f:
    raw = f.read(10000)
    enc_result = chardet.detect(raw)
    encoding = enc_result['encoding']
    print(f"감지된 인코딩: {encoding} (신뢰도: {enc_result['confidence']:.2f})")

# CSV 읽기
print("\nCSV 파일 읽는 중...")
try:
    df = pd.read_csv(csv_path, encoding=encoding, nrows=10)
except:
    # CP949 시도
    df = pd.read_csv(csv_path, encoding='cp949', nrows=10)

print(f"\n총 행 수 (샘플): {len(df)}")
print(f"\n컬럼 목록 ({len(df.columns)}개):")
for i, col in enumerate(df.columns, 1):
    print(f"  {i}. {col}")

print("\n첫 3행 데이터:")
print(df.head(3).to_string())

print("\n컬럼별 데이터 타입:")
print(df.dtypes)

print("\n컬럼별 null 값 개수:")
print(df.isnull().sum())

