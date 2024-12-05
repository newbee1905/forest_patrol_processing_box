import asyncio
import logging
import time
import cv2

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
			annotated_frame, objects = yolo_processor.process_frame(frame)
			# annotated_frame = annotated_frame.squeeze(0).permute(1, 2, 0).cpu().numpy()
			# cv2.imwrite(f"{time.time()}.jpg", annotated_frame)
			print(annotated_frame.shape)
			rtsp_server.push_frame(annotated_frame)
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
