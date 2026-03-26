import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import Menu from "../components/Menu";

function formatDate(iso) {
    return new Date(iso).toLocaleDateString("en-US", {
        month: "short",
        day: "numeric",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit",
    });
}

function History() {
    const navigate = useNavigate();
    const [entries, setEntries] = useState(() =>
        JSON.parse(localStorage.getItem("wordieHistory") || "[]")
    );

    function handleDelete(id) {
        const updated = entries.filter(e => e.id !== id);
        localStorage.setItem("wordieHistory", JSON.stringify(updated));
        setEntries(updated);
    }

    return (
        <div>
            <Menu />
            <div className="historyContainer">
                <h1 className="historyTitle">Your Mind Maps</h1>
                {entries.length === 0 ? (
                    <p className="historyEmpty">
                        No mind maps yet. Upload a file on the home page to get started.
                    </p>
                ) : (
                    <div className="historyList">
                        {entries.map((entry, index) => (
                            <div key={entry.id} className="historyCard">
                                <div className="historyCardLeft">
                                    <span className="historyCardFilename">{entry.filename}</span>
                                    <span className="historyCardDate">{formatDate(entry.createdAt)}</span>
                                </div>
                                <div className="historyCardActions">
                                    <button
                                        className="historyViewBtn"
                                        onClick={() => navigate("/MindMap", { state: { mapId: entry.id } })}
                                    >
                                        View
                                    </button>
                                    <button
                                        className="historyDeleteBtn"
                                        onClick={() => handleDelete(entry.id)}
                                        title="Delete"
                                    >
                                        ✕
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}

export default History;
