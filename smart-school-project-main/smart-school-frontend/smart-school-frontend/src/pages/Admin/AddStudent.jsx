// src/pages/Admin/AddStudent.jsx
import { useState, useEffect, useCallback } from "react";
import API from "../../services/api";
import { useNavigate } from "react-router-dom";
import CameraCapture from "../../components/camera/CameraCapture";

export default function AddStudent() {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    roll_number: "",
    id_code: "",
    name: "",
    email: "",
    class_name: "1",
    section: "A",
    password: "",
    confirmPassword: "",
  });
  const [images, setImages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const addImage = (b64) => {
    if (images.length < 3) {
      setImages([...images, b64]);
    } else {
      alert("You have already captured 3 photos. Delete one to take a new one.");
    }
  };

  const removeImage = (index) => {
    setImages(images.filter((_, i) => i !== index));
  };

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  // generate default ID like ST0001
  const generateStudentId = useCallback(async () => {
    try {
      const res = await API.get("/students/generate-id");
      return res.data.id_code;
    } catch (err) {
      console.error("Error generating student ID:", err);
      // Fallback
      const n = Math.floor(1000 + Math.random() * 9000);
      return `ST${n}`;
    }
  }, []);

  useEffect(() => {
    const initializeId = async () => {
      if (!form.id_code) {
        const newId = await generateStudentId();
        setForm((f) => ({ ...f, id_code: newId }));
      }
    };
    initializeId();
  }, [form.id_code, generateStudentId]);

  // Validate password strength
  const validatePassword = (password) => {
    if (password.length < 8) {
      return "Password must be at least 8 characters long";
    }
    if (!/[A-Z]/.test(password)) {
      return "Password must contain at least one uppercase letter";
    }
    if (!/[a-z]/.test(password)) {
      return "Password must contain at least one lowercase letter";
    }
    if (!/[0-9]/.test(password)) {
      return "Password must contain at least one digit";
    }
    if (!/[!@#$%^&*(),.?\":{}|<>]/.test(password)) {
      return "Password must contain at least one special character";
    }
    return null;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    // Validation
    if (!form.name || !form.email || !form.password) {
      setError("All fields are required");
      return;
    }

    // Password strength validation
    const passwordError = validatePassword(form.password);
    if (passwordError) {
      setError(passwordError);
      return;
    }

    if (form.password !== form.confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    if (images.length < 3) {
      setError("Please enroll exactly 3 face photos from different angles (front, left, right).");
      setLoading(false);
      return;
    }

    setLoading(true);
    try {
      // 1) Create student record AND user account
      const createRes = await API.post("/students", {
        roll_number: form.roll_number,
        id_code: form.id_code,
        name: form.name,
        email: form.email,
        class_name: form.class_name,
        section: form.section || "",
        password: form.password,
      });

      // 2) Enroll multiple face images using EMAIL (Unique ID)
      await API.post("/enrollment/enroll", {
        role: "student",
        user_id: form.email, // Use unique email as requested
        images: images,
        clear_existing: true
      });

      // Reset form on success, fetching new ID
      const nextId = await generateStudentId();
      setForm({
        roll_number: "",
        id_code: nextId,
        name: "",
        email: "",
        class_name: "1",
        section: "A",
        password: "",
        confirmPassword: "",
      });
      navigate("/admin/students");

    } catch (err) {
      console.error("Add student failed:", err);
      setError(err.response?.data?.error || "Enrollment failed. See console for details.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6">
      <h2 className="text-2xl font-semibold mb-5">Add Student</h2>

      {error && (
        <div className="mb-4 p-4 bg-red-100 text-red-700 rounded border border-red-200">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4 max-w-md">

        <div className="flex items-center gap-2">
          <input
            name="id_code"
            placeholder="Student ID (e.g. ST1001)"
            value={form.id_code}
            onChange={handleChange}
            className="border p-3 rounded w-full"
          />
          <button type="button" onClick={async () => {
            const newId = await generateStudentId();
            setForm(f => ({ ...f, id_code: newId }));
          }} className="px-3 py-2 bg-gray-200 rounded">New</button>
        </div>

        <input
          name="roll_number"
          placeholder="Roll Number"
          value={form.roll_number}
          onChange={handleChange}
          className="border p-3 rounded w-full"
        />



        <input
          name="name"
          placeholder="Student Name"
          value={form.name}
          onChange={handleChange}
          className="border p-3 rounded w-full"
          required
        />

        <input
          name="email"
          type="email"
          placeholder="Email"
          value={form.email}
          onChange={handleChange}
          className="border p-3 rounded w-full"
          required
        />

        <label className="block">
          <span className="text-sm">Class</span>
          <select name="class_name" value={form.class_name} onChange={handleChange} className="border p-3 rounded w-full mt-1">
            {Array.from({ length: 12 }, (_, i) => i + 1).map((c) => (
              <option key={c} value={String(c)}>{`Class ${c}`}</option>
            ))}
          </select>
        </label>

        <label className="block">
          <span className="text-sm">Section</span>
          <select name="section" value={form.section} onChange={handleChange} className="border p-3 rounded w-full mt-1">
            {["A", "B", "C", "D", "E", "F"].map((s) => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
        </label>

        <div className="bg-blue-50 p-4 rounded border border-blue-200">
          <h3 className="font-semibold text-blue-900 mb-3">Login Credentials</h3>

          <input
            name="password"
            type="password"
            placeholder="Password"
            value={form.password}
            onChange={handleChange}
            className="border p-3 rounded w-full mb-2"
            required
          />

          <input
            name="confirmPassword"
            type="password"
            placeholder="Confirm Password"
            value={form.confirmPassword}
            onChange={handleChange}
            className="border p-3 rounded w-full"
            required
          />
          <p className="text-sm text-gray-600 mt-2">
            Password must be at least 8 characters with uppercase, lowercase, digit, and special character
          </p>
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">Enroll Face (3 angles recommended for max accuracy)</label>
          <CameraCapture onCapture={addImage} />

          <div className="flex gap-2 mt-3 overflow-x-auto pb-2">
            {images.map((img, idx) => (
              <div key={idx} className="relative group">
                <img src={img} alt={`captured-${idx}`} className="w-24 h-24 object-cover rounded border shadow-sm" />
                <button
                  type="button"
                  onClick={() => removeImage(idx)}
                  className="absolute -top-2 -right-2 bg-red-600 text-white text-xs w-5 h-5 rounded-full flex items-center justify-center hover:bg-red-700 shadow-md"
                >
                  ✕
                </button>
              </div>
            ))}
            {images.length === 0 && <p className="text-gray-400 text-sm italic">No photos captured yet.</p>}
          </div>
          <p className="text-xs text-gray-500 mt-1">
            Photos captured: {images.length}/3. Tip: Capture front, left, and right angles.
          </p>
        </div>


        <button
          type="submit"
          disabled={loading}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50 w-full"
        >
          {loading ? "Adding..." : "Add Student"}
        </button>
      </form>
    </div>
  );
}
