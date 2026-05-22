// src/pages/Teacher/TeacherDashboard.jsx

import React, { useEffect, useState, useCallback } from "react";
import { useAuth } from "../../context/AuthContext";
import { useNavigate } from "react-router-dom";
import API from "../../services/api";

export default function TeacherDashboard() {
  const { user, token } = useAuth();
  const navigate = useNavigate();

  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    total_students: 0,
    today_present: 0,
    classes_today: 0,
  });

  const [recent, setRecent] = useState([]);

  // Fetch Teacher Dashboard Stats
  const loadStats = useCallback(async () => {
    if (!user?.id) return;

    try {
      // For class teachers, get enrolled students count
      if (user.is_class_teacher) {
        const res1 = await API.get(`/teachers/${user.id}/enrolled-students`);
        const res2 = await API.get(`/attendance/teacher/${user.id}/today`);
        const res3 = await API.get(`/timetable/teacher/${user.id}/today`);

        setStats({
          total_students: res1.data.total_students || 0,
          today_present: res2.data.present || 0,
          classes_today: res3.data.count || 0,
        });
      } else {
        // For regular teachers, show 0 students
        const res2 = await API.get(`/attendance/teacher/${user.id}/today`);
        const res3 = await API.get(`/timetable/teacher/${user.id}/today`);

        setStats({
          total_students: 0,
          today_present: res2.data.present || 0,
          classes_today: res3.data.count || 0,
        });
      }
    } catch (err) {
      console.error("Teacher stats error:", err);
    } finally {
      setLoading(false);
    }
  }, [user]);

  // Fetch Latest Logs for Teacher
  const loadRecent = useCallback(async () => {
    if (!user?.id) return;

    try {
      const res = await API.get(
        `/attendance-view/teacher/${user.id}?limit=5`
      );
      // Backend returns data in 'data' or 'records'? Fixed backend to return both.
      setRecent(res.data.data || res.data.records || []);
    } catch (err) {
      console.error("Teacher logs error:", err);
    }
  }, [user]);

  useEffect(() => {
    loadStats();
    loadRecent();
  }, [loadStats, loadRecent]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="p-4 md:p-6">

      {/* Header - Aligned with AdminDashboard style */}
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold">Teacher Dashboard</h1>
        <button
          onClick={() => {
            setLoading(true);
            loadStats();
            loadRecent();
          }}
          className="px-4 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300"
        >
          Refresh
        </button>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-6">
        <SummaryCard title="My Students" count={stats.total_students} color="blue" />
        <SummaryCard title="Present Today" count={stats.today_present} color="green" />
        <SummaryCard title="Classes Today" count={stats.classes_today} color="purple" />
      </div>

      {/* Quick Actions */}
      <h2 className="text-xl font-semibold mb-2">Quick Actions</h2>
      <div className={`grid grid-cols-1 md:grid-cols-2 ${user?.is_class_teacher ? 'lg:grid-cols-4' : 'lg:grid-cols-3'} gap-4 mb-6`}>

        <ActionButton
          label="Mark Attendance"
          onClick={() => navigate("/teacher/attendance")}
          color="blue"
        />

        {user?.is_class_teacher && (
          <ActionButton
            label="Enroll Student"
            onClick={() => navigate("/teacher/add-student")}
            color="green"
          />
        )}

        {user?.is_class_teacher && (
          <ActionButton
            label="My Students"
            onClick={() => navigate("/teacher/students")}
            color="teal"
          />
        )}

        <ActionButton
          label="My Timetable"
          onClick={() => navigate("/teacher/timetable")}
          color="purple"
        />

        <ActionButton
          label="View Attendance"
          onClick={() => navigate("/teacher/attendance")}
          color="orange"
        />
      </div>

      {/* Recent Attendance Logs */}
      <h2 className="text-xl font-semibold mb-3">Recent Attendance</h2>

      <div className="bg-white shadow rounded p-4">
        <table className="w-full text-left">
          <thead>
            <tr className="border-b">
              <th className="py-2">Student</th>
              <th className="py-2">Class</th>
              <th className="py-2">Time</th>
              <th className="py-2">Status</th>
            </tr>
          </thead>

          <tbody>
            {recent.length === 0 && (
              <tr>
                <td colSpan="4" className="py-4 text-center text-gray-500">
                  No attendance logs yet
                </td>
              </tr>
            )}

            {recent.map((log, index) => (
              <tr key={index} className="border-b hover:bg-gray-50">
                <td className="py-2">{log.name}</td>
                <td className="py-2">{log.class_name}</td>
                <td className="py-2">{log.time}</td>
                <td className="py-2">
                  <span className="px-2 py-1 bg-green-100 text-green-700 rounded text-sm">
                    Present
                  </span>
                </td>
              </tr>
            ))}
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
    blue: "bg-blue-600 hover:bg-blue-700",
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
