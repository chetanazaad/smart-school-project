// src/pages/Admin/ParentsPage.jsx

import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import API from "../../services/api";

export default function ParentsPage() {
  const navigate = useNavigate();
  const [parents, setParents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    loadParents();

    const handleEntityChanged = () => {
      loadParents();
    };

    window.addEventListener("entityChanged", handleEntityChanged);
    return () => window.removeEventListener("entityChanged", handleEntityChanged);
  }, []);

  const loadParents = async () => {
    try {
      setLoading(true);
      const response = await API.get("/parents");
      setParents(response.data.parents || []);
      setError("");
    } catch (err) {
      console.error("Failed to load parents:", err);
      setError("Failed to load parents");
      setParents([]);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm("Are you sure you want to delete this parent?")) {
      try {
        await API.delete(`/parents/${id}`);
        setParents(parents.filter(p => p.id !== id));
        window.dispatchEvent(new CustomEvent("entityChanged"));
      } catch (err) {
        console.error("Failed to delete parent:", err);
        setError("Failed to delete parent");
      }
    }
  };

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-semibold">Parents Management</h2>
        <button
          onClick={() => navigate("/admin/add-parent")}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          + Add Parent
        </button>
      </div>

      {error && (
        <div className="mb-4 p-4 bg-red-100 text-red-700 rounded border border-red-200">
          {error}
        </div>
      )}

      {loading ? (
        <div className="text-center py-8">
          <p className="text-gray-500">Loading...</p>
        </div>
      ) : parents.length === 0 ? (
        <div className="text-center py-8 bg-white rounded shadow">
          <p className="text-gray-500">No parents added yet</p>
          <button
            onClick={() => navigate("/admin/add-parent")}
            className="mt-4 bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
          >
            Add First Parent
          </button>
        </div>
      ) : (
        <div className="bg-white rounded shadow overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-100 border-b">
              <tr>
                <th className="px-6 py-3 text-left text-sm font-semibold">ID</th>
                <th className="px-6 py-3 text-left text-sm font-semibold">Name</th>
                <th className="px-6 py-3 text-left text-sm font-semibold">Email</th>
                <th className="px-6 py-3 text-left text-sm font-semibold">Phone</th>
                <th className="px-6 py-3 text-left text-sm font-semibold">ID Code</th>
                <th className="px-6 py-3 text-left text-sm font-semibold">Actions</th>
              </tr>
            </thead>
            <tbody>
              {parents.map((parent) => (
                <tr key={parent.id} className="border-b hover:bg-gray-50">
                  <td className="px-6 py-3 text-sm">{parent.id}</td>
                  <td className="px-6 py-3 text-sm">{parent.name}</td>
                  <td className="px-6 py-3 text-sm">{parent.email}</td>
                  <td className="px-6 py-3 text-sm">{parent.phone || "-"}</td>
                  <td className="px-6 py-3 text-sm font-mono text-blue-600">{parent.id_code}</td>
                  <td className="px-6 py-3 text-sm">
                    <button
                      onClick={() => handleDelete(parent.id)}
                      className="text-red-600 hover:text-red-800 font-medium"
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
