import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import adminApis from "../../apis/Admin/admin.apis.js";
import { useNavigate } from "react-router-dom";
import { Search, ChevronUp, ChevronDown, Eye, Trash2, Calendar, Clock, FileText, AlertCircle, CheckCircle } from "lucide-react";
import Button from "../ui/Button";
import Badge from "../ui/Badge";
import Spinner from "../ui/Spinner";
import EmptyState from "../ui/EmptyState";
import ErrorState from "../ui/ErrorState";
import Skeleton from "../ui/Skeleton";
import Card from "../ui/Card";

export default function AdminExams() {
    const navigate = useNavigate();
    const [page, setPage] = useState(1);
    const [limit, setLimit] = useState(10);
    const [search, setSearch] = useState("");

    const {
        data,
        isLoading,
        isFetching,
        isError,
        error,
    } = useQuery({
        queryKey: [
            "admin-exams",
            page,
            limit,
            search,
        ],
        queryFn: () =>
            adminApis.getExams(
                page,
                limit,
                search
            ),
        placeholderData: (previousData) => previousData,
    });

    const exams = data?.exams || [];
    const total = data?.pagination?.total || 0;
    const totalPages = Math.ceil(total / limit);

    const scheduledCount = exams.filter(exam => exam.status === "scheduled").length;
    const ongoingCount = exams.filter(exam => exam.status === "ongoing").length;
    const completedCount = exams.filter(exam => exam.status === "completed").length;
    const cancelledCount = exams.filter(exam => exam.status === "cancelled").length;

    const getStatusBadge = (status) => {
        switch (status) {
            case "scheduled":
                return <Badge variant="neutral">Scheduled</Badge>;
            case "ongoing":
                return <Badge variant="success">Ongoing</Badge>;
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
            <div className="space-y-4">
                <Skeleton className="h-12 w-full" />
                <Skeleton className="h-64 w-full" />
            </div>
        );
    }

    if (isError) {
        return (
            <ErrorState
                title="Failed to load exams"
                description={error.message || "Please try again later."}
            />
        );
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                <div>
                    <h2 className="text-xl font-semibold text-neutral-900">Exams Overview</h2>
                    <p className="text-sm text-neutral-500 mt-1">
                        View and manage all examinations in the system
                    </p>
                </div>
            </div>

            {/* Statistics Cards */}
            <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
                <Card padding="md">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm text-neutral-500">Total Exams</p>
                            <p className="text-2xl font-semibold text-neutral-900 mt-1">{total}</p>
                        </div>
                        <div className="w-12 h-12 bg-accent/10 rounded-lg flex items-center justify-center">
                            <FileText className="w-6 h-6 text-accent" />
                        </div>
                    </div>
                </Card>

                <Card padding="md">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm text-neutral-500">Scheduled</p>
                            <p className="text-2xl font-semibold text-neutral-900 mt-1">{scheduledCount}</p>
                        </div>
                        <div className="w-12 h-12 bg-indigo-100 rounded-lg flex items-center justify-center">
                            <Clock className="w-6 h-6 text-indigo-600" />
                        </div>
                    </div>
                </Card>

                <Card padding="md">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm text-neutral-500">Ongoing</p>
                            <p className="text-2xl font-semibold text-neutral-900 mt-1">{ongoingCount}</p>
                        </div>
                        <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                            <CheckCircle className="w-6 h-6 text-green-600" />
                        </div>
                    </div>
                </Card>

                <Card padding="md">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm text-neutral-500">Completed</p>
                            <p className="text-2xl font-semibold text-neutral-900 mt-1">{completedCount}</p>
                        </div>
                        <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                            <Calendar className="w-6 h-6 text-blue-600" />
                        </div>
                    </div>
                </Card>

                <Card padding="md">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm text-neutral-500">Cancelled</p>
                            <p className="text-2xl font-semibold text-neutral-900 mt-1">{cancelledCount}</p>
                        </div>
                        <div className="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center">
                            <AlertCircle className="w-6 h-6 text-red-600" />
                        </div>
                    </div>
                </Card>
            </div>

            {/* Search and Filter */}
            <div className="flex flex-col sm:flex-row gap-4">
                <div className="relative flex-1">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-400" />
                    <input
                        type="text"
                        placeholder="Search exams..."
                        value={search}
                        onChange={(e) => {
                            setSearch(e.target.value);
                            setPage(1);
                        }}
                        className="w-full pl-10 pr-4 py-2 border border-neutral-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-accent focus:border-transparent"
                    />
                </div>

                <select
                    value={limit}
                    onChange={(e) => {
                        setLimit(Number(e.target.value));
                        setPage(1);
                    }}
                    className="px-4 py-2 border border-neutral-300 rounded-lg text-sm bg-white focus:outline-none focus:ring-2 focus:ring-accent focus:border-transparent"
                >
                    <option value={10}>10 per page</option>
                    <option value={20}>20 per page</option>
                    <option value={50}>50 per page</option>
                    <option value={100}>100 per page</option>
                </select>

                {isFetching && (
                    <div className="flex items-center gap-2 text-sm text-neutral-500">
                        <Spinner size="sm" />
                        <span>Updating...</span>
                    </div>
                )}
            </div>

            {/* Table */}
            <div className="bg-white rounded-xl shadow-sm border border-neutral-200 overflow-hidden">
                <div className="overflow-x-auto">
                    <table className="w-full">
                        <thead>
                            <tr className="border-b border-neutral-200 bg-neutral-50">
                                <th className="px-6 py-3 text-left text-xs font-semibold text-neutral-600 uppercase tracking-wider">
                                    Exam
                                </th>
                                <th className="px-6 py-3 text-left text-xs font-semibold text-neutral-600 uppercase tracking-wider">
                                    Course
                                </th>
                                <th className="px-6 py-3 text-left text-xs font-semibold text-neutral-600 uppercase tracking-wider">
                                    Code
                                </th>
                                <th className="px-6 py-3 text-left text-xs font-semibold text-neutral-600 uppercase tracking-wider">
                                    Duration
                                </th>
                                <th className="px-6 py-3 text-left text-xs font-semibold text-neutral-600 uppercase tracking-wider">
                                    Created By
                                </th>
                                <th className="px-6 py-3 text-left text-xs font-semibold text-neutral-600 uppercase tracking-wider">
                                    Status
                                </th>
                                <th className="px-6 py-3 text-right text-xs font-semibold text-neutral-600 uppercase tracking-wider">
                                    Actions
                                </th>
                            </tr>
                        </thead>

                        <tbody className="divide-y divide-neutral-200">
                            {exams.length === 0 ? (
                                <tr>
                                    <td colSpan="7">
                                        <EmptyState
                                            icon={Search}
                                            title="No exams found"
                                            description={search ? "Try adjusting your search terms" : "No exams created yet"}
                                        />
                                    </td>
                                </tr>
                            ) : (
                                exams.map((exam) => (
                                    <tr
                                        key={exam._id}
                                        className="hover:bg-neutral-50 transition-colors cursor-pointer"
                                        onClick={() => navigate(`/admin/exam/${exam._id}`)}
                                    >
                                        <td className="px-6 py-4">
                                            <div className="font-medium text-neutral-900">
                                                {exam.title}
                                            </div>
                                            <div className="text-sm text-neutral-500 mt-1">
                                                {exam.description}
                                            </div>
                                        </td>
                                        <td className="px-6 py-4 text-sm text-neutral-600">
                                            {exam.courseName}
                                        </td>
                                        <td className="px-6 py-4 text-sm text-neutral-600">
                                            {exam.courseCode}
                                        </td>
                                        <td className="px-6 py-4 text-sm text-neutral-600">
                                            <div className="flex items-center gap-2">
                                                <Clock className="w-4 h-4" />
                                                {exam.duration} min
                                            </div>
                                        </td>
                                        <td className="px-6 py-4 text-sm text-neutral-600">
                                            {exam.createdBy?.fullName || "Unknown"}
                                        </td>
                                        <td className="px-6 py-4">
                                            {getStatusBadge(exam.status)}
                                        </td>
                                        <td className="px-6 py-4 text-right">
                                            <div className="flex items-center justify-end gap-2">
                                                <button
                                                    onClick={(e) => {
                                                        e.stopPropagation();
                                                        navigate(`/admin/exam/${exam._id}`);
                                                    }}
                                                    className="p-2 text-neutral-400 hover:text-accent hover:bg-accent/10 rounded-lg transition-colors"
                                                    title="View"
                                                >
                                                    <Eye className="w-4 h-4" />
                                                </button>
                                                <button
                                                    onClick={(e) => {
                                                        e.stopPropagation();
                                                        // Handle delete
                                                    }}
                                                    className="p-2 text-neutral-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                                                    title="Delete"
                                                >
                                                    <Trash2 className="w-4 h-4" />
                                                </button>
                                            </div>
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Pagination */}
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                <p className="text-sm text-neutral-600">
                    Showing{" "}
                    <span className="font-medium text-neutral-900">
                        {exams.length === 0 ? 0 : (page - 1) * limit + 1}
                    </span>
                    {" to "}
                    <span className="font-medium text-neutral-900">
                        {Math.min(page * limit, total)}
                    </span>
                    {" of "}
                    <span className="font-medium text-neutral-900">{total}</span>
                    {" results"}
                </p>

                <div className="flex items-center gap-2">
                    <Button
                        variant="outline"
                        size="sm"
                        disabled={page === 1}
                        onClick={() => setPage((prev) => prev - 1)}
                    >
                        Previous
                    </Button>

                    <span className="px-3 py-2 text-sm text-neutral-600">
                        Page {page} of {totalPages || 1}
                    </span>

                    <Button
                        variant="outline"
                        size="sm"
                        disabled={page >= totalPages}
                        onClick={() => setPage((prev) => prev + 1)}
                    >
                        Next
                    </Button>
                </div>
            </div>
        </div>
    );
}
