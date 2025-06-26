import os
import cv2
import numpy as np
from PIL import Image
import requests
import base64
import json
import mimetypes # 新增這一行

class BearDetectionService:
    def __init__(self):
        # 從環境變數中獲取 Hugging Face API 資訊
        self.hf_api_url = os.getenv("HF_API_URL", "")
        self.hf_api_token = os.getenv("HF_API_TOKEN", "")
        self.confidence_threshold = float(os.getenv("CONFIDENCE_THRESHOLD", 0.5))

        if not self.hf_api_url or not self.hf_api_token:
            print("警告：Hugging Face API URL 或 Token 未設定。請設定 HF_API_URL 和 HF_API_TOKEN 環境變數。")
            # 如果沒有設定，可以提供一個預設的錯誤訊息或行為
            # 或者在 detect_bear 方法中處理錯誤

        # 確保上傳目錄存在
        self.upload_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "static", "uploads")
        os.makedirs(self.upload_folder, exist_ok=True)

    def set_confidence_threshold(self, threshold):
        self.confidence_threshold = threshold

    def get_model_info(self):
        # 由於模型在 Hugging Face 上，這裡返回模擬的模型資訊
        # 實際的類別名稱應根據您的 Hugging Face 模型返回的結果來調整
        return {
            "model_type": "Hugging Face Inference API",
            "model_path": self.hf_api_url,
            "confidence_threshold": self.confidence_threshold,
            "class_names": ["kumay", "bear", "black bear", "taiwan black bear"] # 這裡列出您的模型可能檢測到的類別
        }

    def detect_bear(self, image_path):
        try:
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"圖片檔案不存在: {image_path}")

            # 讀取圖片的原始位元組數據
            with open(image_path, "rb") as f:
                image_bytes = f.read()

            # 根據檔案擴展名猜測 Content-Type
            content_type, _ = mimetypes.guess_type(image_path)
            if content_type is None:
                # 如果無法猜測，預設為通用的二進位流
                content_type = "application/octet-stream"

            headers = {
                "Authorization": f"Bearer {self.hf_api_token}",
                "Content-Type": content_type # 明確設定 Content-Type
            }

            # 發送請求到 Hugging Face Inference API
            response = requests.post(self.hf_api_url, headers=headers, data=image_bytes)
            response.raise_for_status() # 如果請求失敗，會拋出異常

            hf_results = response.json()
            
            # ... (以下程式碼保持不變)
    
            
            # 解析 Hugging Face 返回的結果
            # Hugging Face 的物件檢測 API 返回格式通常是 [{box: {xmin, ymin, xmax, ymax}, score, label}, ...]
            detections = []
            bear_detected = False
            for res in hf_results:
                score = res.get("score", 0.0)
                label = res.get("label", "unknown")
                box = res.get("box", {})

                if score >= self.confidence_threshold and self._is_bear_class(label):
                    detections.append({
                        "box": [box.get("xmin"), box.get("ymin"), box.get("xmax"), box.get("ymax")],
                        "score": score,
                        "label": label
                    })
                    bear_detected = True

            # 繪製檢測結果並保存圖片
            result_image_path = None
            if detections:
                result_image_path = self._draw_detections(image_path, detections, self.upload_folder)

            return {
                "success": True,
                "bear_detected": bear_detected,
                "detections": detections,
                "result_image_path": os.path.basename(result_image_path) if result_image_path else None
            }

        except FileNotFoundError as e:
            return {"success": False, "error": str(e)}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": f"Hugging Face API 請求失敗: {e}"}
        except json.JSONDecodeError:
            return {"success": False, "error": "Hugging Face API 返回無效的 JSON"}
        except Exception as e:
            return {"success": False, "error": f"檢測過程中發生錯誤: {e}"}

    def _is_bear_class(self, class_name):
        """
        判斷類別名稱是否為熊類
        
        Args:
            class_name (str): 類別名稱
            
        Returns:
            bool: 是否為熊類
        """
        # 這裡需要根據您的 Hugging Face 模型實際輸出的類別名稱來調整
        # 例如，如果您的模型只輸出 'kumay'，那麼就只判斷 'kumay'
        bear_keywords = ["kumay", "bear", "black bear", "taiwan black bear"]
        class_name_lower = class_name.lower()
        return any(keyword in class_name_lower for keyword in bear_keywords)

    def _draw_detections(self, image_path, detections, output_dir):
        # 確保輸出目錄存在
        os.makedirs(output_dir, exist_ok=True)

        # 讀取圖片
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"無法讀取圖片: {image_path}")

        # 複製圖片以繪製
        img_display = img.copy()

        # 繪製檢測框和標籤
        for det in detections:
            box = det["box"]
            score = det["score"]
            label = det["label"]

            xmin, ymin, xmax, ymax = map(int, box)

            # 繪製矩形框
            color = (0, 255, 0)  # 綠色
            thickness = 2
            cv2.rectangle(img_display, (xmin, ymin), (xmax, ymax), color, thickness)

            # 繪製標籤和分數
            text = f"{label}: {score:.2f}"
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.7
            font_thickness = 2
            text_size = cv2.getTextSize(text, font, font_scale, font_thickness)[0]
            
            # 確保文字背景框不會超出圖片邊界
            text_bg_xmin = xmin
            text_bg_ymin = ymin - text_size[1] - 5
            text_bg_xmax = xmin + text_size[0]
            text_bg_ymax = ymin - 5

            if text_bg_ymin < 0: # 如果文字背景框超出圖片上方，則畫在框下方
                text_bg_ymin = ymax + 5
                text_bg_ymax = ymax + 5 + text_size[1]
                text_bg_xmin = xmin
                text_bg_xmax = xmin + text_size[0]

            cv2.rectangle(img_display, (text_bg_xmin, text_bg_ymin), (text_bg_xmax, text_bg_ymax), color, -1) # -1 表示填充
            cv2.putText(img_display, text, (text_bg_xmin, text_bg_ymax - 2), font, font_scale, (0, 0, 0), font_thickness, cv2.LINE_AA)

        # 生成新的檔案名
        base_name = os.path.basename(image_path)
        name, ext = os.path.splitext(base_name)
        output_filename = f"{name}_detected{ext}"
        output_path = os.path.join(output_dir, output_filename)

        # 保存結果圖片
        cv2.imwrite(output_path, img_display)
        return output_path

