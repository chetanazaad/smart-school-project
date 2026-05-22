// src/services/api.js
import axios from "axios";

const API = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:5000/api/v1",
  withCredentials: true,
  timeout: 30000, // 30 second timeout for all requests
});

// Attach token automatically
API.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Global error handling - throw error for components to handle
API.interceptors.response.use(
  (response) => response,
  (error) => {
    // Error is rejected to be handled by individual components
    // This avoids alert spam - components can show user-friendly messages
    return Promise.reject(error);
  }
);

// ------------ AUTH ----------
export const loginUser = (data) => API.post("/auth/login", data);

// ------------ FACE RECOGNITION ----------
// Updated to match backend blueprints:
// - recognition: POST /api/recognition/recognize
// - enrollment: POST /api/enrollment/enroll
export const recognizeFace = (data) => API.post("/recognition/recognize", data);
export const enrollFace = (data) => API.post("/enrollment/enroll", data);

export default API;
