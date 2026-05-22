import React, { useState } from "react";
import RecognitionCamera from "../../components/RecognitionCamera";
import { recognizeFace } from "../../services/api";

export default function FaceRecognitionPage() {
    const [role, setRole] = useState("student");
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);

    // When camera captures frame
    const handleFrameCapture = async (imageData) => {
        if (!imageData) return;

        setLoading(true);

        try {
                const res = await recognizeFace({ image_base64: imageData });
                // `recognizeFace` returns an axios response promise; take `.data`
                setResult(res.data);
        } catch (err) {
            console.error("Recognition error:", err);
            setResult({
                status: "error",
                message: "Recognition failed. Try again.",
            });
        }

        setLoading(false);
    };

    return (
        <div className="container mt-4">
            <h2>Face Recognition</h2>

            <div className="mt-3">
                <label>Select Role:</label>
                <select
                    className="form-control"
                    value={role}
                    onChange={(e) => setRole(e.target.value)}
                >
                    <option value="student">Student</option>
                    <option value="teacher">Teacher</option>
                </select>
            </div>

            <RecognitionCamera onFrameCapture={handleFrameCapture} />

            {loading && <p>Recognizing… please wait</p>}

            {result && (
                <div className="alert alert-info mt-3">
                    <strong>Status:</strong> {result.status} <br />
                    {result.message && (
                        <>
                            <strong>Message:</strong> {result.message} <br />
                        </>
                    )}

                    {result.matched && (
                        <>
                            <strong>Matched:</strong> {result.matched} <br />
                            <strong>ID:</strong> {result.user_id} <br />
                            <strong>Name:</strong> {result.name} <br />
                            {result.class && (
                                <>
                                    <strong>Class:</strong> {result.class}
                                    <br />
                                </>
                            )}
                            {result.subject && (
                                <>
                                    <strong>Subject:</strong> {result.subject}
                                    <br />
                                </>
                            )}
                            {result.attendance_marked && (
                                <strong>Attendance Marked Automatically</strong>
                            )}
                        </>
                    )}
                </div>
            )}
        </div>
    );
}
