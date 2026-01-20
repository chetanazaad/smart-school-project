import { useEffect, useState } from "react";
import API from "../../services/api";
import { useNavigate, useParams } from "react-router-dom";

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
  });

  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const fetchTeacher = async () => {
    try {
      const res = await API.get(`/teachers/${id}`);
      setForm(res.data.teacher);
    } catch (err) {
      console.error("Error fetching teacher:", err);
      setError("Failed to load teacher details");
    }
  };

  useEffect(() => {
    fetchTeacher();
  }, []);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setForm({
      ...form,
      [name]: type === "checkbox" ? checked : value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    if (form.is_class_teacher && (!form.assigned_class || !form.assigned_section)) {
      setError("Class and Section are required for Class Teachers");
      return;
    }

    setLoading(true);
    try {
      await API.put(`/teachers/${id}`, form);
      navigate("/admin/teachers");
    } catch (err) {
      console.error("Update failed:", err);
      setError(err.response?.data?.error || "Failed to update teacher");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6">
      <h2 className="text-2xl font-semibold mb-5">Edit Teacher</h2>

      {error && (
        <div className="mb-4 p-4 bg-red-100 text-red-700 rounded border border-red-200">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4 max-w-md">
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
              onChange={handleChange}
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
                value={form.assigned_class || ""}
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
                value={form.assigned_section || ""}
                onChange={handleChange}
                className="border p-3 rounded w-full"
                required={form.is_class_teacher}
              />
            </div>
          </div>
        )}

        <button
          type="submit"
          disabled={loading}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? "Updating..." : "Update Teacher"}
        </button>
      </form>
    </div>
  );
}
