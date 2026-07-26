import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useParams, useNavigate } from "react-router-dom";
import examSessionApis from "../../apis/ExamSessions/examSessions.apis.js";
import examApis from "../../apis/Exams/exams.apis.js";
import adminApis from "../../apis/Admin/admin.apis.js";
import { ArrowLeft, Trash2, Edit, Calendar, Clock, Video, Shield, User, FileText } from "lucide-react";
import Button from "../ui/Button";
import Badge from "../ui/Badge";
import Spinner from "../ui/Spinner";
import ErrorState from "../ui/ErrorState";
import Card from "../ui/Card";
import Layout from "../Layout/Layout";
import ExamSessionFormModal from "./ExamSessionFormModal";

export default function ExamSessionDetail() {
    const { sessionId } = useParams();
    const navigate = useNavigate();
    const queryClient = useQueryClient();
    const [showEditModal, setShowEditModal] = useState(false);

    const { data: sessionData, isLoading, isError, error } = useQuery({
        queryKey: ["examSession", sessionId],
        queryFn: () => examSessionApis.getExamSession(sessionId),
        enabled: !!sessionId,
    });

    const { data: examData } = useQuery({
        queryKey: ["exam", sessionData?.examId],
        queryFn: () => examApis.getExam(sessionData?.examId?._id || sessionData?.examId),
        enabled: !!sessionData?.examId,
    });

    const { mutate: deleteSession, isPending: isDeleting } = useMutation({
        mutationFn: () => examSessionApis.deleteExamSession(sessionId),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["examSessions"] });
            navigate("/examSessions");
        },
    });

    const handleDelete = () => {
        if (window.confirm("Are you sure you want to delete this exam session?")) {
            deleteSession();
        }
    };

    const getStatusBadge = (status) => {
        switch (status) {
            case "active":
                return <Badge variant="success">Active</Badge>;
            case "completed":
                return <Badge variant="info">Completed</Badge>;
            case "scheduled":
                return <Badge variant="neutral">Scheduled</Badge>;
            case "waiting":
                return <Badge variant="warning">Waiting</Badge>;
            case "processing":
                return <Badge variant="warning">Processing</Badge>;
            case "cancelled":
                return <Badge variant="error">Cancelled</Badge>;
            default:
                return <Badge variant="neutral">{status}</Badge>;
        }
    };

    const getModeBadge = (mode) => {
        switch (mode) {
            case "live":
                return <Badge variant="success">Live</Badge>;
            case "offline":
                return <Badge variant="neutral">Offline</Badge>;
            default:
                return <Badge variant="neutral">{mode}</Badge>;
        }
    };

    if (isLoading) {
        return (
            <Layout title="Exam Session Details">
                <div className="flex items-center justify-center min-h-screen">
                    <Spinner size="lg" />
                </div>
            </Layout>
        );
    }

    if (isError) {
        return (
            <Layout title="Exam Session Details">
                <ErrorState
                    title="Failed to load exam session"
                    description={error.message || "Please try again later."}
                />
            </Layout>
        );
    }

    const session = sessionData;
    const exam = examData;

    return (
        <Layout title="Exam Session Details">
            <div className="space-y-6">
                {/* Header */}
                <div className="flex items-center justify-between">
                    <Button
                        variant="outline"
                        onClick={() => navigate("/examSessions")}
                        className="flex items-center gap-2"
                    >
                        <ArrowLeft className="w-4 h-4" />
                        Back to Sessions
                    </Button>
                    <div className="flex items-center gap-2">
                        <Button
                            variant="outline"
                            onClick={() => setShowEditModal(true)}
                            className="flex items-center gap-2"
                        >
                            <Edit className="w-4 h-4" />
                            Edit
                        </Button>
                        <Button
                            variant="destructive"
                            onClick={handleDelete}
                            disabled={isDeleting}
                            className="flex items-center gap-2"
                        >
                            {isDeleting ? (
                                <Spinner size="sm" />
                            ) : (
                                <Trash2 className="w-4 h-4" />
                            )}
                            Delete
                        </Button>
                    </div>
                </div>

                {/* Session Info */}
                <Card>
                    <div className="space-y-6">
                        <div className="flex items-start justify-between">
                            <div>
                                <h2 className="text-2xl font-semibold text-neutral-900">
                                    Session: {session?.sessionCode}
                                </h2>
                                <p className="text-sm text-neutral-500 mt-1">
                                    ID: {session?._id}
                                </p>
                            </div>
                            <div className="flex items-center gap-2">
                                {getStatusBadge(session?.status)}
                                {getModeBadge(session?.mode)}
                            </div>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-6 border-t border-neutral-200">
                            <div className="space-y-4">
                                <h3 className="text-sm font-semibold text-neutral-900 uppercase tracking-wider">
                                    Session Information
                                </h3>
                                <div className="space-y-3">
                                    <div className="flex items-center gap-3">
                                        <Calendar className="w-5 h-5 text-neutral-400" />
                                        <div>
                                            <p className="text-sm text-neutral-500">Created</p>
                                            <p className="text-sm font-medium text-neutral-900">
                                                {new Date(session?.createdAt).toLocaleDateString()} at{" "}
                                                {new Date(session?.createdAt).toLocaleTimeString()}
                                            </p>
                                        </div>
                                    </div>
                                    {session?.startedAt && (
                                        <div className="flex items-center gap-3">
                                            <Clock className="w-5 h-5 text-neutral-400" />
                                            <div>
                                                <p className="text-sm text-neutral-500">Started</p>
                                                <p className="text-sm font-medium text-neutral-900">
                                                    {new Date(session.startedAt).toLocaleDateString()} at{" "}
                                                    {new Date(session.startedAt).toLocaleTimeString()}
                                                </p>
                                            </div>
                                        </div>
                                    )}
                                    {session?.endedAt && (
                                        <div className="flex items-center gap-3">
                                            <Clock className="w-5 h-5 text-neutral-400" />
                                            <div>
                                                <p className="text-sm text-neutral-500">Ended</p>
                                                <p className="text-sm font-medium text-neutral-900">
                                                    {new Date(session.endedAt).toLocaleDateString()} at{" "}
                                                    {new Date(session.endedAt).toLocaleTimeString()}
                                                </p>
                                            </div>
                                        </div>
                                    )}
                                    <div className="flex items-center gap-3">
                                        <Shield className="w-5 h-5 text-neutral-400" />
                                        <div>
                                            <p className="text-sm text-neutral-500">Verified</p>
                                            <p className="text-sm font-medium text-neutral-900">
                                                {session?.verified ? "Yes" : "No"}
                                            </p>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div className="space-y-4">
                                <h3 className="text-sm font-semibold text-neutral-900 uppercase tracking-wider">
                                    Assigned Invigilator
                                </h3>
                                {session?.invigilatorId ? (
                                    <div className="flex items-center gap-3 p-3 bg-neutral-50 rounded-lg">
                                        <div className="w-10 h-10 bg-accent/10 rounded-full flex items-center justify-center">
                                            <User className="w-5 h-5 text-accent" />
                                        </div>
                                        <div>
                                            <p className="font-medium text-neutral-900">{session.invigilatorId.name}</p>
                                            <p className="text-sm text-neutral-500">{session.invigilatorId.email}</p>
                                        </div>
                                    </div>
                                ) : (
                                    <p className="text-sm text-neutral-500">No invigilator assigned</p>
                                )}
                            </div>
                        </div>
                    </div>
                </Card>

                {/* Exam Information */}
                {exam && (
                    <Card>
                        <div className="space-y-4">
                            <h3 className="text-lg font-semibold text-neutral-900">Associated Exam</h3>
                            <div className="flex items-center gap-3 p-4 bg-neutral-50 rounded-lg">
                                <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                                    <FileText className="w-6 h-6 text-blue-600" />
                                </div>
                                <div className="flex-1">
                                    <p className="font-medium text-neutral-900">{exam.title}</p>
                                    <p className="text-sm text-neutral-500">
                                        {exam.courseName} - {exam.courseCode}
                                    </p>
                                </div>
                                <Button
                                    variant="outline"
                                    size="sm"
                                    onClick={() => navigate(`/exams/${exam._id}`)}
                                >
                                    View Exam
                                </Button>
                            </div>
                        </div>
                    </Card>
                )}
            </div>

            {/* Edit Modal */}
            <ExamSessionFormModal
                isOpen={showEditModal}
                onClose={() => setShowEditModal(false)}
                onSuccess={() => {
                    queryClient.invalidateQueries({ queryKey: ["examSession", sessionId] });
                    setShowEditModal(false);
                }}
                sessionData={session}
                isEdit={true}
            />
        </Layout>
    );
}
