from pathlib import Path
import os

class Settings:
	RTSP_URL = os.getenv("RTSP_URL", "rtsp://0.0.0.0:8553/stream")
	RETRY_INTERVAL = int(os.getenv("RETRY_INTERVAL", "5"))
	MAX_RETRY_INTERVAL = int(os.getenv("MAX_RETRY_INTERVAL", "100"))

	RTSP_OUTPUT_PORT = os.getenv("RTSP_OUTPUT_PORT", 8554)
	RTSP_OUTPUT_PATH = os.getenv("RTSP_OUTPUT_PATH", "/live")
	
	YOLO_MODEL_PATH = os.getenv("YOLO_MODEL_PATH", "forest_fire_best.pt")
	CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.4"))
	
	WEBRTC_SERVER_URL = os.getenv("WEBRTC_SERVER_URL", "ws://127.0.0.1:8000")
	
	MIN_OBJECTS_FOR_ALERT = int(os.getenv("MIN_OBJECTS_FOR_ALERT", "1"))
	
	BASE_DIR = Path(__file__).resolve().parent.parent
	LOGS_DIR = BASE_DIR / "logs"
	
	def __init__(self):
		self.LOGS_DIR.mkdir(exist_ok=True)

