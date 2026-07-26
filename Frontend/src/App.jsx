import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { Register, Login, InvigilatorDashboard, AdminDashboard, Unauthorized } from "./Pages";
import Homepage from "./Pages/Homepage";
import Student from "./components/Students/Student";
import StudentDetail from "./components/Students/StudentDetail";
import Exam from "./components/Exams/Exam";
import ExamDetail from "./components/Exams/ExamDetail";
import ExamSessionsList from "./components/ExamSessions/ExamSessionsList";
import ExamSessionDetail from "./components/ExamSessions/ExamSessionDetail";
import Admin from "./components/Admin/Admin";
import AdminDetail from "./components/Admin/AdminDetail";
import InvigilatorDetail from "./components/Admin/InvigilatorDetail";
import AdminExamDetail from "./components/Admin/AdminExamDetail";
import ProtectedRoute from "./components/ProtectedRoute";
import AdminProtectedRoute from "./components/AdminProtectedRoute";
import InvigilatorProtectedRoute from "./components/InvigilatorProtectedRoute";
import InvigilatorSessions from "./Pages/Dashboard/InvigilatorSessions";


const App = () => {
    return (
        <Router>
            <Routes>
                <Route path="/" element={<Homepage />} />
                <Route path="/register" element={<Register />} />
                <Route path="/login" element={<Login />} />

                <Route element={<ProtectedRoute />}>
                    <Route element={<AdminProtectedRoute />}>
                        <Route
                            path="/admin/dashboard"
                            element={<AdminDashboard />}
                        />
                        <Route path="/admin" element={<Admin />} />
                        <Route path="/admin/:id" element={<AdminDetail />} />
                        <Route path="/invigilator/:id" element={<InvigilatorDetail />} />
                        <Route path="/admin/exam/:id" element={<AdminExamDetail />} />
                        <Route path="/students" element={<Student />} />
                        <Route path="/students/:studentId" element={<StudentDetail />} />
                        <Route path="/exams" element={<Exam />} />
                        <Route path="/examSessions" element={<ExamSessionsList />} />
                    </Route>
                    
                    <Route element={<InvigilatorProtectedRoute />}>
                        <Route
                            path="/invigilator/dashboard"
                            element={<InvigilatorDashboard />}
                        />
                        <Route
                            path="/invigilator/sessions"
                            element={<InvigilatorSessions />}
                        />
                        <Route
                            path="/invigilator/sessions/:sessionId"
                            element={<InvigilatorSessions />}
                        />
                    </Route>

                    <Route path="/exams/:examId" element={<ExamDetail />} />
                    <Route path="/examSessions/:sessionId" element={<ExamSessionDetail />} />
                </Route>
                
                <Route path="/unauthorized" element={<Unauthorized />} />
            </Routes>
        </Router>
    );
};

export default App;
