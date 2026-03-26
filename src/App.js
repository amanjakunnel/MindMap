import './App.css';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import React from 'react';
import Home from './pages/Home';
import MindMap from './pages/MindMap';
import History from './pages/History';

export default function App() {
  return (
    <div>
      <Router>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/MindMap" element={<MindMap />} />
          <Route path="/History" element={<History />} />
        </Routes>
      </Router>
    </div>
  )
}