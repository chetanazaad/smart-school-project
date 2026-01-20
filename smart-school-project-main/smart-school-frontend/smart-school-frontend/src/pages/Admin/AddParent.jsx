// src/pages/Admin/AddParent.jsx

import React, { useState, useEffect } from "react";
import API from "../../services/api";
import { useNavigate } from "react-router-dom";

export default function AddParent() {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    id_code: "",
    name: "",
    email: "",
    phone: "",
    password: "",
    confirmPassword: "",
  });
  const [createdId, setCreatedId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const generateParentId = () => {
    const n = Math.floor(1000 + Math.random() * 9000);
    return `P${n}`;
  };

  useEffect(() => {
    if (!form.id_code) setForm((f) => ({ ...f, id_code: generateParentId() }));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    // Validation
    if (!form.name || !form.email || !form.password) {
      setError("Name, Email, and Password are required");
      return;
    }

    if (form.password.length < 6) {
      setError("Password must be at least 6 characters");
      return;
    }

    if (form.password !== form.confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    setLoading(true);
    try {
      // Create parent record and user account
      const createRes = await API.post("/parents", {
        id_code: form.id_code,
        name: form.name,
        email: form.email,
        phone: form.phone,
        password: form.password,
      });

      const parentId = createRes.data?.id;
      setCreatedId(parentId || null);

      // Show success and navigate
      setTimeout(() => {
        window.dispatchEvent(new CustomEvent("entityChanged"));
        navigate("/admin/parents");
      }, 500);
    } catch (err) {
      console.error("Add parent failed:", err);
      setError(err.response?.data?.error || "Failed to add parent. See console for details.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6">
      <h2 className="text-2xl font-semibold mb-5">Add Parent</h2>

      {error && (
        <div className="mb-4 p-4 bg-red-100 text-red-700 rounded border border-red-200">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4 max-w-md">

        <div className="flex items-center gap-2">
          <input
            name="id_code"
            placeholder="Parent ID (e.g. P1001)"
            value={form.id_code}
            onChange={handleChange}
            className="border p-3 rounded w-full"
          />
          <button 
            type="button" 
            onClick={() => setForm(f => ({...f, id_code: generateParentId()}))} 
            className="px-3 py-2 bg-gray-200 rounded"
          >
            New
          </button>
        </div>

        <input
          name="name"
          placeholder="Parent Name"
          value={form.name}
          onChange={handleChange}
          className="border p-3 rounded w-full"
          required
        />

        <input
          name="email"
          type="email"
          placeholder="Email"
          value={form.email}
          onChange={handleChange}
          className="border p-3 rounded w-full"
          required
        />

        <input
          name="phone"
          placeholder="Phone Number (Optional)"
          value={form.phone}
          onChange={handleChange}
          className="border p-3 rounded w-full"
        />

        <div className="bg-blue-50 p-4 rounded border border-blue-200">
          <h3 className="font-semibold text-blue-900 mb-3">Login Credentials</h3>
          
          <input
            name="password"
            type="password"
            placeholder="Password"
            value={form.password}
            onChange={handleChange}
            className="border p-3 rounded w-full mb-2"
            required
          />

          <input
            name="confirmPassword"
            type="password"
            placeholder="Confirm Password"
            value={form.confirmPassword}
            onChange={handleChange}
            className="border p-3 rounded w-full"
            required
          />
          <p className="text-sm text-gray-600 mt-2">Password must be at least 6 characters</p>
        </div>

        {createdId && (
          <div className="bg-green-50 p-3 rounded border border-green-200">
            <p className="text-green-700">
              Parent created successfully with ID: <strong>{createdId}</strong>
            </p>
          </div>
        )}

        <button
          type="submit"
          disabled={loading}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50 w-full"
        >
          {loading ? "Adding..." : "Add Parent"}
        </button>
      </form>
    </div>
  );
}
