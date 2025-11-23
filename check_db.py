"""데이터베이스 데이터 확인 스크립트"""
import sqlite3
import sys
import os

# Windows에서 UTF-8 출력 설정
if sys.platform == 'win32':
    os.system('chcp 65001 > nul')

def check_database():
    try:
        conn = sqlite3.connect('neulbom.db')
        cursor = conn.cursor()
        
        # 테이블 목록 확인
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print("=" * 60)
        print("데이터베이스 테이블 목록:")
        for table in tables:
            print(f"  - {table[0]}")
        print("=" * 60)
        
        # category 컬럼 존재 여부 확인 (먼저 확인)
        cursor.execute("PRAGMA table_info(welfares)")
        columns = [col[1] for col in cursor.fetchall()]
        has_category = 'category' in columns
        
        # welfares 테이블 데이터 확인
        cursor.execute("SELECT COUNT(*) FROM welfares")
        count = cursor.fetchone()[0]
        print(f"\n총 복지 정보 개수: {count}")
        
        if count > 0:
            # 샘플 데이터 조회 (category 컬럼이 있으면 포함)
            if has_category:
                cursor.execute("SELECT id, title, category, summary FROM welfares LIMIT 10")
            else:
                cursor.execute("SELECT id, title, NULL, summary FROM welfares LIMIT 10")
            rows = cursor.fetchall()
            
            print("\n" + "=" * 60)
            print("샘플 데이터 (최대 10개):")
            print("=" * 60)
            
            for row in rows:
                welfare_id, title, category, summary = row
                print(f"\n[ID: {welfare_id}]")
                print(f"  제목: {title}")
                if has_category:
                    print(f"  카테고리: {category}")
                if summary:
                    summary_preview = summary[:100] + "..." if len(summary) > 100 else summary
                    print(f"  요약: {summary_preview}")
        
        if has_category:
            cursor.execute("SELECT COUNT(*) FROM welfares WHERE category IS NULL")
            null_category_count = cursor.fetchone()[0]
            print(f"\n카테고리가 NULL인 데이터: {null_category_count}개")
        else:
            print(f"\n[경고] 'category' 컬럼이 아직 데이터베이스에 없습니다.")
        
        # 한글 텍스트가 있는지 확인
        cursor.execute("SELECT id, title FROM welfares WHERE title LIKE '%가족%' OR title LIKE '%청년%' LIMIT 5")
        korean_rows = cursor.fetchall()
        if korean_rows:
            print("\n한글 키워드 포함 데이터 샘플:")
            for row in korean_rows:
                print(f"  ID {row[0]}: {row[1]}")
        
        conn.close()
        print("\n" + "=" * 60)
        print("데이터베이스 확인 완료!")
        print("=" * 60)
        
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    check_database()

