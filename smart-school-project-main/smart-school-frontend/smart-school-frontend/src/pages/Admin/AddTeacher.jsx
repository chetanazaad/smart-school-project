// src/pages/Admin/AddTeacher.jsx
import { useState, useEffect } from "react";
import API from "../../services/api";
import { useNavigate } from "react-router-dom";
import CameraCapture from "../../components/camera/CameraCapture";

export default function AddTeacher() {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    id_code: "",
    name: "",
    email: "",
    subject: "",
    password: "",
    confirmPassword: "",
    is_class_teacher: false,
    assigned_class: "",
    assigned_section: "",
  });
  const [createdId, setCreatedId] = useState(null);
  const [imageBase64, setImageBase64] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const generateTeacherId = async () => {
    try {
      const res = await API.get("/teachers/generate-id");
      return res.data.id_code;
    } catch (err) {
      console.error("Error generating teacher ID:", err);
      // Fallback to client-side generation
      const n = Math.floor(1000 + Math.random() * 9000);
      return `T${n}`;
    }
  };

  useEffect(() => {
    const initializeId = async () => {
      if (!form.id_code) {
        const newId = await generateTeacherId();
        setForm((f) => ({ ...f, id_code: newId }));
      }
    };
    initializeId();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    // Validation
    if (!form.name || !form.email || !form.subject || !form.password) {
      setError("All fields are required");
      return;
    }

    if (form.password.length < 6) {
      setError("Password must be at least 6 characters");
      return;
    }

    if (form.password !== form.confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    if (form.is_class_teacher && (!form.assigned_class || !form.assigned_section)) {
      setError("Class and Section are required for Class Teachers");
      return;
    }

    if (!imageBase64) {
      setError("Please enroll the teacher's face using the camera before submitting.");
      return;
    }

    setLoading(true);
    try {
      // 1) Create teacher record AND user account
      const createRes = await API.post("/teachers", {
        id_code: form.id_code,
        name: form.name,
        email: form.email,
        subject: form.subject,
        password: form.password,
        is_class_teacher: form.is_class_teacher,
        assigned_class: form.is_class_teacher ? form.assigned_class : null,
        assigned_section: form.is_class_teacher ? form.assigned_section : null,
      });

      const teacherId = createRes.data?.id;
      setCreatedId(teacherId || null);

      // 2) Enroll face
      if (teacherId) {
        await API.post("/face/enroll", {
          role: "teacher",
          user_id: teacherId,
          image: imageBase64,
        });
      }

      navigate("/admin/teachers");
    } catch (err) {
      console.error("Add teacher failed:", err);
      setError(err.response?.data?.error || "Enrollment failed. See console for details.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6">
      <h2 className="text-2xl font-semibold mb-5">Add Teacher</h2>

      {error && (
        <div className="mb-4 p-4 bg-red-100 text-red-700 rounded border border-red-200">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4 max-w-md">

        <div className="flex items-center gap-2">
          <input
            name="id_code"
            placeholder="Teacher ID (e.g. T1001)"
            value={form.id_code}
            onChange={handleChange}
            className="border p-3 rounded w-full"
          />
          <button type="button" onClick={async () => {
            const newId = await generateTeacherId();
            setForm(f => ({...f, id_code: newId}));
          }} className="px-3 py-2 bg-gray-200 rounded">New</button>
        </div>

        <input
          name="name"
          placeholder="Teacher Name"
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

        <input
          name="subject"
          placeholder="Subject"
          value={form.subject}
          onChange={handleChange}
          className="border p-3 rounded w-full"
          required
        />

        <div className="border border-amber-300 bg-amber-50 p-4 rounded">
          <label className="flex items-center gap-3 cursor-pointer">
            <input
              type="checkbox"
              name="is_class_teacher"
              checked={form.is_class_teacher}
              onChange={(e) => setForm({ ...form, is_class_teacher: e.target.checked })}
              className="w-5 h-5"
            />
            <span className="font-medium text-gray-800">This teacher is a Class Teacher</span>
          </label>
          <p className="text-sm text-gray-600 mt-2">Class teachers manage a specific class and can enroll students</p>
        </div>

        {form.is_class_teacher && (
          <div className="space-y-3 p-4 bg-blue-50 border border-blue-200 rounded">
            <div>
              <label className="block text-sm font-medium mb-1">Class Name *</label>
              <input
                name="assigned_class"
                placeholder="e.g., Class 10, Class 11"
                value={form.assigned_class}
                onChange={handleChange}
                className="border p-3 rounded w-full"
                required={form.is_class_teacher}
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Section *</label>
              <input
                name="assigned_section"
                placeholder="e.g., A, B, C"
                value={form.assigned_section}
                onChange={handleChange}
                className="border p-3 rounded w-full"
                required={form.is_class_teacher}
              />
            </div>
          </div>
        )}

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
          <p className="text-sm text-gray-600 mt-2">Password must be at least 6 characters</p>
        </div>

        {createdId && (
          <input
            name="id"
            placeholder="Created ID"
            value={createdId}
            readOnly
            className="border p-3 rounded w-full bg-gray-100 mt-2"
          />
        )}

        <div>
          <label className="block text-sm font-medium mb-2">Enroll Face (required)</label>
          <CameraCapture onCapture={(b64) => setImageBase64(b64)} />
          {imageBase64 && (
            <img src={imageBase64} alt="captured" className="mt-3 w-48 h-auto rounded border" />
          )}
        </div>

        <button
          type="submit"
          disabled={loading}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? "Adding..." : "Add Teacher"}
        </button>
      </form>
    </div>
  );
}
