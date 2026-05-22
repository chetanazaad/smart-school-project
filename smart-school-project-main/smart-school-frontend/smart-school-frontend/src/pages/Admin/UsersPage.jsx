import { useEffect, useState } from "react";
import API from "../../services/api";

export default function UsersPage() {
    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    const fetchUsers = async () => {
        try {
            setLoading(true);
            const response = await API.get("/users");
            setUsers(response.data.users || []);
        } catch (err) {
            console.error("Error fetching users:", err);
            setError("Failed to load user accounts.");
        } finally {
            setLoading(false);
        }
    };

    const handleDelete = async (user_id, email) => {
        if (!window.confirm(`Are you sure you want to permanently delete the user account for ${email}? This action cannot be undone.`)) return;

        try {
            await API.delete(`/users/${user_id}`);
            fetchUsers();
        } catch (err) {
            console.error("Delete failed:", err);
            alert("Failed to delete user account.");
        }
    };

    useEffect(() => {
        fetchUsers();
    }, []);

    if (loading) return <div className="p-6 text-lg">Loading system accounts...</div>;

    const orphans = users.filter(u => u.is_orphan);

    return (
        <div className="p-6">
            <div className="flex justify-between items-center mb-6">
                <div>
                    <h2 className="text-2xl font-semibold">System Accounts ({users.length})</h2>
                    <p className="text-gray-500 text-sm mt-1">Manage all login credentials, including orphaned accounts.</p>
                </div>
                <button
                    onClick={fetchUsers}
                    className="bg-gray-200 text-gray-700 px-4 py-2 rounded hover:bg-gray-300"
                >
                    Refresh
                </button>
            </div>

            {error && (
                <div className="mb-4 p-4 bg-red-100 text-red-700 rounded border border-red-200">
                    {error}
                </div>
            )}

            {orphans.length > 0 && (
                <div className="mb-6 p-4 bg-amber-50 border border-amber-200 rounded-lg">
                    <h3 className="text-amber-800 font-bold flex items-center gap-2">
                        ⚠️ Found {orphans.length} Orphaned Account(s)
                    </h3>
                    <p className="text-amber-700 text-sm mt-1">
                        These accounts exist in the login system but have no matching Student or Teacher record. They may be left over from failed deletions.
                    </p>
                </div>
            )}

            <div className="overflow-x-auto bg-white rounded-lg shadow">
                <table className="w-full border-collapse">
                    <thead>
                        <tr className="bg-gray-50 border-b">
                            <th className="p-4 text-left font-semibold text-gray-600">Name</th>
                            <th className="p-4 text-left font-semibold text-gray-600">Email / Login</th>
                            <th className="p-4 text-left font-semibold text-gray-600">Role</th>
                            <th className="p-4 text-left font-semibold text-gray-600">Status</th>
                            <th className="p-4 text-center font-semibold text-gray-600">Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {users.map((u) => (
                            <tr key={u.id} className="border-b hover:bg-gray-50 animate-fadeIn">
                                <td className="p-4">
                                    <div className="font-medium text-gray-800">{u.name || "—"}</div>
                                    <div className="text-xs text-gray-400">ID: {u.id}</div>
                                </td>
                                <td className="p-4 text-gray-600 font-mono text-sm">{u.email}</td>
                                <td className="p-4">
                                    <span className={`px-2 py-1 rounded-full text-xs font-semibold uppercase ${u.role === 'admin' ? 'bg-purple-100 text-purple-700' :
                                            u.role === 'teacher' ? 'bg-green-100 text-green-700' :
                                                'bg-blue-100 text-blue-700'
                                        }`}>
                                        {u.role}
                                    </span>
                                </td>
                                <td className="p-4">
                                    {u.is_orphan ? (
                                        <span className="flex items-center gap-1 text-red-600 text-xs font-bold">
                                            Orphaned
                                        </span>
                                    ) : (
                                        <span className="text-green-600 text-xs font-medium">Link Active</span>
                                    )}
                                </td>
                                <td className="p-4 text-center">
                                    <button
                                        onClick={() => handleDelete(u.id, u.email)}
                                        className="text-red-600 hover:text-red-900 font-medium text-sm transition-colors"
                                    >
                                        Permanently Delete
                                    </button>
                                </td>
                            </tr>
                        ))}
                        {users.length === 0 && (
                            <tr>
                                <td colSpan="5" className="p-8 text-center text-gray-400">
                                    No accounts found in system.
                                </td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </div>

            <div className="mt-6 text-sm text-gray-500 bg-gray-50 p-4 rounded border border-dashed">
                <h4 className="font-semibold mb-1">💡 Pro-Tip for Admin:</h4>
                <p>If you see an "Orphaned" account, it means the login exists but the profile (Student/Teacher data) is missing. You can delete these here to clean up the database and allow re-registration with the same email.</p>
            </div>
        </div>
    );
}
