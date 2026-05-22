// src/pages/Admin/EditStudent.jsx
import { useEffect, useState, useCallback } from "react";
import API from "../../services/api";
import { useNavigate, useParams } from "react-router-dom";
import CameraCapture from "../../components/camera/CameraCapture";

export default function EditStudent() {
  const navigate = useNavigate();
  const { id } = useParams();

  const [form, setForm] = useState({
    name: "",
    email: "",
    class_name: "1",
    section: "A",
    password: "",
    confirmPassword: "",
    id_code: ""
  });

  const [images, setImages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const fetchStudent = useCallback(async () => {
    try {
      const res = await API.get(`/students/${id}`);
      setForm({
        ...res.data.student,
        password: "",
        confirmPassword: ""
      });
    } catch (err) {
      console.error("Error loading student:", err);
      setError("Failed to load student data");
    }
  }, [id]);

  useEffect(() => {
    fetchStudent();
  }, [fetchStudent]);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const removeImage = (index) => {
    setImages(images.filter((_, i) => i !== index));
  };

  const validatePassword = (password) => {
    if (password && password.length < 8) return "Password must be at least 8 characters long";
    if (password && !/[A-Z]/.test(password)) return "Password must contain an uppercase letter";
    if (password && !/[0-9]/.test(password)) return "Password must contain a number";
    return null;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess("");

    if (form.password && form.password !== form.confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    const passError = validatePassword(form.password);
    if (passError) {
      setError(passError);
      return;
    }

    setLoading(true);
    try {
      // 1. Update Profile Info
      await API.put(`/students/${id}`, form);

      // 2. If images captured, update face enrollment
      if (images.length > 0) {
        if (images.length < 3) {
          setError("Please capture at least 3 photos for face enrollment");
          setLoading(false);
          return;
        }

        await API.post("/enrollment/enroll", {
          user_id: form.email, // Using email as unique ID for face
          images: images,
          role: "student",
          clear_existing: true
        });
      }

      setSuccess("Student updated successfully!");
      window.dispatchEvent(new CustomEvent("entityChanged"));
      setTimeout(() => navigate("/admin/students"), 2000);
    } catch (err) {
      console.error("Update failed:", err);
      setError(err.response?.data?.error || "Failed to update student");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <h2 className="text-2xl font-semibold mb-6">Edit Student Profile</h2>

      {error && <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">{error}</div>}
      {success && <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4">{success}</div>}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Profile Details */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <label className="block text-sm font-medium">Full Name</label>
            <input
              name="name"
              value={form.name}
              onChange={handleChange}
              className="border p-3 rounded w-full"
              required
            />
          </div>

          <div className="space-y-2">
            <label className="block text-sm font-medium">Email Address</label>
            <input
              name="email"
              type="email"
              value={form.email}
              onChange={handleChange}
              className="border p-3 rounded w-full"
              required
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <label className="block text-sm font-medium">Class</label>
              <select name="class_name" value={form.class_name} onChange={handleChange} className="border p-3 rounded w-full">
                {Array.from({ length: 12 }, (_, i) => String(i + 1)).map((c) => (
                  <option key={c} value={c}>{`Class ${c}`}</option>
                ))}
              </select>
            </div>
            <div className="space-y-2">
              <label className="block text-sm font-medium">Section</label>
              <select name="section" value={form.section || "A"} onChange={handleChange} className="border p-3 rounded w-full">
                {["A", "B", "C", "D", "E", "F"].map((s) => (
                  <option key={s} value={s}>{s}</option>
                ))}
              </select>
            </div>
          </div>

          <hr className="my-6" />

          <div className="bg-gray-50 p-4 rounded-lg space-y-4">
            <h3 className="font-semibold text-gray-700">Change Password (Optional)</h3>
            <p className="text-xs text-gray-500">Leave blank to keep current password</p>

            <input
              name="password"
              type="password"
              placeholder="New Password"
              value={form.password}
              onChange={handleChange}
              className="border p-3 rounded w-full"
            />
            <input
              name="confirmPassword"
              type="password"
              placeholder="Confirm New Password"
              value={form.confirmPassword}
              onChange={handleChange}
              className="border p-3 rounded w-full"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className={`w-full py-3 text-white rounded font-bold ${loading ? 'bg-gray-400' : 'bg-blue-600 hover:bg-blue-700'}`}
          >
            {loading ? "Updating..." : "Save All Changes"}
          </button>
        </form>

        {/* Face Enrollment */}
        <div className="space-y-4">
          <h3 className="font-semibold text-lg">Update Face Enrollment</h3>
          <p className="text-sm text-gray-600 mb-4">
            If you want to update the student's face data, capture at least 3 photos below.
            If you don't capture new photos, the existing face data will remain.
          </p>

          <CameraCapture
            onCapture={(img) => setImages([...images, img])}
            maxCaptures={5}
          />

          <div className="mt-4">
            <h4 className="text-sm font-medium mb-2">Captured Photos ({images.length}/3 required to update)</h4>
            <div className="flex flex-wrap gap-2">
              {images.map((img, idx) => (
                <div key={idx} className="relative w-20 h-20">
                  <img src={img} alt="captured" className="w-full h-full object-cover rounded border" />
                  <button
                    onClick={() => removeImage(idx)}
                    className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full w-5 h-5 flex items-center justify-center text-xs"
                  >
                    ×
                  </button>
                </div>
              ))}
              {images.length === 0 && <p className="text-xs text-gray-400 italic">No new photos captured</p>}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
