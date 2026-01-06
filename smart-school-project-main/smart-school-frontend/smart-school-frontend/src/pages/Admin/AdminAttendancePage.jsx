import React, { useEffect, useState } from "react";
import api from "../../services/api";
import FaceRecognitionModal from "../../components/FaceRecognitionModal";

export default function AdminAttendancePage() {
  const [openModal, setOpenModal] = useState(false);
  const [attendanceLogs, setAttendanceLogs] = useState([]);
  const [loadingLogs, setLoadingLogs] = useState(false);
  const [formData, setFormData] = useState({
    person_id: "",
    person_type: "student", // or teacher
  });
  const [lastMarked, setLastMarked] = useState(null);

  // ===============================
  // Load Today's Attendance Logs
  // ===============================
  const loadAttendanceLogs = async () => {
    try {
      setLoadingLogs(true);
      const res = await api.get("/attendance-view/all?limit=20");
      setAttendanceLogs(res.data.records || []);
    } catch (err) {
      console.error("Failed loading logs:", err);
    } finally {
      setLoadingLogs(false);
    }
  };

  useEffect(() => {
    loadAttendanceLogs();
  }, []);

  // ===============================
  // Manual Attendance Form Submit
  // ===============================
  const handleManualSubmit = async (e) => {
    e.preventDefault();
    try {
      const res = await api.post("/attendance/mark", {
        id: formData.person_id,
        type: formData.person_type,
      });

      setLastMarked(res.data);
      loadAttendanceLogs();
    } catch (err) {
      console.error("Manual attendance error:", err);
    }
  };

  return (
    <div className="p-6">
      <h2 className="text-2xl font-semibold mb-6">Mark Attendance</h2>

      {/* =============================
          SECTION 1: FACE RECOGNITION
      ============================== */}
      <div className="mb-6">
        <button
          className="px-4 py-2 bg-blue-600 text-white rounded"
          onClick={() => setOpenModal(true)}
        >
          Use Face Recognition
        </button>
      </div>

      {lastMarked && (
        <div className="p-4 bg-green-100 border border-green-300 rounded mb-6">
          <h4 className="font-bold">Attendance Marked:</h4>
          <pre className="text-sm">{JSON.stringify(lastMarked, null, 2)}</pre>
        </div>
      )}

      {/* =============================
          SECTION 2: MANUAL FORM
      ============================== */}
      <div className="mt-4 border p-6 rounded bg-white shadow">
        <h3 className="text-lg font-semibold mb-4">Manual Attendance Form</h3>

        <form onSubmit={handleManualSubmit}>
          <label className="block mb-2">
            Person ID:
            <input
              className="border p-2 rounded w-full mt-1"
              type="text"
              value={formData.person_id}
              onChange={(e) =>
                setFormData({ ...formData, person_id: e.target.value })
              }
              required
            />
          </label>

          <label className="block mb-2">
            Person Type:
            <select
              className="border p-2 rounded w-full mt-1"
              value={formData.person_type}
              onChange={(e) =>
                setFormData({ ...formData, person_type: e.target.value })
              }
            >
              <option value="student">Student</option>
              <option value="teacher">Teacher</option>
            </select>
          </label>

          <button
            className="px-4 py-2 bg-green-600 text-white rounded mt-3"
            type="submit"
          >
            Submit Attendance
          </button>
        </form>
      </div>

      {/* =============================
          SECTION 3: ATTENDANCE LOGS
      ============================== */}
      <div className="mt-8 bg-white p-6 rounded shadow border">
        <h3 className="text-lg font-semibold mb-4">Recent Attendance Logs</h3>

        {loadingLogs ? (
          <p>Loading logs...</p>
        ) : attendanceLogs.length === 0 ? (
          <p>No attendance records found.</p>
        ) : (
          <table className="w-full table-auto border-collapse">
            <thead>
              <tr className="bg-gray-100 border-b">
                <th className="p-2 border">ID</th>
                <th className="p-2 border">Name</th>
                <th className="p-2 border">Type</th>
                <th className="p-2 border">Date</th>
                <th className="p-2 border">Time</th>
              </tr>
            </thead>
            <tbody>
              {attendanceLogs.map((log, index) => (
                <tr key={index} className="border-b">
                  <td className="p-2 border">{log.id}</td>
                  <td className="p-2 border">{log.name}</td>
                  <td className="p-2 border">{log.type}</td>
                  <td className="p-2 border">{log.date}</td>
                  <td className="p-2 border">{log.time}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* =============================
          SECTION 4: FACE RECOGNITION MODAL
      ============================== */}
      <FaceRecognitionModal
        open={openModal}
        onClose={() => setOpenModal(false)}
        onMarked={(data) => {
          setLastMarked(data);
          loadAttendanceLogs();
          setOpenModal(false); // Close modal after successful recognition
        }}
      />
    </div>
  );
}
