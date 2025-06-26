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

