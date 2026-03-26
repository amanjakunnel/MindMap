import React from "react";
import { useLocation, useNavigate } from "react-router-dom";
import Menu from "../components/Menu";
import FinalMindMapRender from "../components/FinalMindMapRender";

function MindMap() {
    const location = useLocation();
    const navigate = useNavigate();

    const history = JSON.parse(localStorage.getItem("wordieHistory") || "[]");
    const mapId = location.state?.mapId;
    const entry = mapId
        ? history.find(e => e.id === mapId)
        : history[0];

    if (!entry) {
        navigate("/");
        return null;
    }

    return (
        <div>
            <Menu />
            <FinalMindMapRender mapData={entry.data} />
        </div>
    );
}

export default MindMap;
