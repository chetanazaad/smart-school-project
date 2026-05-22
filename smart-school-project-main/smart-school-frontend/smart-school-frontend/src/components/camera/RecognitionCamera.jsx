import React, { useRef, useState, useEffect } from "react";
import axios from "../../services/api";

export default function RecognitionCamera({ onRecognized, autoRecognize = false, interval = 700, showControls = true }) {
  const videoRef = useRef(null);
  const canvasRef = useRef(null); // hidden capture canvas
  const overlayRef = useRef(null); // visible overlay canvas
  const streamRef = useRef(null); // persistent stream reference
  const [capturedImage, setCapturedImage] = useState(null);
  const [isCameraReady, setIsCameraReady] = useState(false);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const runningRef = useRef(false);

  useEffect(() => {
    const startCamera = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: { width: 640, height: 480 } });
        streamRef.current = stream; // store stream
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
          setIsCameraReady(true);
        }
      } catch (err) {
        console.error("Camera error:", err);
        alert("Camera access blocked");
      }
    };

    startCamera();

    let faceDetector = null;
    if ("FaceDetector" in window) {
      try {
        faceDetector = new window.FaceDetector();
      } catch (e) {
        faceDetector = null;
      }
    }

    const startLoopWhenReady = () => {
      const check = setInterval(() => {
        if (videoRef.current && videoRef.current.readyState >= 2) {
          clearInterval(check);
          if (autoRecognize) {
            runningRef.current = true;
            autoLoop(faceDetector);
          }
        }
      }, 200);
    };

    const autoLoop = async (detector) => {
      while (runningRef.current) {
        const b64 = captureImage();
        if (b64) {
          if (detector) {
            await detectAndRecognize(detector);
          } else {
            await recognizeFace(b64);
            drawCenteredBox();
          }
        }
        await new Promise((r) => setTimeout(r, interval));
      }
    };

    startLoopWhenReady();

    return () => {
      runningRef.current = false;
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((t) => t.stop());
      }
    };
  }, [autoRecognize, interval]);

  const captureImage = () => {
    const canvas = canvasRef.current;
    const video = videoRef.current;
    if (!canvas || !video) return;
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext("2d");
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    const base64 = canvas.toDataURL("image/jpeg");
    setCapturedImage(base64);
    return base64;
  };

  // Fallback simple centered box
  const drawCenteredBox = () => {
    const overlay = overlayRef.current;
    const video = videoRef.current;
    if (!overlay || !video) return;
    overlay.width = video.videoWidth;
    overlay.height = video.videoHeight;
    const ctx = overlay.getContext("2d");
    ctx.clearRect(0, 0, overlay.width, overlay.height);
    ctx.lineWidth = 4;
    ctx.strokeStyle = "#ff1744";
    const w = overlay.width * 0.4;
    const h = overlay.height * 0.4;
    const x = (overlay.width - w) / 2;
    const y = (overlay.height - h) / 2;
    ctx.strokeRect(x, y, w, h);
    ctx.fillStyle = "#ff1744";
    ctx.font = "18px Arial";
    ctx.fillText("Unknown", x + 8, y + 22);
  };

  const detectAndRecognize = async (detector) => {
    const canvas = canvasRef.current;
    const video = videoRef.current;
    const overlay = overlayRef.current;
    if (!canvas || !video || !overlay) return;
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext("2d");
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    try {
      const faces = await detector.detect(canvas);
      const octx = overlay.getContext("2d");
      overlay.width = canvas.width;
      overlay.height = canvas.height;
      octx.clearRect(0, 0, overlay.width, overlay.height);
      if (!faces || faces.length === 0) return;

      // pick largest face
      let best = faces[0];
      for (const f of faces) if (f.boundingBox.width * f.boundingBox.height > best.boundingBox.width * best.boundingBox.height) best = f;

      const bb = best.boundingBox;
      const sx = Math.max(0, Math.floor(bb.x));
      const sy = Math.max(0, Math.floor(bb.y));
      const sw = Math.min(canvas.width - sx, Math.max(1, Math.floor(bb.width)));
      const sh = Math.min(canvas.height - sy, Math.max(1, Math.floor(bb.height)));

      const faceCanvas = document.createElement("canvas");
      faceCanvas.width = sw;
      faceCanvas.height = sh;
      const fctx = faceCanvas.getContext("2d");
      fctx.drawImage(canvas, sx, sy, sw, sh, 0, 0, sw, sh);
      const b64 = faceCanvas.toDataURL("image/jpeg");

      let data = null;
      try {
        const res = await axios.post("/recognition/recognize", { image_base64: b64 });
        data = res.data;
        setResult(data);
      } catch (e) {
        console.error("Recognition call failed:", e);
      }

      for (const f of faces) {
        const box = f.boundingBox;
        octx.lineWidth = 3;
        const isBest = f === best;
        const color = isBest && data && data.match ? "#00c853" : "#ff1744";
        octx.strokeStyle = color;
        octx.strokeRect(box.x, box.y, box.width, box.height);
        octx.fillStyle = color;
        octx.font = "16px Arial";
        const label = isBest && data && data.match ? `${data.name} (${data.role})` : "Unknown";
        octx.fillText(label, box.x + 6, box.y + 18);
      }

      if (data && data.match && onRecognized) {
        onRecognized({ id: data.person_id || data.id, name: data.name, role: data.role, distance: data.distance });
      }
    } catch (err) {
      console.error("Face detector error:", err);
    }
  };

  const recognizeFace = async (imageB64) => {
    const image_to_send = imageB64 || capturedImage;
    if (!image_to_send) return;
    try {
      setLoading(true);
      setResult(null);
      const response = await axios.post("/recognition/recognize", { image_base64: image_to_send });
      const data = response.data;
      setResult(data);
      if (data && data.match && onRecognized) onRecognized({ id: data.person_id || data.id, name: data.name, role: data.role, distance: data.distance });
    } catch (error) {
      console.error("Recognition error:", error);
      setResult({ error: "Recognition failed" });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ textAlign: "center" }}>
      <div style={{ position: "relative", display: "inline-block", width: 480, height: 360 }}>
        <video ref={videoRef} autoPlay playsInline style={{ width: "480px", height: "360px", borderRadius: "8px" }} />
        <canvas ref={overlayRef} style={{ position: "absolute", left: 0, top: 0, pointerEvents: "none", width: '480px', height: '360px' }} />
      </div>

      <canvas ref={canvasRef} style={{ display: "none" }} />

      <div style={{ marginTop: "10px" }}>
        {!autoRecognize && showControls && (
          <>
            <button onClick={captureImage} disabled={!isCameraReady} style={{ padding: "8px 14px", marginRight: "10px" }}>
              Capture
            </button>
            <button onClick={recognizeFace} disabled={!capturedImage || loading} style={{ padding: "8px 14px" }}>
              {loading ? "Recognizing..." : "Recognize"}
            </button>
          </>
        )}
      </div>

      {result && (
        <div style={{ marginTop: "20px", maxHeight: "100px", overflow: "auto", border: "1px solid #ccc", borderRadius: "5px", padding: "10px" }}>
          <h4>Result:</h4>
          <pre>{JSON.stringify(result, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}
