import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { Register, Login, InvigilatorDashboard } from "./Pages";
import ProtectedRoute from "./components/ProtectedRoute";

const App = () => {
    return (
        <Router>
            <Routes>
                <Route path="/register" element={<Register />} />
                <Route path="/login" element={<Login />} />

                <Route element={<ProtectedRoute />}>
                    <Route
                        path="/invigilator/dashboard"
                        element={<InvigilatorDashboard />}
                    />
                </Route>
            </Routes>
        </Router>
    );
};

export default App;
