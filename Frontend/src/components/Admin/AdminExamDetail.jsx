import { useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import adminApis from "../../apis/Admin/admin.apis.js";
import { ArrowLeft, Calendar, Clock, FileText, User, Shield, CheckCircle, AlertCircle, PlayCircle, StopCircle } from "lucide-react";
import Button from "../ui/Button";
import Badge from "../ui/Badge";
import Spinner from "../ui/Spinner";
import ErrorState from "../ui/ErrorState";
import Skeleton from "../ui/Skeleton";
import Card from "../ui/Card";
import Layout from "../Layout/Layout";

const AdminExamDetail = () => {
    const { id } = useParams();

    const {
        data,
        isLoading,
        isError,
        error,
    } = useQuery({
        queryKey: ["admin-exam", id],
        queryFn: () => adminApis.getExam(id),
    });

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
                            <p className="text-sm text-neutral-500 mt-1">View exam information and creator details</p>
                        </div>
                    </div>
                    {getStatusBadge(data.status)}
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Exam Info Card */}
                    <Card>
                        <div className="space-y-4">
                            <div className="flex items-center justify-center">
                                <div className="w-24 h-24 bg-accent/10 rounded-full flex items-center justify-center">
                                    <FileText className="w-12 h-12 text-accent" />
                                </div>
                            </div>
                            <div className="text-center">
                                <h3 className="text-lg font-semibold text-neutral-900">{data.title}</h3>
                                <p className="text-sm text-neutral-500 mt-1">{data.courseCode}</p>
                            </div>

                            <div className="w-full pt-4 border-t border-neutral-200 space-y-4">
                                <div className="flex justify-between text-sm">
                                    <span className="text-neutral-500">Course</span>
                                    <span className="font-medium text-neutral-900">{data.courseName}</span>
                                </div>
                                <div className="flex justify-between text-sm">
                                    <span className="text-neutral-500">Status</span>
                                    <span className="font-medium text-neutral-900 capitalize">{data.status}</span>
                                </div>
                                <div className="flex justify-between text-sm">
                                    <span className="text-neutral-500">Created</span>
                                    <span className="font-medium text-neutral-900">{new Date(data.createdAt).toLocaleDateString()}</span>
                                </div>
                            </div>
                        </div>
                    </Card>

                    {/* Exam Details and Invigilator Info */}
                    <div className="lg:col-span-2 space-y-6">
                        <Card>
                            <div className="space-y-6">
                                <div>
                                    <h2 className="text-xl font-semibold text-neutral-900 mb-4">Exam Information</h2>
                                    <p className="text-sm text-neutral-500">
                                        Detailed information about the examination
                                    </p>
                                </div>

                                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                    <div className="space-y-3">
                                        <div className="flex items-center gap-3">
                                            <div className="w-10 h-10 bg-accent/10 rounded-lg flex items-center justify-center">
                                                <FileText className="w-5 h-5 text-accent" />
                                            </div>
                                            <div>
                                                <p className="text-sm text-neutral-500">Description</p>
                                                <p className="font-medium text-neutral-900">{data.description}</p>
                                            </div>
                                        </div>
                                    </div>

                                    <div className="space-y-3">
                                        <div className="flex items-center gap-3">
                                            <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                                                <CheckCircle className="w-5 h-5 text-green-600" />
                                            </div>
                                            <div>
                                                <p className="text-sm text-neutral-500">Status</p>
                                                <p className="font-medium text-neutral-900 capitalize">{data.status}</p>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
                                    <div className="flex items-center gap-3">
                                        <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                                            <PlayCircle className="w-5 h-5 text-green-600" />
                                        </div>
                                        <div>
                                            <p className="text-sm text-neutral-500">Start Time</p>
                                            <p className="font-medium text-neutral-900">
                                                {data.startTime ? new Date(data.startTime).toLocaleString() : "Not set"}
                                            </p>
                                        </div>
                                    </div>
                                    <div className="flex items-center gap-3">
                                        <div className="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center">
                                            <StopCircle className="w-5 h-5 text-red-600" />
                                        </div>
                                        <div>
                                            <p className="text-sm text-neutral-500">End Time</p>
                                            <p className="font-medium text-neutral-900">
                                                {data.endTime ? new Date(data.endTime).toLocaleString() : "Not set"}
                                            </p>
                                        </div>
                                    </div>
                                </div>

                                <div className="flex items-center gap-3 mt-6">
                                    <div className="w-10 h-10 bg-accent/10 rounded-lg flex items-center justify-center">
                                        <Clock className="w-5 h-5 text-accent" />
                                    </div>
                                    <div>
                                        <p className="text-sm text-neutral-500">Duration</p>
                                        <p className="font-medium text-neutral-900">{data.duration} minutes</p>
                                    </div>
                                </div>
                            </div>
                        </Card>

                        {/* Invigilator/Creator Info */}
                        {data.createdBy && (
                            <Card>
                                <div className="space-y-4">
                                    <h2 className="text-xl font-semibold text-neutral-900">Created By</h2>
                                    
                                    <div className="flex items-center gap-4 p-4 bg-neutral-50 rounded-lg">
                                        {data.createdBy.profileImage ? (
                                            <img
                                                src={data.createdBy.profileImage}
                                                alt={data.createdBy.fullName}
                                                className="w-12 h-12 rounded-full object-cover"
                                            />
                                        ) : (
                                            <div className="w-12 h-12 bg-accent/10 rounded-full flex items-center justify-center">
                                                <Shield className="w-6 h-6 text-accent" />
                                            </div>
                                        )}
                                        <div className="flex-1">
                                            <p className="font-medium text-neutral-900">{data.createdBy.fullName}</p>
                                            <p className="text-sm text-neutral-500">{data.createdBy.email}</p>
                                        </div>
                                        <Badge variant="neutral" className="capitalize">
                                            {data.createdBy.role}
                                        </Badge>
                                    </div>

                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                        <div className="p-4 bg-neutral-50 rounded-lg">
                                            <p className="text-sm text-neutral-500 mb-1">Phone</p>
                                            <p className="font-medium text-neutral-900">{data.createdBy.phoneNumber}</p>
                                        </div>
                                        <div className="p-4 bg-neutral-50 rounded-lg">
                                            <p className="text-sm text-neutral-500 mb-1">Verification Status</p>
                                            <p className="font-medium text-neutral-900">
                                                {data.createdBy.isVerified ? "Verified" : "Pending"}
                                            </p>
                                        </div>
                                    </div>
                                </div>
                            </Card>
                        )}
                    </div>
                </div>
            </div>
        </Layout>
    );
};

export default AdminExamDetail;
