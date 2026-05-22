import React, { useEffect, useState } from "react";
import api from "../../services/api";
import { useAuth } from "../../context/AuthContext";

export default function TeacherAttendancePage() {
  const { user } = useAuth();
  const [records, setRecords] = useState([]);

  const fetchData = async () => {
    if (!user?.id) return;

    try {
      const res = await api.get('/teacher-attendance/records');
      setRecords(res.data);
    } catch (err) {
      console.error("Failed to fetch teacher attendance:", err);
    }
  };

  useEffect(() => {
    fetchData();
  }, [user]);

  return (
    <div className="p-6 bg-white shadow rounded">
      <h2 className="text-2xl font-bold mb-4">My Attendance</h2>

      <table className="w-full border text-left">
        <thead className="bg-gray-100">
          <tr>
            <th className="p-2 border">Date</th>
            <th className="p-2 border">Time</th>
            <th className="p-2 border">Status</th>
          </tr>
        </thead>

        <tbody>
          {records.map((r, i) => {
            const markedAt = r.marked_at || "";
            const timePart = markedAt.includes(" ") ? markedAt.split(" ")[1] : markedAt;
            return (
              <tr key={i}>
                <td className="p-2 border">{r.date}</td>
                <td className="p-2 border">{timePart}</td>
                <td className="p-2 border capitalize">{r.status}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
