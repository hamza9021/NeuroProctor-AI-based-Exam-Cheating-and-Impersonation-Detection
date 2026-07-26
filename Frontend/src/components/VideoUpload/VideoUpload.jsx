import { useState, useCallback } from "react";
import { useMutation } from "@tanstack/react-query";
import { Upload, X, Loader2, CheckCircle, AlertCircle } from "lucide-react";
import videoAnalysisApis from "../../apis/VideoAnalysis/videoAnalysis.apis.js";
import Button from "../ui/Button";

export default function VideoUpload({ sessionId, examId, onSuccess }) {
    const [isDragging, setIsDragging] = useState(false);
    const [selectedFile, setSelectedFile] = useState(null);
    const [uploadProgress, setUploadProgress] = useState(0);
    const [error, setError] = useState(null);

    const { mutate: processVideo, isPending } = useMutation({
        mutationFn: (file) => videoAnalysisApis.processVideo(file, sessionId, examId),
        onSuccess: (data) => {
            setUploadProgress(100);
            onSuccess?.(data);
            resetForm();
        },
        onError: (err) => {
            setError(err.response?.data?.message || "Failed to process video");
            setUploadProgress(0);
        },
    });

    const resetForm = () => {
        setSelectedFile(null);
        setUploadProgress(0);
        setError(null);
    };

    const handleDragOver = useCallback((e) => {
        e.preventDefault();
        setIsDragging(true);
    }, []);

    const handleDragLeave = useCallback((e) => {
        e.preventDefault();
        setIsDragging(false);
    }, []);

    const handleDrop = useCallback((e) => {
        e.preventDefault();
        setIsDragging(false);

        const files = Array.from(e.dataTransfer.files);
        const videoFile = files.find((file) => file.type.startsWith("video/"));

        if (videoFile) {
            setSelectedFile(videoFile);
            setError(null);
        } else {
            setError("Please upload a valid video file (MP4, AVI, MOV)");
        }
    }, []);

    const handleFileSelect = (e) => {
        const file = e.target.files[0];
        if (file) {
            if (file.type.startsWith("video/")) {
                setSelectedFile(file);
                setError(null);
            } else {
                setError("Please upload a valid video file (MP4, AVI, MOV)");
            }
        }
    };

    const handleUpload = () => {
        if (selectedFile) {
            setError(null);
            setUploadProgress(0);
            processVideo(selectedFile);
        }
    };

    const handleRemoveFile = () => {
        setSelectedFile(null);
        setError(null);
    };

    const formatFileSize = (bytes) => {
        if (bytes === 0) return "0 Bytes";
        const k = 1024;
        const sizes = ["Bytes", "KB", "MB", "GB"];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return Math.round(bytes / Math.pow(k, i) * 100) / 100 + " " + sizes[i];
    };

    return (
        <div className="space-y-4">
            <div
                className={`relative border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
                    isDragging
                        ? "border-accent bg-accent/5"
                        : "border-neutral-300 hover:border-neutral-400"
                }`}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
            >
                <input
                    type="file"
                    accept="video/mp4,video/avi,video/quicktime,video/x-msvideo"
                    onChange={handleFileSelect}
                    className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                    disabled={isPending}
                />

                {!selectedFile ? (
                    <div className="space-y-3">
                        <div className="flex justify-center">
                            <Upload className="w-12 h-12 text-neutral-400" />
                        </div>
                        <div>
                            <p className="text-sm font-medium text-neutral-900">
                                Drag & drop video here
                            </p>
                            <p className="text-xs text-neutral-500 mt-1">
                                or click to browse
                            </p>
                        </div>
                        <p className="text-xs text-neutral-400">
                            Supported formats: MP4, AVI, MOV (Max 500MB)
                        </p>
                    </div>
                ) : (
                    <div className="space-y-3">
                        <div className="flex items-center justify-between">
                            <div className="flex items-center gap-3 flex-1 min-w-0">
                                <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center flex-shrink-0">
                                    <Upload className="w-5 h-5 text-blue-600" />
                                </div>
                                <div className="flex-1 min-w-0 text-left">
                                    <p className="text-sm font-medium text-neutral-900 truncate">
                                        {selectedFile.name}
                                    </p>
                                    <p className="text-xs text-neutral-500">
                                        {formatFileSize(selectedFile.size)}
                                    </p>
                                </div>
                            </div>
                            {!isPending && (
                                <button
                                    onClick={handleRemoveFile}
                                    className="p-2 text-neutral-400 hover:text-neutral-600 hover:bg-neutral-100 rounded-lg transition-colors"
                                >
                                    <X className="w-4 h-4" />
                                </button>
                            )}
                        </div>

                        {isPending && (
                            <div className="space-y-2">
                                <div className="flex items-center gap-2">
                                    <Loader2 className="w-4 h-4 animate-spin text-accent" />
                                    <p className="text-xs text-neutral-600">
                                        Processing video...
                                    </p>
                                </div>
                                <div className="w-full bg-neutral-200 rounded-full h-2">
                                    <div
                                        className="bg-accent h-2 rounded-full transition-all duration-300"
                                        style={{ width: `${uploadProgress}%` }}
                                    />
                                </div>
                            </div>
                        )}
                    </div>
                )}
            </div>

            {error && (
                <div className="flex items-start gap-2 p-3 bg-red-50 border border-red-200 rounded-lg">
                    <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
                    <p className="text-sm text-red-800">{error}</p>
                </div>
            )}

            {selectedFile && !isPending && (
                <Button
                    onClick={handleUpload}
                    className="w-full"
                    disabled={!selectedFile}
                >
                    Process Video
                </Button>
            )}
        </div>
    );
}
