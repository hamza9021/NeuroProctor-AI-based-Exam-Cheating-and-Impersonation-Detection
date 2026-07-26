import { useState, useEffect } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import examSessionApis from "../../apis/ExamSessions/examSessions.apis.js";
import examApis from "../../apis/Exams/exams.apis.js";
import adminApis from "../../apis/Admin/admin.apis.js";
import { X, Loader2 } from "lucide-react";
import Button from "../ui/Button";

export default function ExamSessionFormModal({ isOpen, onClose, onSuccess, sessionData, isEdit = false }) {
    const queryClient = useQueryClient();
    const [formData, setFormData] = useState({
        examId: "",
        invigilatorId: "",
        mode: "offline",
    });

    // Pre-fill form when editing
    useEffect(() => {
        if (isOpen) {
            if (isEdit && sessionData) {
                setFormData({
                    examId: sessionData.examId?._id || sessionData.examId || "",
                    invigilatorId: sessionData.invigilatorId?._id || sessionData.invigilatorId || "",
                    mode: sessionData.mode || "offline",
                });
            } else {
                setFormData({ examId: "", invigilatorId: "", mode: "offline" });
            }
        }
    }, [isOpen, isEdit, sessionData]);

    const { data: examsData } = useQuery({
        queryKey: ["exams-for-session"],
        queryFn: () => examApis.getExams(1, 100, "", "createdAt", "desc"),
        enabled: isOpen,
    });

    const { data: invigilatorsData } = useQuery({
        queryKey: ["invigilators-for-session"],
        queryFn: () => adminApis.getInvigilators(1, 100, ""),
        enabled: isOpen,
    });

    const { mutate: createSession, isPending: isCreating } = useMutation({
        mutationFn: (data) => examSessionApis.createExamSession(data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["examSessions"] });
            onSuccess?.();
            onClose();
        },
    });

    const { mutate: updateSession, isPending: isUpdating } = useMutation({
        mutationFn: ({ id, data }) => examSessionApis.updateExamSession(id, data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["examSessions"] });
            queryClient.invalidateQueries({ queryKey: ["examSession"] });
            onSuccess?.();
            onClose();
        },
    });

    const handleSubmit = (e) => {
        e.preventDefault();
        if (!formData.examId || !formData.invigilatorId) {
            alert("Please select both an exam and an invigilator");
            return;
        }
        
        if (isEdit && sessionData) {
            updateSession({ id: sessionData._id, data: formData });
        } else {
            createSession(formData);
        }
    };

    if (!isOpen) return null;

    const exams = examsData?.exams || [];
    const invigilators = invigilatorsData?.invigilators || [];

    return (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg shadow-xl max-w-md w-full">
                <div className="flex items-center justify-between p-6 border-b border-neutral-200">
                    <h3 className="text-lg font-semibold text-neutral-900">
                        {isEdit ? "Edit Exam Session" : "Create Exam Session"}
                    </h3>
                    <button
                        onClick={onClose}
                        className="p-2 text-neutral-400 hover:text-neutral-600 hover:bg-neutral-100 rounded-lg transition-colors"
                    >
                        <X className="w-5 h-5" />
                    </button>
                </div>

                <form onSubmit={handleSubmit} className="p-6 space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-neutral-700 mb-2">
                            Select Exam
                        </label>
                        <select
                            value={formData.examId}
                            onChange={(e) => setFormData({ ...formData, examId: e.target.value })}
                            required
                            className="w-full px-3 py-2 border border-neutral-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-accent focus:border-transparent"
                        >
                            <option value="">Choose an exam...</option>
                            {exams.map((exam) => (
                                <option key={exam._id} value={exam._id}>
                                    {exam.title} - {exam.courseCode}
                                </option>
                            ))}
                        </select>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-neutral-700 mb-2">
                            Assign Invigilator
                        </label>
                        <select
                            value={formData.invigilatorId}
                            onChange={(e) => setFormData({ ...formData, invigilatorId: e.target.value })}
                            required
                            className="w-full px-3 py-2 border border-neutral-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-accent focus:border-transparent"
                        >
                            <option value="">Choose an invigilator...</option>
                            {invigilators
                                .filter((inv) => inv.isVerified)
                                .map((invigilator) => (
                                    <option key={invigilator._id} value={invigilator._id}>
                                        {invigilator.name} ({invigilator.email})
                                    </option>
                                ))}
                        </select>
                        {!invigilators.filter((inv) => inv.isVerified).length && (
                            <p className="text-xs text-neutral-500 mt-1">
                                No verified invigilators available
                            </p>
                        )}
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-neutral-700 mb-2">
                            Session Mode
                        </label>
                        <select
                            value={formData.mode}
                            onChange={(e) => setFormData({ ...formData, mode: e.target.value })}
                            className="w-full px-3 py-2 border border-neutral-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-accent focus:border-transparent"
                        >
                            <option value="offline">Offline</option>
                            <option value="live">Live</option>
                        </select>
                    </div>

                    <div className="flex gap-3 pt-4">
                        <Button
                            type="button"
                            variant="outline"
                            onClick={onClose}
                            className="flex-1"
                        >
                            Cancel
                        </Button>
                        <Button
                            type="submit"
                            disabled={isCreating || isUpdating}
                            className="flex-1 flex items-center justify-center gap-2"
                        >
                            {(isCreating || isUpdating) ? (
                                <>
                                    <Loader2 className="w-4 h-4 animate-spin" />
                                    {isEdit ? "Updating..." : "Creating..."}
                                </>
                            ) : (
                                isEdit ? "Update Session" : "Create Session"
                            )}
                        </Button>
                    </div>
                </form>
            </div>
        </div>
    );
}
