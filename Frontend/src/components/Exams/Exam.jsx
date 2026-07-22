import ExamsList from "./ExamsList";
import { useState } from "react";
import ExamFormModal from "./ExamFormModal";
import Layout from "../Layout/Layout";
import Button from "../ui/Button";
import { Plus } from "lucide-react";

const Exam = () => {
    const [isOpen, setIsOpen] = useState(false);
    
    return (
        <Layout title="Exams">
            <div className="flex justify-end mb-6">
                <Button onClick={() => setIsOpen(true)}>
                    <Plus className="w-4 h-4 mr-2" />
                    Add Exam
                </Button>
            </div>

            <ExamFormModal
                isOpen={isOpen}
                onClose={() => setIsOpen(false)}
            />

            <ExamsList />
        </Layout>
    );
}

export default Exam;
