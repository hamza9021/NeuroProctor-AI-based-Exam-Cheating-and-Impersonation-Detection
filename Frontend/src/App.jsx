import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import {
    InvigilatorRegister,
    InvigilatorLogin,
    AdminLogin,
    AdminRegister,
    Home,
} from "./Pages";

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
                <Route path="/admin/register" element={<AdminRegister />} />
                <Route path="/admin/login" element={<AdminLogin />} />

                <Route path="/" element={<Home />} />
            </Routes>
        </Router>
    );
};

export default App;
