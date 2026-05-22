// src/routes/AppRoutes.jsx
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "../context/AuthContext";
import ProtectedRoute from "./ProtectedRoute";
import AppLayout from "../components/layout/AppLayout";

/* LOGIN */
import LoginPage from "../pages/Login/LoginPage";

/* ADMIN */
import AdminDashboard from "../pages/Admin/AdminDashboard";
import AdminSettings from "../pages/Admin/AdminSettings";
import StudentsPage from "../pages/Admin/StudentsPage";
import AddStudent from "../pages/Admin/AddStudent";
import EditStudent from "../pages/Admin/EditStudent";
import TeachersPage from "../pages/Admin/TeachersPage";
import AddTeacher from "../pages/Admin/AddTeacher";
import EditTeacher from "../pages/Admin/EditTeacher";
import ParentsPage from "../pages/Admin/ParentsPage";
import AddParent from "../pages/Admin/AddParent";
import TimetablePage from "../pages/Admin/TimetablePage";
import AddTimetable from "../pages/Admin/AddTimetable";
import EditTimetable from "../pages/Admin/EditTimetable";
import AdminAttendancePage from "../pages/Admin/AdminAttendancePage";
import AIReportsPage from "../pages/Admin/AIReportsPage";
import UsersPage from "../pages/Admin/UsersPage";


/* TEACHER */
import TeacherDashboard from "../pages/Teacher/TeacherDashboard";
import TeacherTimetable from "../pages/Teacher/TeacherTimetable";
import TeacherEnrollStudent from "../pages/Teacher/TeacherEnrollStudent";
import TeacherAttendancePage from "../pages/Teacher/TeacherAttendancePage";
import UploadNotesPage from "../pages/Teacher/UploadNotesPage";
import TeacherAiReportsPage from "../pages/Teacher/TeacherAiReportsPage";
import ClassTeacherStudents from "../pages/Teacher/ClassTeacherStudents";

/* STUDENT */
import StudentDashboard from "../pages/Student/StudentDashboard";
import StudentTimetable from "../pages/Student/StudentTimetable";
import StudentAttendancePage from "../pages/Student/StudentAttendancePage";

/* PARENT */
import ParentDashboard from "../pages/Parent/ParentDashboard";
import ParentPerformance from "../pages/Parent/ParentPerformance";



export default function AppRoutes() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>

          {/* DEFAULT REDIRECT */}
          <Route path="/" element={<Navigate to="/login" replace />} />
          <Route path="/login" element={<LoginPage />} />

          {/* ---------------- ADMIN ROUTES ---------------- */}

          <Route
            path="/admin/dashboard"
            element={
              <ProtectedRoute allowedRoles={["admin"]}>
                <AppLayout><AdminDashboard /></AppLayout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/admin/settings"
            element={
              <ProtectedRoute allowedRoles={["admin"]}>
                <AppLayout><AdminSettings /></AppLayout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/admin/attendance"
            element={
              <ProtectedRoute allowedRoles={["admin"]}>
                <AppLayout><AdminAttendancePage /></AppLayout>
              </ProtectedRoute>
            }
          />

          {/* face-enrollment route removed — enrollment is done via Add pages */}

          <Route
            path="/admin/students"
            element={
              <ProtectedRoute allowedRoles={["admin"]}>
                <AppLayout><StudentsPage /></AppLayout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/admin/add-student"
            element={
              <ProtectedRoute allowedRoles={["admin"]}>
                <AppLayout><AddStudent /></AppLayout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/admin/edit-student/:id"
            element={
              <ProtectedRoute allowedRoles={["admin"]}>
                <AppLayout><EditStudent /></AppLayout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/admin/teachers"
            element={
              <ProtectedRoute allowedRoles={["admin"]}>
                <AppLayout><TeachersPage /></AppLayout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/admin/add-teacher"
            element={
              <ProtectedRoute allowedRoles={["admin"]}>
                <AppLayout><AddTeacher /></AppLayout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/admin/edit-teacher/:id"
            element={
              <ProtectedRoute allowedRoles={["admin"]}>
                <AppLayout><EditTeacher /></AppLayout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/admin/parents"
            element={
              <ProtectedRoute allowedRoles={["admin"]}>
                <AppLayout><ParentsPage /></AppLayout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/admin/add-parent"
            element={
              <ProtectedRoute allowedRoles={["admin"]}>
                <AppLayout><AddParent /></AppLayout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/admin/timetable"
            element={
              <ProtectedRoute allowedRoles={["admin"]}>
                <AppLayout><TimetablePage /></AppLayout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/admin/add-timetable"
            element={
              <ProtectedRoute allowedRoles={["admin"]}>
                <AppLayout><AddTimetable /></AppLayout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/admin/edit-timetable/:id"
            element={
              <ProtectedRoute allowedRoles={["admin"]}>
                <AppLayout><EditTimetable /></AppLayout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/admin/ai-reports"
            element={
              <ProtectedRoute allowedRoles={["admin"]}>
                <AppLayout><AIReportsPage /></AppLayout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/admin/users"
            element={
              <ProtectedRoute allowedRoles={["admin"]}>
                <AppLayout><UsersPage /></AppLayout>
              </ProtectedRoute>
            }
          />


          {/* ---------------- TEACHER ROUTES ---------------- */}

          <Route
            path="/teacher/dashboard"
            element={
              <ProtectedRoute allowedRoles={["teacher"]}>
                <AppLayout><TeacherDashboard /></AppLayout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/teacher/timetable"
            element={
              <ProtectedRoute allowedRoles={["teacher"]}>
                <AppLayout><TeacherTimetable /></AppLayout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/teacher/add-student"
            element={
              <ProtectedRoute allowedRoles={["teacher"]}>
                <AppLayout><TeacherEnrollStudent /></AppLayout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/teacher/attendance"
            element={
              <ProtectedRoute allowedRoles={["teacher"]}>
                <AppLayout><TeacherAttendancePage /></AppLayout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/teacher/upload-notes"
            element={
              <ProtectedRoute allowedRoles={["teacher"]}>
                <AppLayout><UploadNotesPage /></AppLayout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/teacher/ai-reports"
            element={
              <ProtectedRoute allowedRoles={["teacher"]}>
                <AppLayout><TeacherAiReportsPage /></AppLayout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/teacher/students"
            element={
              <ProtectedRoute allowedRoles={["teacher"]}>
                <AppLayout><ClassTeacherStudents /></AppLayout>
              </ProtectedRoute>
            }
          />

          {/* ---------------- STUDENT ROUTES ---------------- */}

          <Route
            path="/student/dashboard"
            element={
              <ProtectedRoute allowedRoles={["student"]}>
                <AppLayout><StudentDashboard /></AppLayout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/student/timetable"
            element={
              <ProtectedRoute allowedRoles={["student"]}>
                <AppLayout><StudentTimetable /></AppLayout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/student/my-attendance"
            element={
              <ProtectedRoute allowedRoles={["student"]}>
                <AppLayout><StudentAttendancePage /></AppLayout>
              </ProtectedRoute>
            }
          />

          {/* ---------------- PARENT ROUTES ---------------- */}

          <Route
            path="/parent/dashboard"
            element={
              <ProtectedRoute allowedRoles={["parent"]}>
                <AppLayout><ParentDashboard /></AppLayout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/parent/performance"
            element={
              <ProtectedRoute allowedRoles={["parent"]}>
                <AppLayout><ParentPerformance /></AppLayout>
              </ProtectedRoute>
            }
          />



          {/* FALLBACK */}
          <Route path="*" element={<Navigate to="/login" replace />} />

        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}
