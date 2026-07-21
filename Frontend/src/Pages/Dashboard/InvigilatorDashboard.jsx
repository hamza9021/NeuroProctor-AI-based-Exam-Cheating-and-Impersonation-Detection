import { useQuery } from "@tanstack/react-query";
import StudentFormModal from "../../components/Students/StudentFormModal.jsx"
import { useState } from "react";

const InvigilatorDashboard = ()=>{
      const [isOpen, setIsOpen] = useState(false);


    return (
        <div>
            <h1>Invigilator Dashboard</h1>
            
<div className="flex items-center justify-center h-screen">
      <button
        onClick={() => setIsOpen(true)}
        className="px-4 py-2 bg-blue-600 text-white rounded-md"
      >
        Open Modal
      </button>

      <StudentFormModal
        isOpen={isOpen}
        onClose={() => setIsOpen(false)}
      />
    </div>
        </div>
    )
}


export default InvigilatorDashboard;

