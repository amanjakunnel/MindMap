import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";

function FileUploader() {
    const [file, setFile] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const navigate = useNavigate();

    function handleChange(e) {
        setFile(e.target.files[0]);
        setError("");
    }

    async function handleSubmit() {
        if (!file) {
            setError("Please select a file first.");
            return;
        }

        const formData = new FormData();
        formData.append("file", file);

        setLoading(true);
        setError("");

        try {
            const response = await axios.post("http://localhost:5002/saveDoc", formData, {
                headers: { "Content-Type": "multipart/form-data" },
            });
            const newEntry = {
                id: Date.now().toString(),
                filename: file.name,
                createdAt: new Date().toISOString(),
                data: response.data,
            };
            const existing = JSON.parse(localStorage.getItem("wordieHistory") || "[]");
            const deduplicated = existing.filter(e => e.filename !== newEntry.filename);
            const updated = [newEntry, ...deduplicated].slice(0, 5);
            localStorage.setItem("wordieHistory", JSON.stringify(updated));
            navigate("/MindMap", { state: { mapId: newEntry.id } });
        } catch (err) {
            setError("Failed to process file. Make sure the server is running.");
        } finally {
            setLoading(false);
        }
    }

    return (
        <div className="fileUploaderWrapper">
            <label className="fileDropZone">
                <input
                    type="file"
                    accept=".docx,.pdf,.txt"
                    onChange={handleChange}
                    style={{ display: 'none' }}
                />
                <span className="fileDropIcon">📄</span>
                <span className="fileDropText">
                    {file ? file.name : 'Click to choose a file'}
                </span>
                <span className="fileDropHint">.docx, .pdf, or .txt</span>
            </label>
            <button className="generateBtn" onClick={handleSubmit} disabled={loading}>
                {loading ? "Processing..." : "Generate Mind Map"}
            </button>
            {error && <p className="uploadError">{error}</p>}
        </div>
    );
}

export default FileUploader;
