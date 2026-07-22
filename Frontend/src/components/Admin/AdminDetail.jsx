import { useParams } from "react-router-dom";
import {
    useQuery,
} from "@tanstack/react-query";
import adminApis from "../../apis/Admin/admin.apis.js";
import { ArrowLeft, Mail, Phone, Calendar, Shield, UserCheck, UserX, MapPin } from "lucide-react";
import Button from "../ui/Button";
import Badge from "../ui/Badge";
import Spinner from "../ui/Spinner";
import ErrorState from "../ui/ErrorState";
import Skeleton from "../ui/Skeleton";
import Card from "../ui/Card";
import Layout from "../Layout/Layout";

const AdminDetail = () => {
    const { id } = useParams();

    const {
        data,
        isLoading,
        isError,
        error,
    } = useQuery({
        queryKey: ["admin", id],
        queryFn: () => adminApis.getAdmin(id),
    });

    const getVerificationBadge = (isVerified) => {
        return isVerified ? (
            <Badge variant="success">Verified</Badge>
        ) : (
            <Badge variant="error">Unverified</Badge>
        );
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
                title="Failed to load admin"
                description={error.message || "Please try again later."}
            />
        );
    }

    return (
        <Layout title="Admin Details">
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
                            <h1 className="text-2xl font-semibold text-neutral-900">Admin Details</h1>
                            <p className="text-sm text-neutral-500 mt-1">View and manage admin information</p>
                        </div>
                    </div>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Admin Info Card */}
                    <Card>
                        <div className="space-y-4">
                            <div className="flex items-center justify-center">
                                {data.profileImage ? (
                                    <img
                                        src={data.profileImage}
                                        alt={data.fullName}
                                        className="w-24 h-24 rounded-full object-cover"
                                    />
                                ) : (
                                    <div className="w-24 h-24 bg-accent/10 rounded-full flex items-center justify-center">
                                        <Shield className="w-12 h-12 text-accent" />
                                    </div>
                                )}
                            </div>
                            <div className="text-center">
                                <h3 className="text-lg font-semibold text-neutral-900">{data.fullName}</h3>
                                <p className="text-sm text-neutral-500 mt-1">{data.email}</p>
                                <div className="flex justify-center mt-2">
                                    {getVerificationBadge(data.isVerified)}
                                </div>
                            </div>

                            <div className="w-full pt-4 border-t border-neutral-200 space-y-4">
                                <div className="flex justify-between text-sm">
                                    <span className="text-neutral-500">Role</span>
                                    <span className="font-medium text-neutral-900 capitalize">{data.role}</span>
                                </div>
                                <div className="flex justify-between text-sm">
                                    <span className="text-neutral-500">Phone</span>
                                    <span className="font-medium text-neutral-900">{data.phoneNumber}</span>
                                </div>
                            </div>
                        </div>
                    </Card>

                    {/* Contact and Additional Info */}
                    <div className="lg:col-span-2 space-y-6">
                        <Card>
                            <div className="space-y-6">
                                <div>
                                    <h2 className="text-xl font-semibold text-neutral-900 mb-4">Contact Information</h2>
                                    <p className="text-sm text-neutral-500">
                                        Admin contact details and verification status
                                    </p>
                                </div>

                                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                    <div className="space-y-3">
                                        <div className="flex items-center gap-3">
                                            <div className="w-10 h-10 bg-accent/10 rounded-lg flex items-center justify-center">
                                                <Mail className="w-5 h-5 text-accent" />
                                            </div>
                                            <div>
                                                <p className="text-sm text-neutral-500">Email</p>
                                                <p className="font-medium text-neutral-900">{data.email}</p>
                                            </div>
                                        </div>
                                        <div className="flex items-center gap-3">
                                            <div className="w-10 h-10 bg-accent/10 rounded-lg flex items-center justify-center">
                                                <Phone className="w-5 h-5 text-accent" />
                                            </div>
                                            <div>
                                                <p className="text-sm text-neutral-500">Phone</p>
                                                <p className="font-medium text-neutral-900">{data.phoneNumber}</p>
                                            </div>
                                        </div>
                                    </div>

                                    <div className="space-y-3">
                                        <div className="flex items-center gap-3">
                                            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                                                <Calendar className="w-5 h-5 text-blue-600" />
                                            </div>
                                            <div>
                                                <p className="text-sm text-neutral-500">Created</p>
                                                <p className="font-medium text-neutral-900">
                                                    {new Date(data.createdAt).toLocaleDateString()}
                                                </p>
                                            </div>
                                        </div>
                                        <div className="flex items-center gap-3">
                                            <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                                                {data.isVerified ? (
                                                    <UserCheck className="w-5 h-5 text-green-600" />
                                                ) : (
                                                    <UserX className="w-5 h-5 text-red-600" />
                                                )}
                                            </div>
                                            <div>
                                                <p className="text-sm text-neutral-500">Status</p>
                                                <p className="font-medium text-neutral-900">
                                                    {data.isVerified ? "Verified" : "Unverified"}
                                                </p>
                                            </div>
                                        </div>
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
                                        <p className="text-sm text-neutral-500 mb-1">Account Created</p>
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
        </Layout>
    );
};

export default AdminDetail;
