import os
import uuid
from datetime import datetime
from flask import Blueprint, jsonify, request, current_app, send_from_directory
from werkzeug.utils import secure_filename
from src.models.detection import Detection, db
from src.services.bear_detection import BearDetectionService
import cv2
import numpy as np

detection_bp = Blueprint('detection', __name__)

# 允許的檔案類型
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'webp'}

# 初始化檢測服務
bear_detector = None

def get_bear_detector():
    """獲取檢測服務實例"""
    global bear_detector
    if bear_detector is None:
        # 尋找best.pt模型檔案
        model_path = None
        possible_paths = [
            '/home/ubuntu/bear-detection-backend/models/best.pt',
            '/home/ubuntu/bear-detection-backend/best.pt',
            '/home/ubuntu/best.pt'
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                model_path = path
                break
        
        bear_detector = BearDetectionService(model_path)
    return bear_detector

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def ensure_upload_folder():
    """確保上傳資料夾存在"""
    upload_folder = os.path.join(current_app.static_folder, 'uploads')
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    return upload_folder

@detection_bp.route('/statistics', methods=['GET'])
def get_statistics():
    """獲取系統統計資料"""
    try:
        total_detections = Detection.query.count()
        bear_detections = Detection.query.filter_by(bear_detected=True).count()
        recent_detections = Detection.query.order_by(Detection.detected_at.desc()).limit(10).all()
        
        # 計算檢測率
        detection_rate = (bear_detections / total_detections * 100) if total_detections > 0 else 0
        
        statistics = {
            'total_detections': total_detections,
            'bear_detections': bear_detections,
            'detection_rate': round(detection_rate, 2),
            'recent_count': len(recent_detections)
        }
        
        return jsonify({
            'success': True,
            'statistics': statistics
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@detection_bp.route('/detect', methods=['POST'])
def detect_bear():
    """處理圖片上傳和台灣黑熊檢測"""
    try:
        # 檢查是否有檔案上傳
        if 'image' not in request.files:
            return jsonify({
                'success': False,
                'error': '沒有上傳圖片檔案'
            }), 400
        
        file = request.files['image']
        camera_id = request.form.get('camera_id', 'unknown')
        location = request.form.get('location', '未知位置')
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': '沒有選擇檔案'
            }), 400
        
        if file and allowed_file(file.filename):
            # 確保上傳資料夾存在
            upload_folder = ensure_upload_folder()
            
            # 生成唯一檔名
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4()}_{filename}"
            filepath = os.path.join(upload_folder, unique_filename)
            
            # 保存原始圖片
            file.save(filepath)
            
            # 使用YOLO模型進行檢測
            detector = get_bear_detector()
            detection_result = detector.detect_bear(filepath, upload_folder)
            
            bear_detected = detection_result.get('bear_detected', False)
            confidence = detection_result.get('confidence', 0.0)
            result_image_filename = detection_result.get('result_image_path')
            
            # 創建檢測記錄
            detection = Detection(
                camera_id=camera_id,
                location=location,
                bear_detected=bear_detected,
                confidence=confidence,
                detected_at=datetime.utcnow(),
                image_filename=unique_filename,
                result_image_filename=result_image_filename
            )
            
            db.session.add(detection)
            db.session.commit()
            
            response_data = {
                'bear_detected': bear_detected,
                'confidence': confidence,
                'detected_at': detection.detected_at.isoformat(),
                'location': location,
                'image_url': f'/api/uploads/{unique_filename}',
                'detection_id': detection.id
            }
            
            # 如果有檢測結果圖片，添加到回應中
            if result_image_filename:
                response_data['result_image_url'] = f'/api/uploads/{result_image_filename}'
            
            # 如果檢測過程有錯誤，添加錯誤信息
            if 'error' in detection_result:
                response_data['warning'] = detection_result['error']
            
            return jsonify(response_data)
        
        return jsonify({
            'success': False,
            'error': '不支援的檔案格式'
        }), 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'檢測過程發生錯誤: {str(e)}'
        }), 500

@detection_bp.route('/recent-detections', methods=['GET'])
def get_recent_detections():
    """獲取最近的檢測記錄"""
    try:
        limit = request.args.get('limit', 10, type=int)
        detections = Detection.query.order_by(Detection.detected_at.desc()).limit(limit).all()
        
        result = []
        for detection in detections:
            detection_data = detection.to_dict()
            # 添加圖片URL
            if detection.image_filename:
                detection_data['image_url'] = f'/api/uploads/{detection.image_filename}'
            if detection.result_image_filename:
                detection_data['result_image_url'] = f'/api/uploads/{detection.result_image_filename}'
            result.append(detection_data)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@detection_bp.route('/uploads/<filename>')
def uploaded_file(filename):
    """提供上傳檔案的存取"""
    upload_folder = os.path.join(current_app.static_folder, 'uploads')
    return send_from_directory(upload_folder, filename)

@detection_bp.route('/health', methods=['GET'])
def health_check():
    """健康檢查端點"""
    return jsonify({
        'status': 'healthy',
        'service': 'bear-detection-backend',
        'timestamp': datetime.utcnow().isoformat()
    })


@detection_bp.route('/model-info', methods=['GET'])
def get_model_info():
    """獲取模型資訊"""
    try:
        detector = get_bear_detector()
        model_info = detector.get_model_info()
        
        return jsonify({
            'success': True,
            'model_info': model_info
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@detection_bp.route('/set-confidence', methods=['POST'])
def set_confidence_threshold():
    """設定信心度閾值"""
    try:
        data = request.get_json()
        threshold = data.get('threshold')
        
        if threshold is None:
            return jsonify({
                'success': False,
                'error': '請提供信心度閾值'
            }), 400
        
        detector = get_bear_detector()
        detector.set_confidence_threshold(threshold)
        
        return jsonify({
            'success': True,
            'message': f'信心度閾值已設定為 {threshold}'
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

