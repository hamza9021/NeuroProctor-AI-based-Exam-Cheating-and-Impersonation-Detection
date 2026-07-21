import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { Register, Login, InvigilatorDashboard } from "./Pages";
import Student from "./components/Students/Student";
import StudentDetail from "./components/Students/StudentDetail";
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
                    <Route path="/students" element={<Student />} />
                    <Route path="/students/:studentId" element={<StudentDetail />} />
                </Route>
            </Routes>
        </Router>
    );
};

export default App;
