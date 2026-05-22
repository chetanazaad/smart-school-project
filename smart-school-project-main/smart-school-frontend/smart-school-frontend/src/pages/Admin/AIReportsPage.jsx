// src/pages/Admin/AIReportsPage.jsx
import { useEffect, useState, useCallback } from "react";
import API from "../../services/api";

export default function AIReportsPage() {
  const [students, setStudents] = useState([]);
  const [teachers, setTeachers] = useState([]);
  const [attendance, setAttendance] = useState([]);
  const [timetable, setTimetable] = useState([]);

  const [loading, setLoading] = useState(true);

  const loadData = useCallback(async () => {
    try {
      const s = await API.get("/students");
      const t = await API.get("/teachers");
      const a = await API.get("/attendance");
      const ti = await API.get("/timetable");

      setStudents(s.data.students || []);
      setTeachers(t.data.teachers || []);
      setAttendance(a.data.attendance || []);
      setTimetable(ti.data.timetable || []);

      setLoading(false);
    } catch (err) {
      console.error("Error loading AI summary:", err);
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  if (loading) return <div className="p-6 text-xl">Loading analytics...</div>;

  // ===========================
  // 📊 BASIC CALCULATIONS
  // ===========================

  const totalStudents = students.length;
  const totalTeachers = teachers.length;
  const totalAttendance = attendance.length;
  const totalTimetable = timetable.length;

  const presentCount = attendance.filter((x) => x.status === "Present").length;
  const absentCount = attendance.filter((x) => x.status === "Absent").length;

  const attendanceRate =
    totalAttendance === 0
      ? 0
      : Math.round((presentCount / totalAttendance) * 100);

  // Class distribution
  const classDistribution = {};
  students.forEach((s) => {
    classDistribution[s.class_name] =
      (classDistribution[s.class_name] || 0) + 1;
  });

  const classList = Object.entries(classDistribution);

  // Timetable distribution (per class)
  const classTimetableCount = {};
  timetable.forEach((t) => {
    classTimetableCount[t.class_name] =
      (classTimetableCount[t.class_name] || 0) + 1;
  });

  // AI-style insights (static logic)
  const insights = [];

  if (attendanceRate < 70) {
    insights.push("⚠ Attendance rate is below 70%. Consider interventions.");
  } else {
    insights.push("✔ Attendance rate is healthy.");
  }

  const mostLoadedClass = classList.sort(
    (a, b) => b[1] - a[1]
  )[0]?.[0];

  if (mostLoadedClass) {
    insights.push(`ℹ Class ${mostLoadedClass} has the highest student count.`);
  }

  if (teachers.length < students.length / 20) {
    insights.push("⚠ Teacher-student ratio is low. Consider hiring.");
  }

  return (
    <div className="p-8">
      <h1 className="text-3xl font-semibold mb-6">AI Reports Dashboard</h1>

      {/* SUMMARY CARDS */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-10">
        <Card title="Total Students" value={totalStudents} />
        <Card title="Total Teachers" value={totalTeachers} />
        <Card title="Attendance Entries" value={totalAttendance} />
        <Card title="Timetable Entries" value={totalTimetable} />
      </div>

      {/* ATTENDANCE ANALYSIS */}
      <SectionTitle text="Attendance Overview" />
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
        <Card title="Present Count" value={presentCount} />
        <Card title="Absent Count" value={absentCount} />
        <Card title="Attendance Rate" value={attendanceRate + "%"} />
      </div>

      {/* CLASS DISTRIBUTION */}
      <SectionTitle text="Class-wise Student Distribution" />
      <div className="bg-white shadow p-4 rounded mb-10">
        {classList.map(([className, count]) => (
          <p key={className} className="text-gray-700">
            {className}: <b>{count}</b> students
          </p>
        ))}
      </div>

      {/* INSIGHTS */}
      <SectionTitle text="AI Insights & Recommendations" />
      <div className="bg-blue-50 border border-blue-200 p-4 rounded">
        {insights.map((msg, i) => (
          <p key={i} className="text-blue-700 mb-2">
            {msg}
          </p>
        ))}
      </div>
    </div>
  );
}

// --------------------
// 📌 Helper Components
// --------------------

function Card({ title, value }) {
  return (
    <div className="bg-white p-6 rounded shadow text-center">
      <p className="text-gray-600">{title}</p>
      <h2 className="text-2xl font-bold mt-2">{value}</h2>
    </div>
  );
}

function SectionTitle({ text }) {
  return <h2 className="text-xl font-semibold mb-4 mt-6">{text}</h2>;
}
