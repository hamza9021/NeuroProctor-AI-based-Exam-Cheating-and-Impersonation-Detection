import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { Register, Home } from "./Pages";

const App = () => {
    return (
        <Router>
            <Routes>
                <Route path="/register" element={<Register />} />
                <Route path="/" element={<Home />} />
            </Routes>
        </Router>
    );
};

export default App;
