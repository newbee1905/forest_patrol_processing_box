from ultralytics import YOLO
import logging
import numpy as np

class YOLOProcessor:
	def __init__(self, model_path: str = 'forest_fire_best.pt', conf_threshold=0.7):
		self.model = YOLO(model_path)
		self.logger = logging.getLogger(__name__)
		self.conf_threshold = conf_threshold

	def process_frame(self, frame: np.ndarray) -> tuple[np.ndarray, int]:
		try:
			results = self.model(frame, conf=self.conf_threshold)
			annotated_frame = results[0].plot()
			num_objects = len(results[0].boxes)

			return annotated_frame, num_objects
		except Exception as e:
			self.logger.error(f"Error processing frame: {e}")
			return frame, 0
