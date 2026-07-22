import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import adminApis from "../../apis/Admin/admin.apis.js";
import { useNavigate } from "react-router-dom";
import { Search, ChevronUp, ChevronDown, Eye, Trash2, Shield, Mail, Phone, UserCheck, UserX, CheckCircle, XCircle } from "lucide-react";
import Button from "../ui/Button";
import Badge from "../ui/Badge";
import Spinner from "../ui/Spinner";
import EmptyState from "../ui/EmptyState";
import ErrorState from "../ui/ErrorState";
import Skeleton from "../ui/Skeleton";
import Card from "../ui/Card";

export default function InvigilatorsList() {
    const navigate = useNavigate();
    const [page, setPage] = useState(1);
    const [limit, setLimit] = useState(10);
    const [search, setSearch] = useState("");
    const queryClient = useQueryClient();

    const {
        data,
        isLoading,
        isFetching,
        isError,
        error,
    } = useQuery({
        queryKey: [
            "invigilators",
            page,
            limit,
            search,
        ],
        queryFn: () =>
            adminApis.getInvigilators(
                page,
                limit,
                search
            ),
        placeholderData: (previousData) => previousData,
    });

    const { mutate: verifyMutate } = useMutation({
        mutationFn: (invigilatorId) => {
            return adminApis.verifyInvigilator(invigilatorId);
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["invigilators"] });
        },
    });

    const { mutate: deleteMutate } = useMutation({
        mutationFn: (invigilatorId) => {
            return adminApis.deleteInvigilator(invigilatorId);
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["invigilators"] });
        },
    });

    const invigilators = data?.invigilators || [];
    const total = data?.pagination?.total || 0;
    const totalPages = Math.ceil(total / limit);

    const getVerificationBadge = (isVerified) => {
        return isVerified ? (
            <Badge variant="success">Verified</Badge>
        ) : (
            <Badge variant="error">Pending</Badge>
        );
    };

    const handleVerify = (invigilatorId) => {
        if (window.confirm("Are you sure you want to verify this invigilator?")) {
            verifyMutate(invigilatorId);
        }
    };

    const handleDelete = (invigilatorId) => {
        if (window.confirm("Are you sure you want to delete this invigilator? This action cannot be undone.")) {
            deleteMutate(invigilatorId);
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
                title="Failed to load invigilators"
                description={error.message || "Please try again later."}
            />
        );
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                <div>
                    <h2 className="text-xl font-semibold text-neutral-900">Invigilators</h2>
                    <p className="text-sm text-neutral-500 mt-1">
                        Manage and view all invigilators
                    </p>
                </div>
            </div>

            {/* Statistics Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Card padding="md">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm text-neutral-500">Total Invigilators</p>
                            <p className="text-2xl font-semibold text-neutral-900 mt-1">{total}</p>
                        </div>
                        <div className="w-12 h-12 bg-accent/10 rounded-lg flex items-center justify-center">
                            <Shield className="w-6 h-6 text-accent" />
                        </div>
                    </div>
                </Card>

                <Card padding="md">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm text-neutral-500">Verified</p>
                            <p className="text-2xl font-semibold text-neutral-900 mt-1">{invigilators.filter(i => i.isVerified).length}</p>
                        </div>
                        <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                            <UserCheck className="w-6 h-6 text-green-600" />
                        </div>
                    </div>
                </Card>

                <Card padding="md">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm text-neutral-500">Pending Verification</p>
                            <p className="text-2xl font-semibold text-neutral-900 mt-1">{invigilators.filter(i => !i.isVerified).length}</p>
                        </div>
                        <div className="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center">
                            <UserX className="w-6 h-6 text-yellow-600" />
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
                        placeholder="Search invigilators..."
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
                                    Invigilator
                                </th>
                                <th className="px-6 py-3 text-left text-xs font-semibold text-neutral-600 uppercase tracking-wider">
                                    Contact
                                </th>
                                <th className="px-6 py-3 text-left text-xs font-semibold text-neutral-600 uppercase tracking-wider">
                                    Status
                                </th>
                                <th className="px-6 py-3 text-left text-xs font-semibold text-neutral-600 uppercase tracking-wider">
                                    Created
                                </th>
                                <th className="px-6 py-3 text-right text-xs font-semibold text-neutral-600 uppercase tracking-wider">
                                    Actions
                                </th>
                            </tr>
                        </thead>

                        <tbody className="divide-y divide-neutral-200">
                            {invigilators.length === 0 ? (
                                <tr>
                                    <td colSpan="5">
                                        <EmptyState
                                            icon={Search}
                                            title="No invigilators found"
                                            description={search ? "Try adjusting your search terms" : "No invigilators registered yet"}
                                        />
                                    </td>
                                </tr>
                            ) : (
                                invigilators.map((invigilator) => (
                                    <tr
                                        key={invigilator._id}
                                        className="hover:bg-neutral-50 transition-colors cursor-pointer"
                                        onClick={() => navigate(`/invigilator/${invigilator._id}`)}
                                    >
                                        <td className="px-6 py-4">
                                            <div className="flex items-center gap-3">
                                                {invigilator.profileImage ? (
                                                    <img
                                                        src={invigilator.profileImage}
                                                        alt={invigilator.fullName}
                                                        className="w-10 h-10 rounded-full object-cover"
                                                    />
                                                ) : (
                                                    <div className="w-10 h-10 bg-accent/10 rounded-full flex items-center justify-center">
                                                        <Shield className="w-5 h-5 text-accent" />
                                                    </div>
                                                )}
                                                <div>
                                                    <div className="font-medium text-neutral-900">
                                                        {invigilator.fullName}
                                                    </div>
                                                    <div className="text-sm text-neutral-500 mt-1">
                                                        {invigilator.email}
                                                    </div>
                                                </div>
                                            </div>
                                        </td>
                                        <td className="px-6 py-4 text-sm text-neutral-600">
                                            <div className="space-y-1">
                                                <div className="flex items-center gap-2">
                                                    <Phone className="w-4 h-4" />
                                                    {invigilator.phoneNumber}
                                                </div>
                                            </div>
                                        </td>
                                        <td className="px-6 py-4">
                                            {getVerificationBadge(invigilator.isVerified)}
                                        </td>
                                        <td className="px-6 py-4 text-sm text-neutral-600">
                                            {new Date(invigilator.createdAt).toLocaleDateString()}
                                        </td>
                                        <td className="px-6 py-4 text-right">
                                            <div className="flex items-center justify-end gap-2">
                                                {!invigilator.isVerified && (
                                                    <button
                                                        onClick={(e) => {
                                                            e.stopPropagation();
                                                            handleVerify(invigilator._id);
                                                        }}
                                                        className="p-2 text-neutral-400 hover:text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                                                        title="Verify"
                                                    >
                                                        <CheckCircle className="w-4 h-4" />
                                                    </button>
                                                )}
                                                <button
                                                    onClick={(e) => {
                                                        e.stopPropagation();
                                                        navigate(`/invigilator/${invigilator._id}`);
                                                    }}
                                                    className="p-2 text-neutral-400 hover:text-accent hover:bg-accent/10 rounded-lg transition-colors"
                                                    title="View"
                                                >
                                                    <Eye className="w-4 h-4" />
                                                </button>
                                                <button
                                                    onClick={(e) => {
                                                        e.stopPropagation();
                                                        handleDelete(invigilator._id);
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
                        {invigilators.length === 0 ? 0 : (page - 1) * limit + 1}
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
