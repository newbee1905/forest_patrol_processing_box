import asyncio
import logging

from config.settings import Settings

from models.yolo import YOLOProcessor
from services.rtsp_client import RTSPClient
from services.rtsp_server import RTSPServer

logging.basicConfig(
	level=logging.INFO,
	format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
	settings = Settings()

	yolo_processor = YOLOProcessor(
		settings.YOLO_MODEL_PATH,
		settings.CONFIDENCE_THRESHOLD,

	)
	rtsp_client = RTSPClient(settings.RTSP_URL)

	rtsp_server = RTSPServer(
		port=settings.RTSP_OUTPUT_PORT,
		path=settings.RTSP_OUTPUT_PATH,
	)
	
	try:
		rtsp_server.start()

		def frame_callback(frame):
			rtsp_server.push_frame(frame)
		rtsp_client.start(frame_callback)
		
		while True:
			await asyncio.sleep(1)

	except KeyboardInterrupt:
		logger.info("Shutting down...")
	finally:
		rtsp_server.stop()
		rtsp_client.stop()

if __name__ == "__main__":
	asyncio.run(main())
