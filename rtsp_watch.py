import cv2
import queue
import time
import threading
import logging
from models.yolo import YOLOProcessor
from config.settings import Settings

logging.basicConfig(
	level=logging.INFO,
	format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

q = queue.Queue(maxsize=100)

settings = Settings()

yolo_processor = YOLOProcessor(
	settings.YOLO_MODEL_PATH,
	settings.CONFIDENCE_THRESHOLD,
)

stop_event = threading.Event()

def Receive():
	logger.info("start Reveive")
	cap = cv2.VideoCapture("rtsp://0.0.0.0:8553/stream")

	cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'H264'))
	cap.set(cv2.CAP_PROP_BUFFERSIZE, 3)

	cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
	cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
	cap.set(cv2.CAP_PROP_FPS, 60)

	while not stop_event.is_set():
		ret, frame = cap.read()

		if ret:
			if not q.full():
				q.put(frame)
		else:
			logger.error("Failed to read from stream. Retrying...")
			time.sleep(0.1)

	cap.release()
	logger.info("Receive Thread Stopped")

def Display():
	logger.info("Start Displaying")
	start_time = time.time()
	frame_count = 0

	while not stop_event.is_set():
		if q.empty() != True:
			frame = q.get()

			frame_count += 1
			elapsed_time = time.time() - start_time
			fps = frame_count / elapsed_time

			cv2.putText(
				frame,
				f"FPS: {fps:.2f}",
				(10, 30),
				cv2.FONT_HERSHEY_SIMPLEX,
				1,
				(0, 255, 0),
				2,
			)

			cv2.imshow("Camera", frame)

		if cv2.waitKey(1) & 0xFF == ord('q'):
			break

	cv2.destroyAllWindows()
	logger.info("Display Thread Stopped")
			
if __name__=='__main__':

	receive_thread = threading.Thread(target=Receive)
	display_thread = threading.Thread(target=Display)

	try:
		receive_thread.start()
		display_thread.start()
		
		logger.info("System is running. Press Ctrl+C to stop.")
		while True:
			time.sleep(0.1)

	except KeyboardInterrupt:
		logger.info("Shutting down...")
