import cv2
import numpy as np
from ultralytics import YOLO
import base64
from PIL import Image
import io

class ObjectDetector:
    def __init__(self):
        # Load YOLO model
        self.model = YOLO('yolov8n.pt', task='detect')
        self.classes = self.model.names
        self.colors = self._generate_colors(80)
        
    def _generate_colors(self, num_classes):
        """Generate unique colors for each class"""
        np.random.seed(42)
        return [tuple(np.random.randint(0, 255, 3).tolist()) for _ in range(num_classes)]
    
    def detect_objects(self, image_data):
        """Detect objects in image"""
        # Convert base64 to image
        img = self._base64_to_image(image_data)
        
        # Run detection
        results = self.model(img, stream=False)
        
        # Process results
        detections = []
        for result in results:
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    confidence = float(box.conf[0])
                    class_id = int(box.cls[0])
                    class_name = self.classes[class_id]
                    
                    detections.append({
                        'bbox': [int(x1), int(y1), int(x2), int(y2)],
                        'confidence': round(confidence, 2),
                        'class': class_name,
                        'class_id': class_id,
                        'color': self.colors[class_id % len(self.colors)]
                    })
        
        # Annotate image
        annotated_img = self._annotate_image(img, detections)
        annotated_base64 = self._image_to_base64(annotated_img)
        
        return {
            'detections': detections,
            'annotated_image': annotated_base64,
            'total_objects': len(detections)
        }
    
    def _base64_to_image(self, base64_string):
        """Convert base64 to OpenCV image"""
        # Remove data URL prefix if present
        if 'base64,' in base64_string:
            base64_string = base64_string.split('base64,')[1]
        
        # Decode base64
        image_bytes = base64.b64decode(base64_string)
        image = Image.open(io.BytesIO(image_bytes))
        return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    
    def _image_to_base64(self, image):
        """Convert OpenCV image to base64"""
        _, buffer = cv2.imencode('.jpg', image)
        return base64.b64encode(buffer).decode('utf-8')
    
    def _annotate_image(self, image, detections):
        """Draw bounding boxes on image"""
        img_copy = image.copy()
        
        for det in detections:
            x1, y1, x2, y2 = det['bbox']
            color = det['color']
            
            # Draw rectangle
            cv2.rectangle(img_copy, (x1, y1), (x2, y2), color, 2)
            
            # Draw label
            label = f"{det['class']} ({det['confidence']})"
            label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
            
            cv2.rectangle(img_copy, (x1, y1 - label_size[1] - 10), 
                         (x1 + label_size[0], y1), color, -1)
            cv2.putText(img_copy, label, (x1, y1 - 5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        
        return img_copy