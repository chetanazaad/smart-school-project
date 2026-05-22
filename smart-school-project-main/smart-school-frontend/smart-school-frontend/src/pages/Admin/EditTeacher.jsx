import { useEffect, useState, useCallback } from "react";
import API from "../../services/api";
import { useNavigate, useParams } from "react-router-dom";
import CameraCapture from "../../components/camera/CameraCapture";

export default function EditTeacher() {
  const navigate = useNavigate();
  const { id } = useParams();

  const [form, setForm] = useState({
    name: "",
    email: "",
    subject: "",
    is_class_teacher: false,
    assigned_class: "",
    assigned_section: "",
    password: "",
    confirmPassword: "",
    id_code: ""
  });

  const [images, setImages] = useState([]);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);

  const fetchTeacher = useCallback(async () => {
    try {
      const res = await API.get(`/teachers/${id}`);
      setForm({
        ...res.data.teacher,
        password: "",
        confirmPassword: ""
      });
    } catch (err) {
      console.error("Error fetching teacher:", err);
      setError("Failed to load teacher details");
    }
  }, [id]);

  useEffect(() => {
    fetchTeacher();
  }, [fetchTeacher]);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setForm({
      ...form,
      [name]: type === "checkbox" ? checked : value,
    });
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

    if (form.is_class_teacher && (!form.assigned_class || !form.assigned_section)) {
      setError("Class and Section are required for Class Teachers");
      return;
    }

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
      await API.put(`/teachers/${id}`, form);

      // 2. If images captured, update face enrollment
      if (images.length > 0) {
        if (images.length < 3) {
          setError("Please capture at least 3 photos for face enrollment");
          setLoading(false);
          return;
        }

        await API.post("/enrollment/enroll", {
          user_id: form.email, // Using email as unique ID
          images: images,
          role: "teacher",
          clear_existing: true
        });
      }

      setSuccess("Teacher updated successfully!");
      window.dispatchEvent(new CustomEvent("entityChanged"));
      setTimeout(() => navigate("/admin/teachers"), 2000);
    } catch (err) {
      console.error("Update failed:", err);
      setError(err.response?.data?.error || "Failed to update teacher");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <h2 className="text-2xl font-semibold mb-6">Edit Teacher Profile</h2>

      {error && (
        <div className="mb-4 p-4 bg-red-100 text-red-700 rounded border border-red-200">
          {error}
        </div>
      )}
      {success && (
        <div className="mb-4 p-4 bg-green-100 text-green-700 rounded border border-green-200">
          {success}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Form Column */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-1">
            <label className="text-sm font-medium">Full Name</label>
            <input
              name="name"
              placeholder="Teacher Name"
              value={form.name}
              onChange={handleChange}
              className="border p-3 rounded w-full"
              required
            />
          </div>

          <div className="space-y-1">
            <label className="text-sm font-medium">Email Address</label>
            <input
              name="email"
              type="email"
              placeholder="Email"
              value={form.email}
              onChange={handleChange}
              className="border p-3 rounded w-full"
              required
            />
          </div>

          <div className="space-y-1">
            <label className="text-sm font-medium">Subject</label>
            <input
              name="subject"
              placeholder="Subject"
              value={form.subject}
              onChange={handleChange}
              className="border p-3 rounded w-full"
              required
            />
          </div>

          <div className="border border-amber-300 bg-amber-50 p-4 rounded">
            <label className="flex items-center gap-3 cursor-pointer">
              <input
                type="checkbox"
                name="is_class_teacher"
                checked={form.is_class_teacher}
                onChange={handleChange}
                className="w-5 h-5"
              />
              <span className="font-medium text-gray-800">This teacher is a Class Teacher</span>
            </label>
          </div>

          {form.is_class_teacher && (
            <div className="grid grid-cols-2 gap-4 p-4 bg-blue-50 border border-blue-200 rounded">
              <div>
                <label className="block text-sm font-medium mb-1">Class</label>
                <input
                  name="assigned_class"
                  placeholder="e.g. 10"
                  value={form.assigned_class || ""}
                  onChange={handleChange}
                  className="border p-3 rounded w-full bg-white"
                  required={form.is_class_teacher}
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Section</label>
                <input
                  name="assigned_section"
                  placeholder="e.g. A"
                  value={form.assigned_section || ""}
                  onChange={handleChange}
                  className="border p-3 rounded w-full bg-white"
                  required={form.is_class_teacher}
                />
              </div>
            </div>
          )}

          <hr className="my-6" />

          <div className="bg-gray-50 p-4 rounded-lg space-y-4">
            <h3 className="font-semibold text-gray-700">Account Security</h3>
            <p className="text-xs text-gray-500">Only fill these if you want to change the password</p>

            <input
              name="password"
              type="password"
              placeholder="New Password"
              value={form.password}
              onChange={handleChange}
              className="border p-3 rounded w-full bg-white"
            />
            <input
              name="confirmPassword"
              type="password"
              placeholder="Confirm New Password"
              value={form.confirmPassword}
              onChange={handleChange}
              className="border p-3 rounded w-full bg-white"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 text-white py-3 rounded font-bold hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? "Updating..." : "Save All Changes"}
          </button>
        </form>

        {/* Camera Column */}
        <div className="space-y-4">
          <h3 className="font-semibold text-lg">Update Face Data</h3>
          <p className="text-sm text-gray-600">
            To update the teacher's biometric profile, capture at least 3 photos from different angles.
            Existing data will be replaced if new photos are saved.
          </p>

          <CameraCapture
            onCapture={(img) => setImages([...images, img])}
            maxCaptures={5}
          />

          <div className="mt-4">
            <h4 className="text-sm font-medium mb-2">Captured Photos ({images.length}/3)</h4>
            <div className="flex flex-wrap gap-2">
              {images.map((img, idx) => (
                <div key={idx} className="relative w-24 h-24">
                  <img src={img} alt="captured" className="w-full h-full object-cover rounded shadow-sm border" />
                  <button
                    onClick={() => removeImage(idx)}
                    className="absolute -top-2 -right-2 bg-red-600 text-white rounded-full w-6 h-6 flex items-center justify-center shadow-md"
                  >
                    ×
                  </button>
                </div>
              ))}
              {images.length === 0 && (
                <div className="w-full py-8 border-2 border-dashed border-gray-200 rounded flex flex-col items-center justify-center text-gray-400">
                  <span className="text-xs italic">No new captures</span>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
