import cv2
import time
from datetime import datetime
import logging
from typing import Optional, Callable
import threading

class RTSPClient:
	def __init__(self, url: str, retry_interval: int = 5, max_retry_interval: int = 100):
		self.url = url

		self.initial_retry_interval = retry_interval
		self.max_retry_interval = max_retry_interval
		self.current_retry_interval = retry_interval

		self.cap: Optional[cv2.VideoCapture] = None
		self.running = False
		self.frame_callback: Optional[Callable] = None

		self.logger = logging.getLogger(__name__)
		
	def start(self, frame_callback: Callable):
		"""Start the RTSP client with a callback for frame processing."""
		self.frame_callback = frame_callback
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
					
					if self.frame_callback:
						self.frame_callback(frame)
			
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
