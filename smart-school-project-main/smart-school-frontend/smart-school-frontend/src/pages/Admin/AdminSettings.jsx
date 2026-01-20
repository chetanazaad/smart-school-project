// src/pages/Admin/AdminSettings.jsx

import React, { useState, useEffect } from "react";
import { useAuth } from "../../context/AuthContext";
import API from "../../services/api";

export default function AdminSettings() {
  const { user } = useAuth();
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  // Email Update State
  const [showEmailForm, setShowEmailForm] = useState(false);
  const [newEmail, setNewEmail] = useState("");

  // Password Update State
  const [showPasswordForm, setShowPasswordForm] = useState(false);
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  // Load current user info
  useEffect(() => {
    if (user) {
      setNewEmail(user.email || "");
    }
  }, [user]);

  // Handle Email Update
  const handleEmailUpdate = async () => {
    setError("");
    setMessage("");

    if (!newEmail) {
      setError("Email cannot be empty");
      return;
    }

    if (newEmail === user.email) {
      setError("New email must be different from current email");
      return;
    }

    setLoading(true);
    try {
      const response = await API.post("/auth/update-email", {
        new_email: newEmail,
      });

      setMessage("Email updated successfully!");
      setTimeout(() => {
        window.location.reload();
      }, 1500);
    } catch (err) {
      setError(err.response?.data?.error || "Failed to update email");
    } finally {
      setLoading(false);
    }
  };

  // Handle Password Update
  const handlePasswordUpdate = async () => {
    setError("");
    setMessage("");

    if (!currentPassword || !newPassword || !confirmPassword) {
      setError("All fields are required");
      return;
    }

    if (newPassword !== confirmPassword) {
      setError("New passwords do not match");
      return;
    }

    if (newPassword.length < 6) {
      setError("New password must be at least 6 characters");
      return;
    }

    if (currentPassword === newPassword) {
      setError("New password must be different from current password");
      return;
    }

    setLoading(true);
    try {
      const response = await API.post("/auth/update-password", {
        current_password: currentPassword,
        new_password: newPassword,
      });

      setMessage("Password updated successfully!");
      setCurrentPassword("");
      setNewPassword("");
      setConfirmPassword("");
      setShowPasswordForm(false);

      setTimeout(() => {
        window.location.reload();
      }, 1500);
    } catch (err) {
      setError(err.response?.data?.error || "Failed to update password");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-4 md:p-6">
      <h1 className="text-3xl font-bold mb-6">Settings</h1>

      {/* Alert Messages */}
      {message && (
        <div className="mb-4 p-4 bg-green-100 text-green-700 rounded-lg border border-green-200">
          ✓ {message}
        </div>
      )}

      {error && (
        <div className="mb-4 p-4 bg-red-100 text-red-700 rounded-lg border border-red-200">
          ✗ {error}
        </div>
      )}

      {/* Profile Information */}
      <div className="bg-white shadow rounded-lg p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4">Profile Information</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Name
            </label>
            <input
              type="text"
              value={user?.name || ""}
              disabled
              className="w-full px-4 py-2 bg-gray-100 text-gray-600 rounded border border-gray-300"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Role
            </label>
            <input
              type="text"
              value={user?.role || ""}
              disabled
              className="w-full px-4 py-2 bg-gray-100 text-gray-600 rounded border border-gray-300"
            />
          </div>
        </div>
      </div>

      {/* Email Update Section */}
      <div className="bg-white shadow rounded-lg p-6 mb-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">Change Email</h2>
          <button
            onClick={() => {
              setShowEmailForm(!showEmailForm);
              setError("");
              setMessage("");
            }}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition"
          >
            {showEmailForm ? "Cancel" : "Change Email"}
          </button>
        </div>

        {showEmailForm && (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Current Email
              </label>
              <input
                type="email"
                value={user?.email || ""}
                disabled
                className="w-full px-4 py-2 bg-gray-100 text-gray-600 rounded border border-gray-300"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                New Email
              </label>
              <input
                type="email"
                value={newEmail}
                onChange={(e) => setNewEmail(e.target.value)}
                placeholder="Enter new email"
                className="w-full px-4 py-2 rounded border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <button
              onClick={handleEmailUpdate}
              disabled={loading}
              className="px-6 py-2 bg-green-600 text-white rounded hover:bg-green-700 transition disabled:opacity-50"
            >
              {loading ? "Updating..." : "Update Email"}
            </button>
          </div>
        )}
      </div>

      {/* Password Update Section */}
      <div className="bg-white shadow rounded-lg p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">Change Password</h2>
          <button
            onClick={() => {
              setShowPasswordForm(!showPasswordForm);
              setError("");
              setMessage("");
              setCurrentPassword("");
              setNewPassword("");
              setConfirmPassword("");
            }}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition"
          >
            {showPasswordForm ? "Cancel" : "Change Password"}
          </button>
        </div>

        {showPasswordForm && (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Current Password
              </label>
              <input
                type="password"
                value={currentPassword}
                onChange={(e) => setCurrentPassword(e.target.value)}
                placeholder="Enter current password"
                className="w-full px-4 py-2 rounded border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                New Password
              </label>
              <input
                type="password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                placeholder="Enter new password"
                className="w-full px-4 py-2 rounded border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Confirm New Password
              </label>
              <input
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="Confirm new password"
                className="w-full px-4 py-2 rounded border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <button
              onClick={handlePasswordUpdate}
              disabled={loading}
              className="px-6 py-2 bg-green-600 text-white rounded hover:bg-green-700 transition disabled:opacity-50"
            >
              {loading ? "Updating..." : "Update Password"}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
