import { Download, Clock, CheckCircle, AlertCircle, Video, Play, FileVideo, ExternalLink } from "lucide-react";
import Button from "../ui/Button";
import Badge from "../ui/Badge";

export default function VideoAnalysisCard({ videoAnalysis }) {
    const getStatusBadge = (status) => {
        switch (status) {
            case "completed":
                return <Badge variant="success">Completed</Badge>;
            case "processing":
                return <Badge variant="neutral">Processing</Badge>;
            case "failed":
                return <Badge variant="destructive">Failed</Badge>;
            default:
                return <Badge variant="neutral">Pending</Badge>;
        }
    };

    const formatTime = (seconds) => {
        if (!seconds) return "N/A";
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins}m ${secs}s`;
    };

    const formatDate = (dateString) => {
        if (!dateString) return "N/A";
        return new Date(dateString).toLocaleString();
    };

    return (
        <div className="bg-white rounded-xl border border-neutral-200 shadow-sm overflow-hidden">
            <div className="px-5 py-4 border-b border-neutral-200 bg-gradient-to-r from-neutral-50 to-white">
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 bg-accent/10 rounded-lg flex items-center justify-center">
                            <Video className="w-5 h-5 text-accent" />
                        </div>
                        <div>
                            <h4 className="font-semibold text-neutral-900">Video Analysis Results</h4>
                            <p className="text-xs text-neutral-500">
                                Session: {videoAnalysis.sessionId?.slice(0, 8)}...
                            </p>
                        </div>
                    </div>
                    {getStatusBadge(videoAnalysis.status)}
                </div>
            </div>

            <div className="p-5 space-y-4">
                <div className="grid grid-cols-2 gap-4">
                    <div className="flex items-center gap-3 p-3 bg-neutral-50 rounded-lg">
                        <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
                            <Clock className="w-4 h-4 text-blue-600" />
                        </div>
                        <div>
                            <p className="text-xs text-neutral-500">Processing Time</p>
                            <p className="text-sm font-semibold text-neutral-900">
                                {formatTime(videoAnalysis.processingTime)}
                            </p>
                        </div>
                    </div>
                    <div className="flex items-center gap-3 p-3 bg-neutral-50 rounded-lg">
                        <div className="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center">
                            <CheckCircle className="w-4 h-4 text-green-600" />
                        </div>
                        <div>
                            <p className="text-xs text-neutral-500">Completed</p>
                            <p className="text-sm font-semibold text-neutral-900">
                                {formatDate(videoAnalysis.completedAt)}
                            </p>
                        </div>
                    </div>
                </div>

                {videoAnalysis.status === "completed" && (
                    <div className="space-y-3 pt-4 border-t border-neutral-200">
                        <div className="p-4 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border border-blue-100">
                            <div className="flex items-center justify-between">
                                <div className="flex items-center gap-3">
                                    <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                                        <FileVideo className="w-5 h-5 text-blue-600" />
                                    </div>
                                    <div>
                                        <p className="text-sm font-semibold text-neutral-900">Original Video</p>
                                        <p className="text-xs text-neutral-600">Unprocessed exam footage</p>
                                    </div>
                                </div>
                                <Button
                                    variant="outline"
                                    size="sm"
                                    onClick={() => window.open(videoAnalysis.originalVideo, "_blank")}
                                    className="gap-2"
                                >
                                    <ExternalLink className="w-4 h-4" />
                                    View
                                </Button>
                            </div>
                        </div>

                        <div className="p-4 bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg border border-green-100">
                            <div className="flex items-center justify-between">
                                <div className="flex items-center gap-3">
                                    <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                                        <Play className="w-5 h-5 text-green-600" />
                                    </div>
                                    <div>
                                        <p className="text-sm font-semibold text-neutral-900">Processed Video</p>
                                        <p className="text-xs text-neutral-600">AI-annotated with detection results</p>
                                    </div>
                                </div>
                                <Button
                                    variant="outline"
                                    size="sm"
                                    onClick={() => window.open(videoAnalysis.processedVideo, "_blank")}
                                    className="gap-2"
                                >
                                    <ExternalLink className="w-4 h-4" />
                                    View
                                </Button>
                            </div>
                        </div>
                    </div>
                )}

                {videoAnalysis.status === "failed" && videoAnalysis.errorMessage && (
                    <div className="flex items-start gap-3 p-4 bg-red-50 border border-red-200 rounded-lg">
                        <div className="flex-shrink-0 w-8 h-8 bg-red-100 rounded-lg flex items-center justify-center mt-0.5">
                            <AlertCircle className="w-4 h-4 text-red-600" />
                        </div>
                        <div>
                            <p className="text-sm font-semibold text-red-900">Processing Failed</p>
                            <p className="text-sm text-red-800 mt-1">{videoAnalysis.errorMessage}</p>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
