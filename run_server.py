import uvicorn
import logging
import sys
import socket
import os

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('server_startup.log', encoding='utf-8')
    ]
)


def is_port_in_use(port: int) -> bool:
    """포트가 사용 중인지 확인"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0


def find_available_port(start_port: int = 8000, max_attempts: int = 10) -> int:
    """사용 가능한 포트 찾기"""
    for port in range(start_port, start_port + max_attempts):
        if not is_port_in_use(port):
            return port
    raise RuntimeError(f"포트 {start_port}부터 {start_port + max_attempts - 1}까지 모두 사용 중입니다.")


if __name__ == "__main__":
    print("Starting server script...")
    
    # 포트 설정 (환경변수 또는 기본값)
    port = int(os.getenv("PORT", "8000"))
    
    # 포트가 사용 중이면 다른 포트 시도
    if is_port_in_use(port):
        print(f"⚠️  포트 {port}가 이미 사용 중입니다. 다른 포트를 찾는 중...")
        try:
            port = find_available_port(port + 1)
            print(f"✅ 포트 {port}를 사용합니다.")
        except RuntimeError as e:
            print(f"❌ {e}")
            print("💡 해결 방법:")
            print("   1. 포트를 사용하는 프로세스를 종료하세요:")
            print(f"      netstat -ano | findstr :{port}")
            print("   2. 또는 다른 포트를 지정하세요:")
            print("      set PORT=8001")
            print("      python run_server.py")
            sys.exit(1)
    
    try:
        # app.main import
        from app.main import app
        print("App imported successfully.")
        
        print(f"🚀 서버 시작 중... (포트: {port})")
        print(f"📖 API 문서: http://localhost:{port}/docs")
        print(f"💚 헬스 체크: http://localhost:{port}/health")
        
        # uvicorn run
        uvicorn.run(app, host="0.0.0.0", port=port)
    except OSError as e:
        if "10048" in str(e) or "address already in use" in str(e).lower():
            print(f"❌ 포트 {port}가 이미 사용 중입니다.")
            print("💡 해결 방법:")
            print(f"   1. 포트를 사용하는 프로세스 확인: netstat -ano | findstr :{port}")
            print(f"   2. 프로세스 종료: taskkill /PID <PID> /F")
            print(f"   3. 또는 다른 포트 사용: set PORT=8001 && python run_server.py")
        else:
            print(f"Server failed to start: {e}")
        logging.error(f"Server failed: {e}", exc_info=True)
        sys.exit(1)
    except Exception as e:
        print(f"Server failed to start: {e}")
        logging.error(f"Server failed: {e}", exc_info=True)
        sys.exit(1)

