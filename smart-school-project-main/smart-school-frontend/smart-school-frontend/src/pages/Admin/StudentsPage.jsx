// src/pages/Admin/StudentsPage.jsx
import { useEffect, useState, useCallback } from "react";
import API from "../../services/api";
import { Link } from "react-router-dom";

export default function StudentsPage() {
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [enrolledIds, setEnrolledIds] = useState(new Set());

  // Fetch students and their face enrollment status from backend
  const fetchStudents = useCallback(async () => {
    try {
      const response = await API.get("/students");

      console.log("STUDENT LIST RESPONSE:", response.data);

      const list = Array.isArray(response.data.students)
        ? response.data.students
        : [];

      setStudents(list);

      // Also fetch face enrollment status
      try {
        const statsResponse = await API.get("/face/enrollment-stats");
        const enrolled = statsResponse.data?.enrolled_students || [];
        setEnrolledIds(new Set(enrolled.map(s => s.id)));
      } catch (enrollErr) {
        console.log("Could not fetch enrollment status:", enrollErr);
      }
    } catch (error) {
      console.error("Error loading students:", error);
      setStudents([]); // prevent frontend crash
    } finally {
      setLoading(false);
    }
  }, []);

  const handleDelete = async (id) => {
    if (!window.confirm("Are you sure you want to delete this student?")) return;

    try {
      await API.delete(`/students/${id}`);
      fetchStudents(); // refresh table
      window.dispatchEvent(new CustomEvent("entityChanged"));
    } catch (error) {
      console.error("Delete failed:", error);
    }
  };

  useEffect(() => {
    fetchStudents();
  }, [fetchStudents]);

  if (loading) return <div className="p-6 text-lg">Loading students...</div>;

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-semibold">Students ({students.length})</h2>

        <Link
          to="/admin/add-student"
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          + Add Student
        </Link>
      </div>

      {/* Empty state */}
      {students.length === 0 ? (
        <div className="text-center py-8">
          <p className="text-gray-500 mb-4">No students found.</p>
          <Link
            to="/admin/add-student"
            className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
          >
            + Add First Student
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
                <th className="p-3 border">Roll No.</th>
                <th className="p-3 border">ID Code (Custom ID)</th>
                <th className="p-3 border">Class</th>
                <th className="p-3 border">Section</th>
                <th className="p-3 border">Face Enrolled</th>
                <th className="p-3 border">Actions</th>
              </tr>
            </thead>

            <tbody>
              {students.map((s, index) => {
                const isEnrolled = enrolledIds.has(s.id);
                return (
                  <tr key={s.id} className="text-center hover:bg-gray-50">
                    <td className="p-3 border text-xs text-gray-400">{index + 1}</td>
                    <td className="p-3 border font-medium">{s.name}</td>
                    <td className="p-3 border">{s.email || "—"}</td>
                    <td className="p-3 border">{s.roll_number || "—"}</td>
                    <td className="p-3 border font-semibold text-blue-700">{s.id_code || "—"}</td>
                    <td className="p-3 border">{s.class_name || "—"}</td>
                    <td className="p-3 border">{s.section || "—"}</td>
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
                        to={`/admin/edit-student/${s.id}`}
                        className="text-blue-600 hover:text-blue-800"
                      >
                        Edit
                      </Link>
                      <Link
                        to={`/admin/enrollment/student/${s.id}`}
                        className={`${isEnrolled ? 'text-green-600' : 'text-orange-600'} hover:underline`}
                      >
                        {isEnrolled ? 'Re-enroll' : 'Enroll'}
                      </Link>
                      <button
                        onClick={() => handleDelete(s.id)}
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
      {students.length > 0 && (
        <div className="mt-4 p-4 bg-gray-100 rounded-lg">
          <h3 className="font-semibold mb-2">Summary:</h3>
          <p>Total Students: {students.length}</p>
          <p>Face Enrolled: {enrolledIds.size}</p>
          <p>Not Enrolled: {students.length - enrolledIds.size}</p>
        </div>
      )}
    </div>
  );
}
