import React, { useEffect, useRef, useState } from "react";
import api from "../../services/api";
import { useAuth } from "../../context/AuthContext";

export default function UniversalAttendance() {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const { user } = useAuth();

  const [statusMessage, setStatusMessage] = useState("");
  const [processing, setProcessing] = useState(false);
  const [cameraActive, setCameraActive] = useState(false);

  const startCamera = async () => {
    try {
      setCameraActive(true);

      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: 640, height: 480 }
      });

      videoRef.current.srcObject = stream;
      videoRef.current.play();

      recognizeLoop();
    } catch (error) {
      console.error("Camera Error:", error);
      setStatusMessage("Unable to access camera.");
    }
  };

  const stopCamera = () => {
    setCameraActive(false);

    const stream = videoRef.current?.srcObject;
    if (stream) stream.getTracks().forEach((track) => track.stop());
  };

  const captureFrame = () => {
    const canvas = canvasRef.current;
    const video = videoRef.current;

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    const ctx = canvas.getContext("2d");
    ctx.drawImage(video, 0, 0);

    return canvas.toDataURL("image/jpeg");
  };

  const recognizeLoop = async () => {
    if (!cameraActive) return;

    if (!processing) {
      await recognizeFace();
    }

    setTimeout(recognizeLoop, 500);
  };

  const recognizeFace = async () => {
    if (processing) return;
    setProcessing(true);

    const frame = captureFrame();

    try {
      const res = await api.post("/recognition/recognize", { image_base64: frame });
      const data = res.data;

      if (data.match) {
        drawBoundingBox("green");
        setStatusMessage(`Recognized: ${data.name}. Marking attendance...`);
        
        await markAttendance(data.role, data.id);
        
        // Pause for 2 seconds after successful recognition
        setTimeout(() => {
          setProcessing(false);
          setStatusMessage("Ready for next recognition.");
        }, 2000);

      } else {
        drawBoundingBox("red");
        setStatusMessage("Unknown Face");
        setProcessing(false);
      }
    } catch (err) {
      console.error("Recognition error:", err);
      drawBoundingBox("red");
      setStatusMessage("Error during recognition.");
      setProcessing(false);
    }
  };

  const markAttendance = async (role, personId) => {
    const endpoint =
      role === "student"
        ? "/student-attendance/mark"
        : "/teacher-attendance/mark";
    const payload =
      role === "student"
        ? { student_id: personId }
        : { teacher_id: personId };

    try {
      await api.post(endpoint, payload);
      setStatusMessage(`Attendance marked for ${role} ID: ${personId}`);
      window.dispatchEvent(new CustomEvent("entityChanged"));
    } catch (err) {
      console.error("Attendance error:", err);
      setStatusMessage("Error marking attendance.");
    }
  };

  const drawBoundingBox = (color) => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    ctx.lineWidth = 4;
    ctx.strokeStyle = color;
    ctx.strokeRect(20, 20, canvas.width - 40, canvas.height - 40);
  };

  useEffect(() => {
    return () => stopCamera();
  }, []);

  return (
    <div className="p-4 max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">Face Recognition Attendance</h1>

      <div className="relative w-full flex justify-center border rounded-lg overflow-hidden">
        <video ref={videoRef} className="w-full max-w-2xl" autoPlay muted />
        <canvas ref={canvasRef} className="absolute top-0 left-0 w-full h-full" />
      </div>

      <p className="text-center text-lg font-semibold mt-4">
        {statusMessage}
      </p>

      <div className="flex justify-center gap-4 mt-6">
        {!cameraActive ? (
          <button
            className="bg-green-600 text-white px-6 py-3 rounded"
            onClick={startCamera}
          >
            Start Attendance
          </button>
        ) : (
          <button
            className="bg-red-600 text-white px-6 py-3 rounded"
            onClick={stopCamera}
          >
            Stop Camera
          </button>
        )}
      </div>
    </div>
  );
}
