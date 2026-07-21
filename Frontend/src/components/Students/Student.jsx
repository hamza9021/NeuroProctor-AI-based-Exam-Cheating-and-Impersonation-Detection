import StudentsList from "./StudentsList";
import { useState } from "react";
import StudentFormModal from "./StudentFormModal";
import Layout from "../Layout/Layout";
import Button from "../ui/Button";
import { Plus } from "lucide-react";

const Student = () => {
    const [isOpen, setIsOpen] = useState(false);
    
    return (
        <Layout title="Students">
            <div className="flex justify-end mb-6">
                <Button onClick={() => setIsOpen(true)}>
                    <Plus className="w-4 h-4 mr-2" />
                    Add Student
                </Button>
            </div>

            <StudentFormModal
                isOpen={isOpen}
                onClose={() => setIsOpen(false)}
            />

            <StudentsList />
        </Layout>
    );
}

export default Student;