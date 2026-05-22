// src/pages/Admin/TeachersPage.jsx
import { useEffect, useState, useCallback } from "react";
import API from "../../services/api";
import { Link } from "react-router-dom";

export default function TeachersPage() {
  const [teachers, setTeachers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [enrolledIds, setEnrolledIds] = useState(new Set());

  const fetchTeachers = useCallback(async () => {
    try {
      const res = await API.get("/teachers");
      setTeachers(res.data.teachers || []);

      // Fetch face enrollment status for teachers
      try {
        const statsResponse = await API.get("/face/enrollment-stats");
        const enrolledTeachers = statsResponse.data?.enrolled_teachers || [];
        setEnrolledIds(new Set(enrolledTeachers.map(t => t.id)));
      } catch (enrollErr) {
        console.log("Could not fetch enrollment stats:", enrollErr);
      }
      setLoading(false);
    } catch (err) {
      console.error("Error fetching teachers:", err);
      setLoading(false);
    }
  }, []);

  const handleDelete = async (id) => {
    if (!window.confirm("Delete this teacher?")) return;

    try {
      await API.delete(`/teachers/${id}`);
      fetchTeachers();
    } catch (err) {
      console.error("Delete failed:", err);
    }
  };

  useEffect(() => {
    fetchTeachers();
  }, [fetchTeachers]);

  if (loading) return <div className="p-6 text-lg">Loading...</div>;

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-semibold">Teachers ({teachers.length})</h2>

        <Link
          to="/admin/add-teacher"
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          + Add Teacher
        </Link>
      </div>

      {teachers.length === 0 ? (
        <div className="text-center py-8">
          <p className="text-gray-500 mb-4">No teachers found.</p>
          <Link
            to="/admin/add-teacher"
            className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
          >
            + Add First Teacher
          </Link>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full border">
            <thead>
              <tr className="bg-gray-200">
                <th className="p-3 border text-xs text-gray-400">#</th>
                <th className="p-3 border">Name</th>
                <th className="p-3 border">Email</th>
                <th className="p-3 border">Subject</th>
                <th className="p-3 border">ID Code (Custom ID)</th>
                <th className="p-3 border">Face Enrolled</th>
                <th className="p-3 border">Actions</th>
              </tr>
            </thead>

            <tbody>
              {teachers.map((t, index) => {
                const isEnrolled = enrolledIds.has(t.id);
                return (
                  <tr key={t.id} className="text-center hover:bg-gray-50">
                    <td className="p-3 border text-xs text-gray-400">{index + 1}</td>
                    <td className="p-3 border font-medium">{t.name}</td>
                    <td className="p-3 border">{t.email || "—"}</td>
                    <td className="p-3 border">{t.subject || "—"}</td>
                    <td className="p-3 border font-semibold text-blue-700">{t.id_code || "—"}</td>
                    <td className="p-3 border">
                      {isEnrolled ? (
                        <span className="bg-green-100 text-green-800 px-2 py-1 rounded text-sm">
                          ✅ Enrolled
                        </span>
                      ) : (
                        <span className="bg-yellow-100 text-yellow-800 px-2 py-1 rounded text-sm">
                          ⚠️ Not Enrolled
                        </span>
                      )}
                    </td>
                    <td className="p-3 border space-x-2">
                      <Link
                        to={`/admin/edit-teacher/${t.id}`}
                        className="text-blue-600 hover:text-blue-800"
                      >
                        Edit
                      </Link>
                      <Link
                        to={`/admin/enrollment/teacher/${t.id}`}
                        className={`${isEnrolled ? 'text-green-600' : 'text-orange-600'} hover:underline`}
                      >
                        {isEnrolled ? 'Re-enroll' : 'Enroll'}
                      </Link>
                      <button
                        onClick={() => handleDelete(t.id)}
                        className="text-red-600 hover:text-red-800"
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* Summary */}
      {teachers.length > 0 && (
        <div className="mt-4 p-4 bg-gray-100 rounded-lg">
          <h3 className="font-semibold mb-2">Summary:</h3>
          <p>Total Teachers: {teachers.length}</p>
          <p>Face Enrolled: {enrolledIds.size}</p>
          <p>Not Enrolled: {teachers.length - enrolledIds.size}</p>
        </div>
      )}
    </div>
  );
}
