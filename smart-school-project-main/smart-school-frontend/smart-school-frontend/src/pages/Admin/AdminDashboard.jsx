// src/pages/Admin/AdminDashboard.jsx

import React, { useEffect, useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import API from "../../services/api";
import { Pie } from "react-chartjs-2";
import Chart from "chart.js/auto";

export default function AdminDashboard() {
  const navigate = useNavigate();
  const { token } = useAuth();

  const [stats, setStats] = useState({
    students: 0,
    teachers: 0,
    today_attendance: 0,
    classes: 0,
    teachers_present: 0,
  });

  const [recent, setRecent] = useState([]);

  // Fetch Dashboard Summary
  const loadStats = useCallback(async () => {
    try {
      const s = await API.get(`/students/count`);
      const t = await API.get(`/teachers/count`);
      const a = await API.get(`/attendance/today`);
      const c = await API.get(`/students/class-count`);
      const tp = await API.get(`/attendance/teachers/today`);

      setStats({
        students: s.data.count || 0,
        teachers: t.data.count || 0,
        today_attendance: a.data.count || 0,
        classes: c.data.count || 0,
        teachers_present: tp.data.count || 0,
      });
    } catch (err) {
      console.error("Stats Error:", err);
    }
  }, []);

  // Fetch recent logs
  const loadRecent = useCallback(async () => {
    try {
      const r = await API.get(`/attendance-view/all?limit=5`);
      setRecent(r.data.records || []);
    } catch (err) {
      console.error("Recent logs error:", err);
    }
  }, []);

  useEffect(() => {
    if (token) {
      loadStats();
      loadRecent();
    }

    const handleEntityChanged = () => {
      console.log("Entity changed event received, reloading stats...");
      loadStats();
      loadRecent();
    };

    window.addEventListener("entityChanged", handleEntityChanged);

    return () => {
      window.removeEventListener("entityChanged", handleEntityChanged);
    };
  }, [token, loadStats, loadRecent]);

  return (
    <div className="p-4 md:p-6">

      {/* Header */}
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold">Admin Dashboard</h1>
        <button
          onClick={() => {
            loadStats();
            loadRecent();
          }}
          className="px-4 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300"
        >
          Refresh
        </button>
      </div>

      {/* Top Summary Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <SummaryCard title="Students" count={stats.students} color="blue" />
        <SummaryCard title="Teachers" count={stats.teachers} color="green" />
        <SummaryCard title="Today Present" count={stats.today_attendance} color="purple" />
        <SummaryCard title="Classes" count={stats.classes} color="orange" />
      </div>

      {/* Quick Actions */}
      <h2 className="text-xl font-semibold mb-2">Quick Actions</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">

        <ActionButton
          label="Mark Attendance"
          onClick={() => navigate("/admin/attendance")}
          color="blue"
        />

        <ActionButton
          label="Enroll Faces"
          onClick={() => navigate("/admin/students")}
          color="green"
        />

        <ActionButton
          label="View Records"
          onClick={() => navigate("/admin/attendance")}
          color="purple"
        />

        <ActionButton
          label="Add Student"
          onClick={() => navigate("/admin/students")}
          color="orange"
        />

      </div>
      {/* Present/Total Pie Charts */}
      <h2 className="text-xl font-semibold mb-3">Attendance Overview</h2>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white shadow rounded p-4">
          <h3 className="text-lg font-semibold mb-3">Students: Present / Total</h3>
          <Pie
            data={{
              labels: ["Present", "Absent"],
              datasets: [
                {
                  data: [stats.today_attendance, Math.max(0, stats.students - stats.today_attendance)],
                  backgroundColor: ["#34D399", "#E5E7EB"],
                },
              ],
            }}
          />
          <div className="mt-3 text-sm text-gray-600">{stats.today_attendance} present of {stats.students} students</div>
        </div>

        <div className="bg-white shadow rounded p-4">
          <h3 className="text-lg font-semibold mb-3">Teachers: Present / Total</h3>
          <Pie
            data={{
              labels: ["Present", "Absent"],
              datasets: [
                {
                  data: [stats.teachers_present, Math.max(0, stats.teachers - stats.teachers_present)],
                  backgroundColor: ["#60A5FA", "#E5E7EB"],
                },
              ],
            }}
          />
          <div className="mt-3 text-sm text-gray-600">{stats.teachers_present} present of {stats.teachers} teachers</div>
        </div>
      </div>

      <div className="mt-8">
        <h2 className="text-xl font-bold mb-4">Recent Attendance</h2>
        <div className="bg-white shadow rounded overflow-hidden">
          <table className="w-full text-left">
            <thead className="bg-gray-50 text-gray-600 uppercase text-xs font-semibold">
              <tr>
                <th className="px-4 py-3">Time</th>
                <th className="px-4 py-3">Name</th>
                <th className="px-4 py-3">ID</th>
                <th className="px-4 py-3">Role</th>
                <th className="px-4 py-3">Class</th>
                <th className="px-4 py-3">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {recent.length > 0 ? (
                recent.map((record, index) => (
                  <tr key={index} className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-sm">{record.time}</td>
                    <td className="px-4 py-3 text-sm font-medium">{record.name}</td>
                    <td className="px-4 py-3 text-sm text-gray-500">{record.full_id || record.id}</td>
                    <td className="px-4 py-3 text-sm capitalize">{record.type}</td>
                    <td className="px-4 py-3 text-sm">{record.class_name || "—"}</td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${record.status === 'present' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                        }`}>
                        {record.status}
                      </span>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="6" className="px-4 py-8 text-center text-gray-400">No logs found</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  );
}

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