// src/pages/Login/LoginPage.jsx

import { useState } from "react";
import { loginUser } from "../../services/api";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";

export default function LoginPage() {
  const [role, setRole] = useState("admin");
  const [email, setEmail] = useState("admin@school.com");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const navigate = useNavigate();
  const { login } = useAuth();

  const handleLogin = async () => {
    setError("");

    if (!email || !password) {
      setError("All fields are required");
      return;
    }

    try {
      console.log("Sending login:", { email, password, role });

      const response = await loginUser({
        email,
        password,
        role,
      });

      const token = response.data.token;
      const userData = response.data.user || { email, role };

      console.log("✓ Login successful!");
      console.log("✓ Token received:", token.substring(0, 30) + "...");
      
      // Store token in localStorage FIRST
      localStorage.setItem("token", token);
      localStorage.setItem("user", JSON.stringify(userData));
      console.log("✓ Stored in localStorage");
      
      // Then update context
      login(token, userData);
      console.log("✓ Updated AuthContext");
      
      // Verify before redirect
      console.log("✓ Verification:");
      console.log("  - localStorage token:", !!localStorage.getItem("token"));
      console.log("  - localStorage user:", !!localStorage.getItem("user"));
      
      // Wait a bit then redirect (gives time for context to update)
      setTimeout(() => {
        if (role === "admin") navigate("/admin/dashboard");
        else if (role === "teacher") navigate("/teacher/dashboard");
        else if (role === "student") navigate("/student/dashboard");
        else if (role === "parent") navigate("/parent/dashboard");
      }, 200);

    } catch (err) {
      console.error("Login failed:", err);
      if (err.response && err.response.status === 401) {
        setError("Invalid email or password");
      } else {
        setError("Server error. Try again later.");
      }
    }
  };

  return (
    <div 
      className="min-h-screen flex items-center justify-center bg-cover bg-center relative"
      style={{ backgroundImage: "url('https://images.unsplash.com/photo-1562774053-701939374585?q=80&w=1986&auto=format&fit=crop')" }}
    >
      <div className="absolute inset-0 bg-black/40 backdrop-blur-sm"></div>
      <style>
        {`
          @keyframes float {
            0% { transform: translateY(0px); }
            50% { transform: translateY(-5px); }
            100% { transform: translateY(0px); }
          }
          .school-title {
            animation: float 3s ease-in-out infinite;
            background: linear-gradient(to right, #2563eb, #0891b2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
          }
        `}
      </style>
      
      <div className="relative z-10 w-full max-w-md p-8 bg-white/90 backdrop-blur-md rounded-2xl shadow-2xl border border-white/50">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-extrabold school-title mb-2">
            Modern Day School
          </h1>
          <p className="text-gray-500 font-medium">Welcome to Smart School</p>
          <p className="text-xs text-gray-400 mt-2">Default admin: email <strong>admin@school.com</strong> / password <strong>admin123</strong></p>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-100 text-red-700 rounded-lg text-sm text-center font-medium border border-red-200">
            {error}
          </div>
        )}

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-1">Select Role</label>
            <select
              value={role}
              onChange={(e) => setRole(e.target.value)}
              className="w-full p-3 rounded-xl border border-gray-200 bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-400 transition-all"
            >
              <option value="admin">Admin</option>
              <option value="teacher">Teacher</option>
              <option value="student">Student</option>
              <option value="parent">Parent</option>
            </select>
          </div>

          <div>
            <input
              type="email"
              placeholder="Email address"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full p-3 rounded-xl border border-gray-200 bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-400 transition-all"
            />
          </div>

          <div>
            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full p-3 rounded-xl border border-gray-200 bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-400 transition-all"
            />
          </div>

          <button
            onClick={handleLogin}
            className="w-full py-3.5 rounded-xl bg-gradient-to-r from-blue-500 to-cyan-500 text-white font-bold text-lg shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 transition-all duration-200"
          >
            Login
          </button>
        </div>

        <div className="mt-8 text-center text-xs text-gray-400">
          © 2025 Modern Day School System
        </div>
      </div>
    </div>
  );
}
