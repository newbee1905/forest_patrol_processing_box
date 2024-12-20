# Forest Processing Box

A Python-based application to process forest-related video streams, detect objects using YOLO, and serve the stream via RTSP.

## Features

- Detects forest fires and other objects of interest using YOLO models.
- Streams processed video via RTSP.

## Dependencies 

- Python: >=3.12
- GStreamer

```bash
sudo apt install gstreamer1.0-plugins-base gstreamer1.0-plugins-good gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly gstreamer1.0-libav
```

## Setting Up

### Installation

1. Clone the Repository

```bash
git clone https://github.com/your-username/forest-processing-box.git
cd forest-processing-box
```

2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate
```

```bash
pip install -r requirements.txt
```

Install optimised pytorch for Nvidia Jetson (Optional)

```bash
pip install torch torchvision torchaudio --index-url https://developer.download.nvidia.com/compute/redist/jp/v50
```

### Configuration

```
RTSP_URL=rtsp://your_rtsp_source
RETRY_INTERVAL=5
MAX_RETRY_INTERVAL=100

RTSP_OUTPUT_PORT=8554
RTSP_OUTPUT_PATH=/live

YOLO_MODEL_PATH=forest_fire_best.pt
CONFIDENCE_THRESHOLD=0.4

WEBRTC_SERVER_URL=ws://127.0.0.1:8000
MIN_OBJECTS_FOR_ALERT=1
```

## Running the Program

```bash
python main.py
```


## Setup systemd service

### Create the service

Create a `systemd` service file at `/etc/systemd/system/forest-processing.service`:

```service
[Unit]
Description=Forest Processing Box Service
After=network.target

[Service]
WorkingDirectory=/home/username/forest-processing-box
ExecStart=python /home/username/forest-processing-box/main.py
Environment="PATH=/home/username/forest-processing-box/.venv/bin:$PATH"

Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```


### Reload and Enable the Service

```bash
sudo systemctl daemon-reload
sudo systemctl enable forest-processing.service
sudo systemctl start forest-processing.service
# Or
sudo systemctl enable --now forest-processing.service
```
