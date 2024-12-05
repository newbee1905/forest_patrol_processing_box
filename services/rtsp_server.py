import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0')
from gi.repository import Gst, GstRtspServer, GLib
import threading
from concurrent.futures import ThreadPoolExecutor
import asyncio
import cv2
import numpy as np

Gst.init(None)

class CustomRTSPMediaFactory(GstRtspServer.RTSPMediaFactory):
	def __init__(self):
		super(CustomRTSPMediaFactory, self).__init__()
		self.frame = None
		self.pipeline_str = (
			"appsrc name=source is-live=true format=GST_FORMAT_TIME "
			"caps=video/x-raw,format=RGB,width=1920,height=1080,framerate=60/1 "
			"! videoconvert ! x264enc bitrate=2000 speed-preset=medium tune=zerolatency "
			"! rtph264pay config-interval=1 name=pay0 pt=96"
		)
		self.timestamp = 0

	def set_frame(self, frame):
		self.frame = frame

	def on_need_data(self, src, length):
		if self.frame is not None:
			data = self.frame.tobytes()
			buf = Gst.Buffer.new_allocate(None, len(data), None)
			buf.fill(0, data)
			buf.duration = Gst.SECOND // 60
			timestamp = getattr(self, "timestamp", 0)
			buf.pts = buf.dts = timestamp
			buf.offset = timestamp
			self.timestamp = timestamp + buf.duration
			retval = src.emit("push-buffer", buf)
			if retval != Gst.FlowReturn.OK:
				print("Push buffer error:", retval)
		else:
			print("Frame is None")

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
		self.loop = GLib.MainLoop()
		self.loop_future = None
		self.executor = ThreadPoolExecutor(max_workers=1)

		self.port = port
		self.path = path

	def start(self):
		# self.loop_thread = threading.Thread(target=self.loop.run)
		# self.loop_thread.start()
		print(f"RTSP server is running at rtsp://0.0.0.0:{self.port}{self.path}")
		loop = asyncio.get_running_loop()
		self.loop_future = loop.run_in_executor(self.executor, self.loop.run)

	def stop(self):
		# if self.loop is not None:
		# 	print("Stopping RTSP server...")
		# 	self.loop.quit()
		# 	self.loop_thread.join()
		if self.loop_future:
			print("Stopping RTSP server...")
			self.loop.quit()
			self.loop_future.cancel()
			self.executor.shutdown(wait=True)
			print("RTSP server stopped.")

	def push_frame(self, frame):
		self.factory.set_frame(frame)
