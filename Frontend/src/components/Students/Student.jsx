import StudentsList from "./StudentsList";
import { useState } from "react";
import StudentFormModal from "./StudentFormModal";

const Student = () => {
    const [isOpen, setIsOpen] = useState(false);
    return (<div className="flex items-center justify-center h-screen">

        <button
            onClick={() => setIsOpen(true)}
            className="px-4 py-2 bg-blue-600 text-white rounded-md"
        >
            Add Student
        </button>

        <StudentFormModal
            isOpen={isOpen}
            onClose={() => setIsOpen(false)}
        />

        <StudentsList />
    </div>)
}


export default Student;