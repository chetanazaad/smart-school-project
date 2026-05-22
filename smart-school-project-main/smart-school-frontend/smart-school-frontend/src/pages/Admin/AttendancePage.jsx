// src/pages/Admin/AttendancePage.jsx
import { useEffect, useState } from "react";
import API from "../../services/api";

export default function AttendancePage() {
  const [attendance, setAttendance] = useState([]);
  const [selectedDate, setSelectedDate] = useState(
    new Date().toISOString().split("T")[0]
  );
  const [loading, setLoading] = useState(true);

  const fetchAttendance = async () => {
    setLoading(true);
    try {
      const res = await API.get(`/teacher-attendance/all_records?date=${selectedDate}`);
      setAttendance(res.data || []);
      setLoading(false);
    } catch (err) {
      console.error("Error fetching attendance:", err);
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAttendance();
  }, [selectedDate]);

  if (loading) return <div className="p-6 text-lg">Loading...</div>;

  return (
    <div className="p-6">
      <h2 className="text-2xl font-semibold mb-6">Teacher Attendance</h2>

      <div className="mb-6">
        <label className="block text-sm font-medium mb-2">Select Date:</label>
        <input
          type="date"
          value={selectedDate}
          onChange={(e) => setSelectedDate(e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded"
        />
      </div>

      {attendance.length === 0 ? (
        <p>No attendance records found for {selectedDate}.</p>
      ) : (
        <table className="w-full border">
          <thead>
            <tr className="bg-gray-200">
              <th className="p-3 border">Teacher ID</th>
              <th className="p-3 border">Teacher Name</th>
              <th className="p-3 border">Status</th>
              <th className="p-3 border">Date</th>
            </tr>
          </thead>

          <tbody>
            {attendance.map((a) => (
              <tr key={a.teacher_id} className="text-center">
                <td className="p-3 border">{a.teacher_id}</td>
                <td className="p-3 border">{a.teacher_name}</td>
                <td className="p-3 border">
                  <span className={`px-3 py-1 rounded ${
                    a.status === "present" ? "bg-green-200 text-green-800" : "bg-red-200 text-red-800"
                  }`}>
                    {a.status}
                  </span>
                </td>
                <td className="p-3 border">{a.date}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
