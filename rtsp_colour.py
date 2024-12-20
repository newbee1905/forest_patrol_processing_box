import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0')
import numpy as np
import threading
from gi.repository import Gst, GstRtspServer, GLib
import time
import cv2

# Initialize GStreamer
Gst.init(None)


class CustomRTSPMediaFactory(GstRtspServer.RTSPMediaFactory):
	def __init__(self):
		super(CustomRTSPMediaFactory, self).__init__()
		self.frame = None
		self.lock = threading.Lock()
		self.pipeline_str = (
			"appsrc name=source is-live=true format=GST_FORMAT_TIME "
			"caps=video/x-raw,format=RGB,width=640,height=480,framerate=30/1 "
			"! videoconvert ! x264enc speed-preset=ultrafast tune=zerolatency "
			"! rtph264pay config-interval=1 name=pay0 pt=96"
		)
		self.timestamp = 0

	def set_frame(self, frame):
		with self.lock:
			self.frame = frame
	
	def on_need_data(self, src, length):
		try:
			with self.lock:
				if self.frame is not None:
					data = self.frame.tobytes()
					buf = Gst.Buffer.new_allocate(None, len(data), None)
					buf.fill(0, data)
					buf.duration = Gst.SECOND // 30	# 30 fps
					buf.pts = buf.dts = self.timestamp
					buf.offset = self.timestamp
					self.timestamp += buf.duration
					retval = src.emit("push-buffer", buf)
					if retval != Gst.FlowReturn.OK:
						print("Push buffer error:", retval)
		except Exception as e:
			print(f"Error in on_need_data: {e}")

	def do_create_element(self, url):
		return Gst.parse_launch(self.pipeline_str)

	def do_configure(self, rtsp_media):
		self.appsrc = rtsp_media.get_element().get_by_name("source")
		self.appsrc.connect("need-data", self.on_need_data)


class RTSPServer:
	def __init__(self, port, path):
		self.server = GstRtspServer.RTSPServer()
		self.factory = CustomRTSPMediaFactory()
		self.factory.set_shared(True)
		self.server.set_address("0.0.0.0")
		self.server.set_service(str(port))
		self.mount_points = self.server.get_mount_points()
		self.mount_points.add_factory(path, self.factory)
		self.server.attach(None)
		print(f"RTSP server is running at rtsp://0.0.0.0:{port}{path}")

		self.loop = GLib.MainLoop()

	def start(self):
		print("Starting GLib Main Loop...")
		# self.loop.run()
		self.loop_thread = threading.Thread(target=self.loop.run)
		self.loop_thread.start()

	def stop(self):
		if self.loop is not None:
			print("Stopping RTSP server...")
			self.loop.quit()
			self.loop_thread.join()
			self.loop = None

	def push_frame(self, frame):
		self.factory.set_frame(frame)


def main():
	server = RTSPServer(8554, "/stream")

	def feed_random_frames():
		while True:
			# Generate a random color frame (640x480)
			random_frame = np.random.randint(0, 256, (480, 640, 3), dtype=np.uint8)
			random_frame = cv2.cvtColor(random_frame, cv2.COLOR_BGR2RGB)
			server.push_frame(random_frame)

			time.sleep(1 // 30)

	feed_thread = threading.Thread(target=feed_random_frames, daemon=True)
	feed_thread.start()

	try:
		server.start()
	except KeyboardInterrupt:
		print("Shutting down RTSP server...")
		server.stop()

if __name__ == "__main__":
	main()

