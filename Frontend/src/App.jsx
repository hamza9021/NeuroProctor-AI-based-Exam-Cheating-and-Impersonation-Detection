import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { Register, Login } from "./Pages";

const App = () => {
    return (
        <Router>
            <Routes>
                <Route path="/register" element={<Register />} />
                <Route path="/login" element={<Login />} />
            </Routes>
        </Router>
    );
};

export default App;
