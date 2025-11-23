"""view_count 컬럼 NULL 값 수정 스크립트"""
import sqlite3
import sys
import os

# Windows에서 UTF-8 출력 설정
if sys.platform == 'win32':
    os.system('chcp 65001 > nul')

def fix_view_count():
    try:
        conn = sqlite3.connect('neulbom.db')
        cursor = conn.cursor()
        
        # view_count가 NULL인 데이터 개수 확인
        cursor.execute('SELECT COUNT(*) FROM welfares WHERE view_count IS NULL')
        null_count = cursor.fetchone()[0]
        print(f'view_count가 NULL인 데이터: {null_count}개')
        
        if null_count > 0:
            # NULL 값을 0으로 업데이트
            cursor.execute('UPDATE welfares SET view_count = 0 WHERE view_count IS NULL')
            conn.commit()
            print(f'view_count가 NULL인 {null_count}개 데이터를 0으로 업데이트했습니다.')
        else:
            print('view_count가 NULL인 데이터가 없습니다.')
        
        # 확인
        cursor.execute('SELECT COUNT(*) FROM welfares WHERE view_count IS NULL')
        remaining_null = cursor.fetchone()[0]
        print(f'남은 NULL 데이터: {remaining_null}개')
        
        conn.close()
        print('작업 완료!')
        
    except Exception as e:
        print(f'오류 발생: {e}')
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    fix_view_count()

