import { useParams } from "react-router-dom";
import {
    useQuery,
    useMutation,
    useQueryClient,
} from "@tanstack/react-query";
import examApis from "../../apis/Exams/exams.apis.js";
import { ArrowLeft, Calendar, Clock, FileText, Edit, Trash2 } from "lucide-react";
import Button from "../ui/Button";
import Badge from "../ui/Badge";
import Spinner from "../ui/Spinner";
import ErrorState from "../ui/ErrorState";
import Skeleton from "../ui/Skeleton";
import Card from "../ui/Card";
import Layout from "../Layout/Layout";
import { useState } from "react";
import ExamFormModal from "./ExamFormModal";

const ExamDetail = () => {
    const { examId } = useParams();
    const queryClient = useQueryClient();
    const [isEditModalOpen, setIsEditModalOpen] = useState(false);

    const {
        data,
        isLoading,
        isError,
        error,
    } = useQuery({
        queryKey: ["exam", examId],
        queryFn: () => examApis.getExam(examId),
    });

    const { mutate: deleteMutate, isPending: isDeleting } = useMutation({
        mutationFn: (examId) => examApis.deleteExam(examId),
        onSuccess: () => {
            window.history.back();
        },
    });

    const { mutate: updateMutate, isPending: isUpdating } = useMutation({
        mutationFn: ({ examId, examData }) => examApis.updateExam(examId, examData),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["exam", examId] });
            setIsEditModalOpen(false);
        },
    });

    const handleDelete = () => {
        if (window.confirm("Are you sure you want to delete this exam?")) {
            deleteMutate(examId);
        }
    };

    const handleUpdate = (examData) => {
        updateMutate({ examId, examData });
    };

    const getStatusBadge = (status) => {
        switch (status) {
            case "active":
                return <Badge variant="success">Active</Badge>;
            case "completed":
                return <Badge variant="info">Completed</Badge>;
            case "cancelled":
                return <Badge variant="error">Cancelled</Badge>;
            default:
                return <Badge variant="neutral">{status}</Badge>;
        }
    };

    if (isLoading) {
        return (
            <div className="space-y-6">
                <Skeleton className="h-12 w-48" />
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    <Skeleton className="h-64" />
                    <Skeleton className="h-64 lg:col-span-2" />
                </div>
            </div>
        );
    }

    if (isError) {
        return (
            <ErrorState
                title="Failed to load exam"
                description={error.message || "Please try again later."}
            />
        );
    }

    return (
        <Layout title="Exam Details">
            <div className="space-y-6">
                {/* Header */}
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                        <button
                            onClick={() => window.history.back()}
                            className="p-2 text-neutral-400 hover:text-neutral-600 hover:bg-neutral-100 rounded-lg transition-colors"
                        >
                            <ArrowLeft className="w-5 h-5" />
                        </button>
                        <div>
                            <h1 className="text-2xl font-semibold text-neutral-900">Exam Details</h1>
                            <p className="text-sm text-neutral-500 mt-1">View and manage exam information</p>
                        </div>
                    </div>
                    <div className="flex items-center gap-2">
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={() => setIsEditModalOpen(true)}
                        >
                            <Edit className="w-4 h-4 mr-2" />
                            Edit
                        </Button>
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={handleDelete}
                            isLoading={isDeleting}
                            className="text-red-600 hover:text-red-700 hover:bg-red-50"
                        >
                            <Trash2 className="w-4 h-4 mr-2" />
                            Delete
                        </Button>
                    </div>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Exam Info Card */}
                    <Card>
                        <div className="space-y-4">
                            <div>
                                <h3 className="text-lg font-semibold text-neutral-900">{data.title}</h3>
                                <p className="text-sm text-neutral-500 mt-1">{data.description}</p>
                            </div>

                            <div className="w-full pt-4 border-t border-neutral-200 space-y-4">
                                <div className="flex justify-between text-sm">
                                    <span className="text-neutral-500">Course</span>
                                    <span className="font-medium text-neutral-900">{data.courseName}</span>
                                </div>
                                <div className="flex justify-between text-sm">
                                    <span className="text-neutral-500">Course Code</span>
                                    <span className="font-medium text-neutral-900">{data.courseCode}</span>
                                </div>
                                <div className="flex justify-between text-sm">
                                    <span className="text-neutral-500">Duration</span>
                                    <span className="font-medium text-neutral-900">{data.duration} minutes</span>
                                </div>
                                <div className="flex justify-between text-sm">
                                    <span className="text-neutral-500">Status</span>
                                    <div>{getStatusBadge(data.status)}</div>
                                </div>
                            </div>
                        </div>
                    </Card>

                    {/* Schedule Card */}
                    <div className="lg:col-span-2 space-y-6">
                        <Card>
                            <div className="space-y-6">
                                <div>
                                    <h2 className="text-xl font-semibold text-neutral-900 mb-4">Schedule</h2>
                                    <p className="text-sm text-neutral-500">
                                        Exam timing and duration information
                                    </p>
                                </div>

                                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                    <div className="space-y-3">
                                        <div className="flex items-center gap-3">
                                            <div className="w-10 h-10 bg-accent/10 rounded-lg flex items-center justify-center">
                                                <Calendar className="w-5 h-5 text-accent" />
                                            </div>
                                            <div>
                                                <p className="text-sm text-neutral-500">Start Date</p>
                                                <p className="font-medium text-neutral-900">
                                                    {new Date(data.startTime).toLocaleDateString()}
                                                </p>
                                            </div>
                                        </div>
                                        <div className="flex items-center gap-3">
                                            <div className="w-10 h-10 bg-accent/10 rounded-lg flex items-center justify-center">
                                                <Clock className="w-5 h-5 text-accent" />
                                            </div>
                                            <div>
                                                <p className="text-sm text-neutral-500">Start Time</p>
                                                <p className="font-medium text-neutral-900">
                                                    {new Date(data.startTime).toLocaleTimeString()}
                                                </p>
                                            </div>
                                        </div>
                                    </div>

                                    <div className="space-y-3">
                                        <div className="flex items-center gap-3">
                                            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                                                <Calendar className="w-5 h-5 text-blue-600" />
                                            </div>
                                            <div>
                                                <p className="text-sm text-neutral-500">End Date</p>
                                                <p className="font-medium text-neutral-900">
                                                    {new Date(data.endTime).toLocaleDateString()}
                                                </p>
                                            </div>
                                        </div>
                                        <div className="flex items-center gap-3">
                                            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                                                <Clock className="w-5 h-5 text-blue-600" />
                                            </div>
                                            <div>
                                                <p className="text-sm text-neutral-500">End Time</p>
                                                <p className="font-medium text-neutral-900">
                                                    {new Date(data.endTime).toLocaleTimeString()}
                                                </p>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                <div className="pt-4 border-t border-neutral-200">
                                    <div className="flex items-center justify-between">
                                        <div className="flex items-center gap-2">
                                            <FileText className="w-5 h-5 text-neutral-500" />
                                            <span className="text-sm text-neutral-500">Total Duration</span>
                                        </div>
                                        <span className="font-semibold text-neutral-900">{data.duration} minutes</span>
                                    </div>
                                </div>
                            </div>
                        </Card>

                        {/* Additional Info */}
                        <Card>
                            <div className="space-y-4">
                                <h2 className="text-xl font-semibold text-neutral-900">Additional Information</h2>
                                
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    <div className="p-4 bg-neutral-50 rounded-lg">
                                        <p className="text-sm text-neutral-500 mb-1">Created At</p>
                                        <p className="font-medium text-neutral-900">
                                            {new Date(data.createdAt).toLocaleString()}
                                        </p>
                                    </div>
                                    <div className="p-4 bg-neutral-50 rounded-lg">
                                        <p className="text-sm text-neutral-500 mb-1">Last Updated</p>
                                        <p className="font-medium text-neutral-900">
                                            {new Date(data.updatedAt).toLocaleString()}
                                        </p>
                                    </div>
                                </div>
                            </div>
                        </Card>
                    </div>
                </div>
            </div>

            {/* Edit Modal */}
            <ExamFormModal
                isOpen={isEditModalOpen}
                onClose={() => setIsEditModalOpen(false)}
                examData={data}
                isEdit={true}
                onUpdate={handleUpdate}
                isLoading={isUpdating}
            />
        </Layout>
    );
};

export default ExamDetail;
