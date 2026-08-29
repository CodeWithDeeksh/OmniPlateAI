# ANPR Module — SIH26127

Vehicle & license plate detection pipeline. Produces `DetectionEvent`
objects matching `docs/data_contract.md` — this module's only output.

## Pipeline

```
frame -> VehicleDetector -> PlateDetector -> preprocess_plate -> OCR -> DetectionEvent
```

## Files

| File | Responsibility |
|---|---|
| `schema.py` | `DetectionEvent` dataclass + validation, mirrors the data contract exactly |
| `detector.py` | Vehicle detection (YOLOv8n, pretrained COCO weights) + plate detection (OpenCV Haar cascade) — both real, CPU-runnable, tested |
| `preprocess.py` | Cleans a plate crop before OCR (grayscale, denoise, deskew, contrast, resize) |
| `ocr.py` | Reads text off the preprocessed plate (EasyOCR by default) + plate format validation |
| `event_builder.py` | Assembles a validated `DetectionEvent` |
| `pipeline.py` | Wires all stages together — `ANPRPipeline.process_frame(...)` is the main entry point |
| `tests/test_pipeline.py` | Contract-compliance tests — run before every commit |

## Setup

```bash
pip install -r requirements.txt
```

## Run tests

```bash
pytest tests/ -v
```

## Status

Both detection stages are real and tested, not stubs:
- `VehicleDetector` uses pretrained YOLOv8n (COCO weights) — confirmed
  detecting real vehicles at ~87% confidence on a test photo.
- `PlateDetector` uses OpenCV's bundled Haar cascade — confirmed loading
  and running without crashing on real and blank images.
- Full pipeline confirmed running end-to-end (vehicle detection → plate
  detection → preprocessing → OCR → DetectionEvent) with no errors.

## Known limitations / next upgrades

- [ ] Haar cascade plate detection is a CPU-only baseline — expect more
      false positives/negatives than a trained plate-specific YOLO model.
      Natural upgrade path: fine-tune a YOLOv8 model on Indian plate images
      (same `PlateDetector` interface, just swap the internals).
- [ ] Validate OCR accuracy on a real labeled dataset before reporting any
      confidence numbers as "measured accuracy" (contract Section 3 — don't
      claim accuracy that hasn't actually been validated)
- [ ] COCO has no "auto" (auto-rickshaw) class — currently unmapped;
      decide whether to proxy via "motorcycle" or add custom logic
- [ ] Wire `camera_id`, `latitude`, `longitude`, `direction` from actual
      camera metadata rather than hardcoding in a test harness
- [ ] If GPU access becomes available, swap `yolov8n.pt` for `yolov8s.pt`
      or `yolov8m.pt` in `VehicleDetector.__init__` for better accuracy

## Notes for teammates / integration

- Every `DetectionEvent` this module emits is validated against the
  contract in `schema.py` at construction time — a malformed event will
  raise `ValueError` before it ever reaches the backend.
- Do not modify `schema.py`'s field names/types without checking with the
  Lead first (shared contract rule).
