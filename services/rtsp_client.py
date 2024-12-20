import cv2
import time
from datetime import datetime
import logging
from typing import Optional, Callable
import threading
import queue
from concurrent.futures import ThreadPoolExecutor

class RTSPClient:
	def __init__(self, url: str, retry_interval: int = 5, max_retry_interval: int = 100, queue_size: int = 60):
		self.url = url

		self.initial_retry_interval = retry_interval
		self.max_retry_interval = max_retry_interval
		self.current_retry_interval = retry_interval

		self.queue_size = queue_size
		self.frame_queue = queue.Queue(maxsize=queue_size)
		self.cap: Optional[cv2.VideoCapture] = None
		self.running = False
		self.executor = ThreadPoolExecutor(max_workers=1)

		self.logger = logging.getLogger(__name__)
		
	def start(self):
		self.running = True
		threading.Thread(target=self._run, daemon=True).start()

	def stop(self):
		"""Stop the RTSP client."""
		self.running = False
		if self.cap:
			self.cap.release()
	
	def _connect(self) -> bool:
		try:
			if self.cap is not None:
				self.cap.release()
			
			self.cap = cv2.VideoCapture(self.url)
			if not self.cap.isOpened():
				self.logger.error(f"Failed to connect to {self.url}")
				return False

			# self.cap.set(cv2.CAP_PROP_HW_ACCELERATION, cv2.VIDEO_ACCELERATION_NONE)
			
			self.logger.info(f"Successfully connected to {self.url}")
			self.current_retry_interval = self.initial_retry_interval
			return True
		except Exception as e:
			self.logger.error(f"Error connecting to stream: {str(e)}")
			return False
	
	def _run(self):
		while self.running:
			if not self._connect():
				self._handle_retry()
				continue
			
			try:
				while self.running:
					ret, frame = self.cap.read()
					if not ret or frame is None:
						self.logger.warning("Failed to retrieve frame")
						break
					
					# if self.frame_callback:
					# 	self.frame_callback(frame)
					if not self.frame_queue.full():
						self.frame_queue.put(frame)
					else:
						self.logger.warning("Frame queue is full. Dropping frame.")
						self.frame_queue.get()
			
			except Exception as e:
				self.logger.error(f"Error during streaming: {str(e)}")
			
			if self.running:
				self._handle_retry()
	
	def _handle_retry(self):
		self.logger.info(f"Retrying connection in {self.current_retry_interval} seconds")
		time.sleep(self.current_retry_interval)
		self.current_retry_interval = min(
			self.current_retry_interval * 1.5, 
			self.max_retry_interval
		)
	
	def get_frame(self):
		frame = self.frame_queue.get()
		self.logger.info(f"Frame retrieved from queue. Queue size: {self.frame_queue.qsize()}")
		return frame
