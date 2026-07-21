import { useParams } from "react-router-dom";
import {
    useQuery,
    useMutation,
    useQueryClient,
} from "@tanstack/react-query";
import studentApis from "../../apis/Students/student.apis.js";
import { ArrowLeft, Upload, CheckCircle, AlertCircle } from "lucide-react";
import Button from "../ui/Button";
import Badge from "../ui/Badge";
import Spinner from "../ui/Spinner";
import ErrorState from "../ui/ErrorState";
import Skeleton from "../ui/Skeleton";
import Card from "../ui/Card";
import Layout from "../Layout/Layout";

const StudentDetail = () => {
    const { studentId } = useParams();
    const queryClient = useQueryClient();

    const {
        data,
        isLoading,
        isError,
        error,
    } = useQuery({
        queryKey: ["student", studentId],
        queryFn: () => studentApis.getStudent(studentId),
    });

    const {
        mutate,
        isPending,
        isError: faceError,
        error: faceErrorMessage,
    } = useMutation({
        mutationFn: (formData) =>
            studentApis.updateFace(studentId, formData),

        onSuccess: () => {
            queryClient.invalidateQueries({
                queryKey: ["student", studentId],
            });
        },
    });

    const handleUpload = (e, pose) => {
        e.preventDefault();

        const file = e.target.image.files[0];

        if (!file) {
            alert("Please select an image.");
            return;
        }

        const formData = new FormData();
        formData.append("image", file);
        formData.append("pose", pose);

        mutate(formData);

        e.target.reset();
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
                title="Failed to load student"
                description={error.message || "Please try again later."}
            />
        );
    }

    return (
        <Layout title="Student Details">
            <div className="space-y-6">
                {/* Header */}
                <div className="flex items-center gap-4">
                    <button
                        onClick={() => window.history.back()}
                        className="p-2 text-neutral-400 hover:text-neutral-600 hover:bg-neutral-100 rounded-lg transition-colors"
                    >
                        <ArrowLeft className="w-5 h-5" />
                    </button>
                    <div>
                        <h1 className="text-2xl font-semibold text-neutral-900">Student Details</h1>
                        <p className="text-sm text-neutral-500 mt-1">View and manage student information</p>
                    </div>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Profile Card */}
                    <Card>
                        <div className="flex flex-col items-center text-center">
                            <div className="w-32 h-32 rounded-full bg-neutral-200 overflow-hidden mb-4">
                                <img
                                    src={data.profile_image}
                                    alt={data.full_name}
                                    className="w-full h-full object-cover"
                                />
                            </div>
                            <h2 className="text-xl font-semibold text-neutral-900">{data.full_name}</h2>
                            <p className="text-sm text-neutral-500 mt-1">{data.email}</p>
                            
                            <div className="w-full mt-6 pt-6 border-t border-neutral-200 space-y-3">
                                <div className="flex justify-between text-sm">
                                    <span className="text-neutral-500">Registration</span>
                                    <span className="font-medium text-neutral-900">{data.registration_number}</span>
                                </div>
                                <div className="flex justify-between text-sm">
                                    <span className="text-neutral-500">Department</span>
                                    <span className="font-medium text-neutral-900">{data.department}</span>
                                </div>
                                <div className="flex justify-between text-sm">
                                    <span className="text-neutral-500">Semester</span>
                                    <span className="font-medium text-neutral-900">{data.semester}</span>
                                </div>
                            </div>
                        </div>
                    </Card>

                    {/* Face Embeddings */}
                    <div className="lg:col-span-2 space-y-6">
                        <div>
                            <h2 className="text-xl font-semibold text-neutral-900 mb-4">Face Embeddings</h2>
                            <p className="text-sm text-neutral-500 mb-6">
                                Upload face images for different poses to enable facial recognition during exams.
                            </p>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {data.face_embeddings?.map((face) => (
                                <Card key={face.pose} padding="md">
                                    <div className="flex items-center justify-between mb-4">
                                        <h3 className="font-semibold text-neutral-900 capitalize">{face.pose}</h3>
                                        {face.quality_score > 0 ? (
                                            <Badge variant="success">Embedded</Badge>
                                        ) : (
                                            <Badge variant="error">Not Embedded</Badge>
                                        )}
                                    </div>

                                    {face.quality_score > 0 ? (
                                        <div className="space-y-3">
                                            <div className="flex items-center gap-2 text-sm text-green-600">
                                                <CheckCircle className="w-4 h-4" />
                                                <span>Successfully embedded</span>
                                            </div>
                                            <div className="flex justify-between text-sm">
                                                <span className="text-neutral-500">Quality Score</span>
                                                <span className="font-medium text-neutral-900">{face.quality_score}</span>
                                            </div>
                                            {face.captured_at && (
                                                <div className="flex justify-between text-sm">
                                                    <span className="text-neutral-500">Captured At</span>
                                                    <span className="font-medium text-neutral-900">
                                                        {new Date(face.captured_at).toLocaleString()}
                                                    </span>
                                                </div>
                                            )}
                                        </div>
                                    ) : (
                                        <form
                                            onSubmit={(e) => handleUpload(e, face.pose)}
                                            className="space-y-4"
                                        >
                                            <div>
                                                <label className="block text-sm font-medium text-neutral-700 mb-2">
                                                    Upload {face.pose} image
                                                </label>
                                                <input
                                                    type="file"
                                                    name="image"
                                                    accept="image/*"
                                                    className="w-full px-3 py-2 border border-neutral-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-accent focus:border-transparent"
                                                />
                                            </div>

                                            <Button
                                                type="submit"
                                                size="sm"
                                                isLoading={isPending}
                                                className="w-full"
                                            >
                                                <Upload className="w-4 h-4 mr-2" />
                                                Upload {face.pose}
                                            </Button>

                                            {faceError && (
                                                <div className="flex items-center gap-2 text-sm text-red-600">
                                                    <AlertCircle className="w-4 h-4" />
                                                    <span>{faceErrorMessage.message}</span>
                                                </div>
                                            )}
                                        </form>
                                    )}
                                </Card>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        </Layout>
    );
};

export default StudentDetail;