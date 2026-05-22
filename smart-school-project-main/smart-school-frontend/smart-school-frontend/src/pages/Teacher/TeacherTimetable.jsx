import { useEffect, useState } from "react";
import { useAuth } from "../../context/AuthContext";
import API from "../../services/api";

export default function TeacherTimetable() {
  const { user } = useAuth();
  const [personalTimetable, setPersonalTimetable] = useState([]);
  const [classTimetable, setClassTimetable] = useState([]);
  const [teacherDetails, setTeacherDetails] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    if (!user?.id) return;

    try {
      setLoading(true);

      // Fetch teacher details to get assigned class info
      const teacherRes = await API.get(`/teachers/${user.id}`);
      setTeacherDetails(teacherRes.data);

      // Fetch personal timetable
      const personalRes = await API.get(`/timetable/teacher/${user.id}/week`);
      setPersonalTimetable(personalRes.data.timetable || []);

      // Fetch class timetable if class teacher
      if (teacherRes.data.is_class_teacher && teacherRes.data.assigned_class) {
        const classRes = await API.get(`/timetable/${teacherRes.data.assigned_class}/${teacherRes.data.assigned_section || 'A'}`);
        setClassTimetable(classRes.data.timetable || []);
      }
    } catch (err) {
      console.error("Error fetching timetable:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [user]);

  if (loading) {
    return (
      <div className="p-6">
        <div className="text-center py-8">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <p className="mt-2 text-gray-600">Loading timetable...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <h2 className="text-2xl font-semibold mb-4">My Timetable</h2>

      {/* Personal Timetable */}
      <div className="mb-8">
        <h3 className="text-xl font-semibold mb-3">My Classes</h3>
        <div className="bg-white shadow rounded-lg overflow-hidden">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Day</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Class</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Subject</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Time</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {personalTimetable.length === 0 ? (
                <tr>
                  <td colSpan="4" className="px-6 py-4 text-center text-gray-500">
                    No classes scheduled
                  </td>
                </tr>
              ) : (
                personalTimetable.map((t) => (
                  <tr key={t.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{t.day}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {t.class_name}{t.section}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{t.subject}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {t.start_time} - {t.end_time}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Class Timetable for Class Teachers */}
      {teacherDetails?.is_class_teacher && (
        <div>
          <h3 className="text-xl font-semibold mb-3">
            Class {teacherDetails.assigned_class} - Section {teacherDetails.assigned_section || 'A'} Timetable
          </h3>
          <div className="bg-white shadow rounded-lg overflow-hidden">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Day</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Subject</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Teacher</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Time</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {classTimetable.length === 0 ? (
                  <tr>
                    <td colSpan="4" className="px-6 py-4 text-center text-gray-500">
                      No class schedule available
                    </td>
                  </tr>
                ) : (
                  classTimetable.map((t) => (
                    <tr key={t.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{t.day}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{t.subject}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{t.teacher_name}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {t.start_time} - {t.end_time}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
