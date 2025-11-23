"""복지 서비스 검색 상태 확인 스크립트"""
import sqlite3
import sys
import os

# Windows에서 UTF-8 출력 설정
if sys.platform == 'win32':
    os.system('chcp 65001 > nul')

def check_welfare_search():
    try:
        conn = sqlite3.connect('neulbom.db')
        cursor = conn.cursor()
        
        # 전체 복지 정보 개수
        cursor.execute("SELECT COUNT(*) FROM welfares")
        total = cursor.fetchone()[0]
        print(f"전체 복지 정보: {total}개")
        
        # full_text가 있는 데이터 개수
        cursor.execute("SELECT COUNT(*) FROM welfares WHERE full_text IS NOT NULL AND full_text != ''")
        with_full_text = cursor.fetchone()[0]
        print(f"full_text가 있는 데이터: {with_full_text}개")
        print(f"full_text가 없는 데이터: {total - with_full_text}개")
        
        # summary가 있는 데이터 개수
        cursor.execute("SELECT COUNT(*) FROM welfares WHERE summary IS NOT NULL AND summary != ''")
        with_summary = cursor.fetchone()[0]
        print(f"summary가 있는 데이터: {with_summary}개")
        print(f"summary가 없는 데이터: {total - with_summary}개")
        
        # 샘플 데이터 확인
        print("\n" + "=" * 60)
        print("샘플 데이터 (최대 5개):")
        print("=" * 60)
        cursor.execute("SELECT id, title, summary, full_text FROM welfares LIMIT 5")
        rows = cursor.fetchall()
        for row in rows:
            welfare_id, title, summary, full_text = row
            print(f"\n[ID: {welfare_id}]")
            print(f"  제목: {title[:50] if title else 'None'}...")
            print(f"  summary: {'있음' if summary else '없음'}")
            print(f"  full_text: {'있음' if full_text else '없음'}")
            if full_text:
                print(f"  full_text 내용: {full_text[:100]}...")
        
        # 검색 테스트
        print("\n" + "=" * 60)
        print("검색 테스트:")
        print("=" * 60)
        
        # 키워드 검색 테스트
        test_keywords = ['노인', '장애인', '청년']
        for keyword in test_keywords:
            cursor.execute(
                "SELECT COUNT(*) FROM welfares WHERE title LIKE ? OR summary LIKE ?",
                (f'%{keyword}%', f'%{keyword}%')
            )
            count = cursor.fetchone()[0]
            print(f"'{keyword}' 검색 결과: {count}개")
        
        conn.close()
        print("\n" + "=" * 60)
        print("검색 상태 확인 완료!")
        print("=" * 60)
        
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    check_welfare_search()

