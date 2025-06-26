import os
import cv2
import numpy as np
from ultralytics import YOLO
from PIL import Image, ImageDraw, ImageFont
import uuid
from datetime import datetime

class BearDetectionService:
    def __init__(self, model_path=None):
        """
        初始化台灣黑熊檢測服務
        
        Args:
            model_path (str): YOLO模型檔案路徑，如果為None則使用預設模型
        """
        self.model_path = model_path
        self.model = None
        self.confidence_threshold = 0.5
        self.load_model()
    
    def load_model(self):
        """載入YOLO模型"""
        try:
            if self.model_path and os.path.exists(self.model_path):
                # 載入用戶提供的訓練好的模型
                self.model = YOLO(self.model_path)
                print(f"成功載入自定義模型: {self.model_path}")
            else:
                # 使用預設的YOLOv8模型作為備用
                self.model = YOLO('yolov8n.pt')
                print("載入預設YOLOv8模型")
        except Exception as e:
            print(f"模型載入失敗: {str(e)}")
            # 如果模型載入失敗，使用預設模型
            self.model = YOLO('yolov8n.pt')
    
    def detect_bear(self, image_path, output_dir=None):
        """
        檢測圖片中的台灣黑熊
        
        Args:
            image_path (str): 輸入圖片路徑
            output_dir (str): 輸出目錄，如果為None則使用輸入圖片的目錄
            
        Returns:
            dict: 檢測結果
        """
        try:
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"圖片檔案不存在: {image_path}")
            
            # 執行檢測
            results = self.model(image_path, conf=self.confidence_threshold)
            
            # 分析檢測結果
            bear_detected = False
            max_confidence = 0.0
            detections = []
            
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        # 獲取類別名稱和信心度
                        class_id = int(box.cls[0])
                        confidence = float(box.conf[0])
                        class_name = self.model.names[class_id]
                        
                        # 檢查是否為熊類（根據模型的類別名稱調整）
                        if self._is_bear_class(class_name):
                            bear_detected = True
                            max_confidence = max(max_confidence, confidence)
                            
                            # 獲取邊界框座標
                            x1, y1, x2, y2 = box.xyxy[0].tolist()
                            detections.append({
                                'class_name': class_name,
                                'confidence': confidence,
                                'bbox': [x1, y1, x2, y2]
                            })
            
            # 生成結果圖片
            result_image_path = None
            if bear_detected and output_dir:
                result_image_path = self._draw_detections(
                    image_path, detections, output_dir
                )
            
            return {
                'bear_detected': bear_detected,
                'confidence': max_confidence,
                'detections': detections,
                'result_image_path': result_image_path
            }
            
        except Exception as e:
            print(f"檢測過程發生錯誤: {str(e)}")
            return {
                'bear_detected': False,
                'confidence': 0.0,
                'detections': [],
                'result_image_path': None,
                'error': str(e)
            }
    
    def _is_bear_class(self, class_name):
        """
        判斷類別名稱是否為熊類
        
        Args:
            class_name (str): 類別名稱
            
        Returns:
            bool: 是否為熊類
        """
        bear_keywords = ['bear', '熊', 'black bear', '黑熊', 'taiwan black bear', '台灣黑熊', 'kumay']
        class_name_lower = class_name.lower()
        return any(keyword in class_name_lower for keyword in bear_keywords)
    
    def _draw_detections(self, image_path, detections, output_dir):
        """
        在圖片上繪製檢測結果
        
        Args:
            image_path (str): 原始圖片路徑
            detections (list): 檢測結果列表
            output_dir (str): 輸出目錄
            
        Returns:
            str: 結果圖片路徑
        """
        try:
            # 讀取原始圖片
            image = cv2.imread(image_path)
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(image_rgb)
            draw = ImageDraw.Draw(pil_image)
            
            # 設定字體（如果系統沒有字體檔案，使用預設字體）
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
            except:
                font = ImageFont.load_default()
            
            # 繪製檢測框和標籤
            for detection in detections:
                x1, y1, x2, y2 = detection['bbox']
                confidence = detection['confidence']
                class_name = detection['class_name']
                
                # 繪製邊界框
                draw.rectangle([x1, y1, x2, y2], outline="red", width=3)
                
                # 繪製標籤
                label = f"{class_name}: {confidence:.2f}"
                bbox = draw.textbbox((x1, y1-25), label, font=font)
                draw.rectangle(bbox, fill="red")
                draw.text((x1, y1-25), label, fill="white", font=font)
            
            # 保存結果圖片
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            result_filename = f"detection_result_{timestamp}_{uuid.uuid4().hex[:8]}.jpg"
            result_path = os.path.join(output_dir, result_filename)
            
            # 轉換回BGR格式並保存
            result_image_bgr = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
            cv2.imwrite(result_path, result_image_bgr)
            
            return result_filename
            
        except Exception as e:
            print(f"繪製檢測結果時發生錯誤: {str(e)}")
            return None
    
    def set_confidence_threshold(self, threshold):
        """
        設定信心度閾值
        
        Args:
            threshold (float): 信心度閾值 (0.0 - 1.0)
        """
        if 0.0 <= threshold <= 1.0:
            self.confidence_threshold = threshold
        else:
            raise ValueError("信心度閾值必須在0.0到1.0之間")
    
    def get_model_info(self):
        """
        獲取模型資訊
        
        Returns:
            dict: 模型資訊
        """
        if self.model:
            return {
                'model_path': self.model_path,
                'model_type': str(type(self.model)),
                'confidence_threshold': self.confidence_threshold,
                'class_names': list(self.model.names.values()) if hasattr(self.model, 'names') else []
            }
        return None

