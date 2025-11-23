import uvicorn
import logging
import sys

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('server_startup.log', encoding='utf-8')
    ]
)

if __name__ == "__main__":
    print("Starting server script...")
    try:
        # app.main import
        from app.main import app
        print("App imported successfully.")
        
        # uvicorn run
        uvicorn.run(app, host="0.0.0.0", port=8000)
    except Exception as e:
        print(f"Server failed to start: {e}")
        logging.error(f"Server failed: {e}", exc_info=True)

