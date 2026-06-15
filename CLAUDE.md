# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the app

The backend must be launched from `app/backend/` because all module imports are relative to that directory:

```bash
cd app/backend
python main.py
```

Or with auto-reload:

```bash
cd app/backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Access at `http://localhost:8000`. Swagger docs at `http://localhost:8000/docs`.

## Environment / configuration

Settings live in `app/backend/config.py` as a `pydantic-settings` `BaseSettings` class. All values can be overridden with a `.env` file at the project root (see `.env.example`). Key settings:

- `DEVICE` — defaults to `"cuda"` if `CUDA_VISIBLE_DEVICES` is set, otherwise `"cpu"`
- `YOLO_MODEL_PATH` — model size variant (`yolov8n.pt`, `yolov8s.pt`, … `yolov8x.pt`)
- `RCNN_CONFIDENCE_THRESHOLD` / `YOLO_CONFIDENCE_THRESHOLD` — detection cutoff (default `0.5`)

The `yolov8n.pt` weights file is already committed at `app/backend/yolov8n.pt`. Faster R-CNN weights are downloaded automatically from torchvision on first run.

## Architecture

```
app/
├── backend/          # FastAPI application (all Python imports relative to here)
│   ├── main.py       # Routes + startup model loading; detectors are module-level globals
│   ├── config.py     # Pydantic settings singleton: `from config import settings`
│   ├── detection/
│   │   ├── rcnn_detector.py   # RCNNDetector wrapping fasterrcnn_resnet50_fpn (torchvision)
│   │   └── yolo_detector.py   # YOLODetector wrapping Ultralytics YOLO
│   ├── database/
│   │   ├── models.py          # SQLAlchemy ORM: DetectionResult, ComparisonResult, SystemMetrics
│   │   └── db.py              # Engine/session factory; DB file: app/backend/database/detection.db
│   ├── metrics/
│   │   └── calculator.py      # MetricsCalculator: system metrics + side-by-side comparison math
│   └── utils/
│       └── file_handler.py    # FileHandler (save/validate uploads), ImageProcessor (save results)
└── frontend/
    ├── templates/index.html   # Single-page app; all UI in one file
    └── static/
        ├── css/styles.css
        └── js/main.js         # All frontend logic; calls REST API endpoints
uploads/               # Created at runtime by config.py
├── images/            # Uploaded source images
├── videos/            # Uploaded source videos
└── results/           # Annotated output images/videos
```

### Request flow

1. Browser uploads a file to `POST /api/v1/detect/image/{rcnn|yolo}`.
2. `main.py` saves the file via `FileHandler`, runs the appropriate detector, saves the annotated result, persists a `DetectionResult` row in SQLite, and returns JSON including a `/api/v1/results/image/{id}` URL.
3. To compare, the frontend calls `POST /api/v1/compare?rcnn_result_id=X&yolo_result_id=Y` which reads both rows and calls `MetricsCalculator.compare_detections`.

### Detector interface

Both `RCNNDetector` and `YOLODetector` expose the same two public methods:

- `detect_image(image_path) → (annotated_np_array, list[dict], inference_time_s)`
- `detect_video(video_path, callback=None) → (output_path, list[frame_dict], total_time_s, avg_fps)`

Detection dicts share a common shape: `{class_name, class_id, confidence, bbox: {x1,y1,x2,y2,width,height}}`.

### Database

SQLite file at `app/backend/database/detection.db` (auto-created on startup). Schema is managed via `Base.metadata.create_all` — no migration tool. To reset, delete the `.db` file and restart.
