import threading
import logging
import time
import cv2
import queue
cv2.setNumThreads(3)

from config.settings import Settings

from models.yolo import YOLOProcessor
from services.rtsp_client import RTSPClient
from services.rtsp_server import RTSPServer

logging.basicConfig(
	level=logging.INFO,
	format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class FrameProcessor:
	def __init__(self, rtsp_client, rtsp_server, yolo_processor):
		self.rtsp_client = rtsp_client
		self.rtsp_server = rtsp_server
		self.yolo_processor = yolo_processor
		self.running = False

	def start(self):
		self.running = True
		threading.Thread(target=self._process_frames, daemon=True).start()

	def stop(self):
		self.running = False

	def _process_frames(self):
		logger.info("Starting frame processing thread.")
		start_time = time.time()
		frame_count = 0

		while self.running:
			try:
				frame = self.rtsp_client.get_frame()
				if frame is not None:
					annotated_frame, objects = self.yolo_processor.process_frame(frame)
					logger.info(f"Processed frame with {objects} objects detected.")

					frame_count += 1
					elapsed_time = time.time() - start_time
					fps = frame_count / elapsed_time

					cv2.putText(
						annotated_frame, f"FPS: {fps:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2
					)

					self.rtsp_server.push_frame(annotated_frame)
			except Exception as e:
				logger.error(f"Error during frame processing: {e}")

def main():
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

	frame_processor = FrameProcessor(rtsp_client, rtsp_server, yolo_processor)
	
	try:
		rtsp_server.start()
		rtsp_client.start()
		frame_processor.start()
		
		logger.info("System is running. Press Ctrl+C to stop.")
		while True:
			time.sleep(0.01)

	except KeyboardInterrupt:
		logger.info("Shutting down...")
	finally:
		frame_processor.stop()
		rtsp_client.stop()
		rtsp_server.stop()

if __name__ == "__main__":
	main()
