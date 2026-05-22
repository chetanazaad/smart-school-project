// src/pages/Parent/ParentDashboard.jsx

import React, { useEffect, useState } from "react";
import API from "../../services/api";
import { useAuth } from "../../context/AuthContext";
import { useNavigate } from "react-router-dom";

export default function ParentDashboard() {
  const { user, token } = useAuth();
  const navigate = useNavigate();

  const [studentInfo, setStudentInfo] = useState(null);

  const [stats, setStats] = useState({
    total_days: 0,
    present_days: 0,
    percentage: 0,
    today_status: "Not Marked",
  });

  const [recent, setRecent] = useState([]);

  // Load student assigned to parent
  const loadStudentInfo = async () => {
    try {
      const res = await API.get(`/parents/${user.id}/student`);
      setStudentInfo(res.data.student);
    } catch (err) {
      console.error("Parent student fetch error:", err);
    }
  };

  // Load student attendance stats
  const loadStats = async (studentId) => {
    try {
      const s1 = await API.get(`/student-attendance/${studentId}/stats`);
      const s2 = await API.get(`/student-attendance/${studentId}/today`);

      setStats({
        total_days: s1.data.total_days || 0,
        present_days: s1.data.present_days || 0,
        percentage: s1.data.percentage || 0,
        today_status: s2.data.status || "Not Marked",
      });
    } catch (err) {
      console.error("Parent stats error:", err);
    }
  };

  // Load recent logs
  const loadRecent = async (studentId) => {
    try {
      const logs = await API.get(
        `/student-attendance/${studentId}/logs?limit=5`
      );
      setRecent(logs.data.data || []);
    } catch (err) {
      console.error("Parent recent logs error:", err);
    }
  };

  useEffect(() => {
    if (token) {
      loadStudentInfo();
    }
  }, [token]);

  useEffect(() => {
    if (studentInfo?.id) {
      loadStats(studentInfo.id);
      loadRecent(studentInfo.id);
    }
  }, [studentInfo]);

  return (
    <div className="p-4 md:p-6">
      
      <h1 className="text-2xl font-bold mb-4">Parent Dashboard</h1>

      {/* Student Info Selected */}
      {studentInfo ? (
        <div className="p-4 bg-white rounded shadow mb-6">
          <h2 className="text-xl font-semibold mb-2">Student Information</h2>
          <p><strong>Name:</strong> {studentInfo.name}</p>
          <p><strong>Class:</strong> {studentInfo.class_name}</p>
          <p><strong>Section:</strong> {studentInfo.section}</p>
        </div>
      ) : (
        <p className="text-gray-600 mb-4">Loading student information...</p>
      )}

      {/* Summary Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <SummaryCard title="Total Days" count={stats.total_days} color="blue" />
        <SummaryCard title="Present Days" count={stats.present_days} color="green" />
        <SummaryCard title="Attendance %" count={`${stats.percentage}%`} color="purple" />
        <SummaryCard title="Today's Status" count={stats.today_status} color="orange" />
      </div>

      {/* Quick Actions */}
      <h2 className="text-xl font-semibold mb-2">Quick Actions</h2>
      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-3 gap-4 mb-6">

        <ActionButton
          label="View Attendance"
          onClick={() => navigate(`/parent-performance`)}
          color="green"
        />

        <ActionButton
          label="Student Timetable"
          onClick={() => navigate("/student-timetable")}
          color="purple"
        />


      </div>

      {/* Recent Logs */}
      <h2 className="text-xl font-semibold mb-3">Recent Attendance</h2>
      <div className="bg-white shadow rounded p-4">
        <table className="w-full text-left">
          <thead>
            <tr className="border-b">
              <th className="py-2">Date</th>
              <th className="py-2">Time</th>
              <th className="py-2">Status</th>
            </tr>
          </thead>

          <tbody>
            {recent.length === 0 ? (
              <tr>
                <td colSpan="3" className="py-4 text-center text-gray-500">
                  No attendance found
                </td>
              </tr>
            ) : (
              recent.map((log, index) => (
                <tr key={index} className="border-b hover:bg-gray-50">
                  <td className="py-2">{log.date}</td>
                  <td className="py-2">{log.time}</td>
                  <td className="py-2">
                    <span className="px-2 py-1 bg-green-100 text-green-700 rounded text-sm">
                      Present
                    </span>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

    </div>
  );
}


/* =======================
   COMPONENTS
======================= */

function SummaryCard({ title, count, color }) {
  const colors = {
    blue: "bg-blue-100 text-blue-700",
    green: "bg-green-100 text-green-700",
    purple: "bg-purple-100 text-purple-700",
    orange: "bg-orange-100 text-orange-700",
  };

  return (
    <div className={`p-4 rounded shadow ${colors[color]}`}>
      <h3 className="text-lg font-semibold">{title}</h3>
      <p className="text-2xl font-bold">{count}</p>
    </div>
  );
}

function ActionButton({ label, onClick, color }) {
  const colors = {
    green: "bg-green-600 hover:bg-green-700",
    purple: "bg-purple-600 hover:bg-purple-700",
    orange: "bg-orange-600 hover:bg-orange-700",
  };

  return (
    <button
      onClick={onClick}
      className={`w-full py-3 text-white rounded font-semibold ${colors[color]}`}
    >
      {label}
    </button>
  );
}
