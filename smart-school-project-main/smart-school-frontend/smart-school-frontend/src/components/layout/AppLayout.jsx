import { useState } from "react";
import Sidebar from "./Sidebar";
import Navbar from "./Navbar";
import {
  FiHome,
  FiUsers,
  FiUserPlus,
  FiBookOpen,
  FiCamera,
  FiClipboard,
  FiPieChart,
  FiMessageCircle,
  FiUpload,
  FiSettings,
} from "react-icons/fi";

const AppLayout = ({ children }) => {
  const [isSidebarOpen, setSidebarOpen] = useState(true);

  const adminMenu = [
    { label: "Dashboard", path: "/admin/dashboard", icon: <FiHome /> },
    { section: "Attendance" },
    { label: "Attendance Records", path: "/admin/attendance", icon: <FiClipboard /> },
    { section: "Management" },
    { label: "Students", path: "/admin/students", icon: <FiUsers /> },
    { label: "Teachers", path: "/admin/teachers", icon: <FiUsers /> },
    { label: "Parents", path: "/admin/parents", icon: <FiUsers /> },
    { section: "Academics" },
    { label: "Timetable", path: "/admin/timetable", icon: <FiBookOpen /> },
    { section: "AI" },
    { label: "AI Reports", path: "/admin/ai-reports", icon: <FiPieChart /> },
    { section: "Chat" },
    { label: "Chatbot", path: "/chatbot", icon: <FiMessageCircle /> },
    { section: "Account" },
    { label: "Settings", path: "/admin/settings", icon: <FiSettings /> },
  ];

  const teacherMenu = [
    { label: "Dashboard", path: "/teacher/dashboard", icon: <FiHome /> },
    { section: "Attendance" },
    { label: "Attendance Records", path: "/teacher/attendance", icon: <FiClipboard /> },
    { section: "Students" },
    { label: "Enroll Student", path: "/teacher/add-student", icon: <FiUserPlus /> },
    { section: "Academics" },
    { label: "Class Timetable", path: "/teacher/timetable", icon: <FiBookOpen /> },
    { label: "Upload Notes", path: "/teacher/upload-notes", icon: <FiUpload /> },
    { section: "AI" },
    { label: "AI Tutor Reports", path: "/teacher/ai-reports", icon: <FiPieChart /> },
    { section: "Chat" },
    { label: "Chatbot", path: "/chatbot", icon: <FiMessageCircle /> },
  ];

  const studentMenu = [
    { label: "Dashboard", path: "/student/dashboard", icon: <FiHome /> },
    { section: "Attendance" },
    { label: "My Attendance", path: "/student/my-attendance", icon: <FiClipboard /> },
    { section: "Academics" },
    { label: "My Timetable", path: "/student/timetable", icon: <FiBookOpen /> },
    { section: "Chat" },
    { label: "Chatbot", path: "/chatbot", icon: <FiMessageCircle /> },
  ];

  const parentMenu = [
    { label: "Dashboard", path: "/parent/dashboard", icon: <FiHome /> },
    { label: "Performance", path: "/parent/performance", icon: <FiPieChart /> },
    { label: "Chatbot", path: "/chatbot", icon: <FiMessageCircle /> },
  ];

  return (
    <div className="flex h-screen bg-gray-100">
      <Sidebar
        isOpen={isSidebarOpen}
        adminMenu={adminMenu}
        teacherMenu={teacherMenu}
        studentMenu={studentMenu}
        parentMenu={parentMenu}
      />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Navbar toggleSidebar={() => setSidebarOpen(!isSidebarOpen)} />
        <main className="flex-1 overflow-x-hidden overflow-y-auto bg-gray-100 p-4">
          {children}
        </main>
      </div>
    </div>
  );
};

export default AppLayout;