import React, { useState, useEffect, useRef } from 'react';
import { io } from 'socket.io-client';
import Camera from './components/Camera';
import DetectionResults from './components/DetectionResults';
import Controls from './components/Controls';

function App() {
  const [detections, setDetections] = useState([]);
  const [totalObjects, setTotalObjects] = useState(0);
  const [isStreaming, setIsStreaming] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [currentImage, setCurrentImage] = useState(null);
  const socketRef = useRef(null);

  useEffect(() => {
    socketRef.current = io('http://localhost:5000');
    
    socketRef.current.on('connect', () => {
      console.log('Connected to server');
      setIsConnected(true);
    });
    
    socketRef.current.on('detection_results', (data) => {
      setDetections(data.detections);
      setTotalObjects(data.total_objects);
      setCurrentImage(data.annotated_image);
    });
    
    socketRef.current.on('error', (error) => {
      console.error('Server error:', error);
      alert('Error: ' + error.message);
    });
    
    return () => {
      if (socketRef.current) {
        socketRef.current.disconnect();
      }
    };
  }, []);

  const handleVideoFrame = (imageData) => {
    if (isStreaming && socketRef.current && isConnected) {
      socketRef.current.emit('video_frame', { image: imageData });
    }
  };

  const toggleStreaming = () => {
    setIsStreaming(!isStreaming);
    if (!isStreaming) {
      setDetections([]);
      setTotalObjects(0);
    }
  };

  const clearResults = () => {
    setDetections([]);
    setTotalObjects(0);
    setCurrentImage(null);
  };

  return (
    <div className="min-h-screen bg-gray-900">
      <header className="bg-gradient-to-r from-blue-600 to-purple-600 shadow-lg">
        <div className="container mx-auto px-4 py-6">
          <h1 className="text-3xl font-bold text-white">
            🤖 AI Object Detection System
          </h1>
          <p className="text-blue-100 mt-2">
            Real-time object detection using YOLOv8 | Apexcify Technologies
          </p>
          {isConnected && (
            <span className="inline-flex items-center mt-2 px-2 py-1 bg-green-500 rounded-full text-xs">
              <span className="w-2 h-2 bg-white rounded-full mr-1 animate-pulse"></span>
              Connected to Server
            </span>
          )}
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-4">
            <div className="bg-gray-800 rounded-lg p-4">
              <h2 className="text-xl font-bold text-white mb-3">Live Camera Feed</h2>
              <Camera onFrame={handleVideoFrame} isStreaming={isStreaming} />
            </div>
            
            {currentImage && (
              <div className="bg-gray-800 rounded-lg p-4">
                <h3 className="text-lg font-semibold text-white mb-2">Detection Preview</h3>
                <img 
                  src={`data:image/jpeg;base64,${currentImage}`}
                  alt="Detection preview"
                  className="rounded-lg w-full"
                />
              </div>
            )}
          </div>

          <div className="space-y-6">
            <Controls 
              isStreaming={isStreaming}
              onToggleStream={toggleStreaming}
              onClear={clearResults}
            />
            <DetectionResults detections={detections} totalObjects={totalObjects} />
          </div>
        </div>
      </main>

      <footer className="bg-gray-800 mt-12 py-6">
        <div className="container mx-auto px-4 text-center">
          <p className="text-gray-400">
            Built with YOLOv8, React, and Flask | Apexcify Technologies Internship Project
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;