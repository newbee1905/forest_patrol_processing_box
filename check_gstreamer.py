import cv2
import subprocess
import sys
import platform

def check_gstreamer_installation():
	"""Comprehensive check of GStreamer installation and configuration."""
	print("System Information:")
	print(f"OS: {platform.system()} {platform.release()}")
	print(f"Python Version: {sys.version}")
	print(f"OpenCV Version: {cv2.__version__}")

	# Check GStreamer version
	try:
		gst_version = subprocess.check_output(["gst-launch-1.0", "--version"], 
											  universal_newlines=True)
		print("\nGStreamer Version:")
		print(gst_version.strip())
	except (subprocess.CalledProcessError, FileNotFoundError):
		print("\n❌ GStreamer tools not found. Please install GStreamer.")

	# List available GStreamer plugins
	try:
		plugins = subprocess.check_output(["gst-inspect-1.0"], 
										  universal_newlines=True)
		print("\nGStreamer Plugins:")
		# Count and display plugin count
		plugin_count = len([line for line in plugins.split('\n') if 'Plugin' in line])
		print(f"Total Plugins Detected: {plugin_count}")
	except (subprocess.CalledProcessError, FileNotFoundError):
		print("\n❌ Cannot list GStreamer plugins.")

def test_gstreamer_pipelines():
	"""Test various GStreamer video capture pipelines."""
	print("\nTesting GStreamer Pipelines:")
	
	# Test pipelines
	test_pipelines = [
		# Basic test source
		"videotestsrc ! videoconvert ! appsink",
		
		# More complex test pipeline
		"videotestsrc pattern=ball ! videoconvert ! videoscale ! appsink",
		
		# Null pipeline (minimal test)
		"videotestsrc ! fakesink"
	]

	for pipeline in test_pipelines:
		print(f"\nTesting pipeline: {pipeline}")
		try:
			cap = cv2.VideoCapture(pipeline, cv2.CAP_GSTREAMER)
			
			if cap.isOpened():
				print("✓ Pipeline opened successfully")
				
				# Try to read a frame
				ret, frame = cap.read()
				if ret:
					print("✓ Successfully read a frame")
					print(f"Frame shape: {frame.shape}")
				else:
					print("⚠ Opened pipeline, but cannot read frame")
				
				cap.release()
			else:
				print("❌ Failed to open pipeline")
		
		except Exception as e:
			print(f"❌ Exception occurred: {e}")

def check_opencv_gstreamer_build():
	"""Detailed check of OpenCV's GStreamer build configuration."""
	print("\nOpenCV GStreamer Build Configuration:")
	build_info = cv2.getBuildInformation()
	
	# Check for specific GStreamer-related build flags
	gstreamer_flags = [
		"GSTREAMER",
		"gstreamer",
		"WITH_GSTREAMER",
		"GStreamer"
	]
	
	found_flags = [flag for flag in gstreamer_flags if flag in build_info]
	
	if found_flags:
		print("✓ GStreamer-related build flags found:")
		for flag in found_flags:
			print(f"  - {flag}")
	else:
		print("❌ No GStreamer-related build flags detected")

def main():
	print("===== GStreamer Diagnostic Tool =====")
	check_gstreamer_installation()
	check_opencv_gstreamer_build()
	test_gstreamer_pipelines()
	print("\n===== Diagnostic Complete =====")

if __name__ == "__main__":
	main()
