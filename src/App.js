import './App.css';
import {BrowserRouter as Router, Route,Routes} from 'react-router-dom';
import Home from './pages/Home';
import React, { createRef, useEffect } from 'react';
import MindMap from './pages/MindMap';

export default function App() {
  return (
    <div>
      <Router>
        <Routes>
          <Route path="/" element={<Home />} /> 
          <Route path="/MindMap" element={<MindMap />} />
        </Routes>
      </Router>
    </div>
  )
}