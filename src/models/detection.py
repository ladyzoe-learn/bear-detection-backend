# detection.py 最上方新增
from flask import Blueprint, request, jsonify
from ultralytics import YOLO
import os
import uuid

# 建立 Blueprint
detection_bp = Blueprint("detection", __name__)

# 載入模型（只載一次）
model = YOLO("/bear-detection-backend/models/best.pt")  # 換成你的模型實際路徑

from datetime import datetime
from src.models.user import db

class Detection(db.Model):
    __tablename__ = 'detections'
    
    id = db.Column(db.Integer, primary_key=True)
    camera_id = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    bear_detected = db.Column(db.Boolean, nullable=False, default=False)
    confidence = db.Column(db.Float, nullable=True)
    detected_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    image_filename = db.Column(db.String(200), nullable=True)
    result_image_filename = db.Column(db.String(200), nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'camera_id': self.camera_id,
            'location': self.location,
            'bear_detected': self.bear_detected,
            'confidence': self.confidence,
            'detected_at': self.detected_at.isoformat() if self.detected_at else None,
            'image_filename': self.image_filename,
            'result_image_filename': self.result_image_filename
        }

@detection_bp.route("/predict", methods=["POST"])
def predict():
    if 'image' not in request.files:
        return jsonify({"error": "No image provided"}), 400

    image = request.files["image"]
    if image.filename == '':
        return jsonify({"error": "Empty filename"}), 400

    # 儲存圖片到 temp 資料夾
    filename = f"{uuid.uuid4().hex}.jpg"
    save_path = os.path.join("temp", filename)
    os.makedirs("temp", exist_ok=True)
    image.save(save_path)

    try:
        # 做推論
        results = model(save_path)

        detections = []
        for r in results:
            for box in r.boxes:
                cls_id = int(box.cls[0])
                label = model.names[cls_id]
                confidence = float(box.conf[0])
                xyxy = box.xyxy[0].tolist()

                detections.append({
                    "label": label,
                    "confidence": round(confidence, 2),
                    "bbox": xyxy  # [x1, y1, x2, y2]
                })

        return jsonify({
            "detections": detections,
            "image": filename
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
