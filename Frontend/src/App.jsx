import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { InvigilatorRegister, InvigilatorLogin, Home } from "./Pages";

const App = () => {
    return (
        <Router>
            <Routes>
                <Route
                    path="/invigilator/register"
                    element={<InvigilatorRegister />}
                />
                <Route
                    path="/invigilator/login"
                    element={<InvigilatorLogin />}
                />

                <Route path="/" element={<Home />} />
            </Routes>
        </Router>
    );
};

export default App;
