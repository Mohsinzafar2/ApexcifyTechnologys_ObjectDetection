from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from detector import ObjectDetector
import base64
import cv2
import numpy as np

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize detector
detector = ObjectDetector()

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'message': 'Object Detection API is running'})

@app.route('/detect', methods=['POST'])
def detect_objects():
    try:
        data = request.json
        image_data = data.get('image')
        
        if not image_data:
            return jsonify({'error': 'No image provided'}), 400
        
        # Perform detection
        results = detector.detect_objects(image_data)
        
        return jsonify(results)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@socketio.on('video_frame')
def handle_video_frame(data):
    """Handle real-time video stream"""
    try:
        image_data = data['image']
        results = detector.detect_objects(image_data)
        emit('detection_results', results)
    except Exception as e:
        emit('error', {'message': str(e)})

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('connected', {'message': 'Connected to detection server'})

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    print("Starting Object Detection Server...")
    print("Server running on http://localhost:5000")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)