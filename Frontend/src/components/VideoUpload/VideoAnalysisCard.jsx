import { Download, Clock, CheckCircle, AlertCircle, Video } from "lucide-react";
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
        <div className="border border-neutral-200 rounded-lg p-4 space-y-4">
            <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                        <Video className="w-5 h-5 text-blue-600" />
                    </div>
                    <div>
                        <h4 className="font-medium text-neutral-900">Video Analysis</h4>
                        <p className="text-xs text-neutral-500">
                            Session: {videoAnalysis.sessionId?.slice(0, 8)}...
                        </p>
                    </div>
                </div>
                {getStatusBadge(videoAnalysis.status)}
            </div>

            <div className="grid grid-cols-2 gap-4 text-sm">
                <div className="flex items-center gap-2">
                    <Clock className="w-4 h-4 text-neutral-400" />
                    <span className="text-neutral-600">Processing Time:</span>
                    <span className="font-medium text-neutral-900">
                        {formatTime(videoAnalysis.processingTime)}
                    </span>
                </div>
                <div className="flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-neutral-400" />
                    <span className="text-neutral-600">Completed:</span>
                    <span className="font-medium text-neutral-900">
                        {formatDate(videoAnalysis.completedAt)}
                    </span>
                </div>
            </div>

            {videoAnalysis.status === "completed" && (
                <div className="space-y-3 pt-3 border-t border-neutral-200">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm font-medium text-neutral-900">Original Video</p>
                            <p className="text-xs text-neutral-500">Unprocessed footage</p>
                        </div>
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={() => window.open(videoAnalysis.originalVideo, "_blank")}
                        >
                            <Download className="w-4 h-4 mr-2" />
                            Download
                        </Button>
                    </div>

                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm font-medium text-neutral-900">Processed Video</p>
                            <p className="text-xs text-neutral-500">AI-annotated footage</p>
                        </div>
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={() => window.open(videoAnalysis.processedVideo, "_blank")}
                        >
                            <Download className="w-4 h-4 mr-2" />
                            Download
                        </Button>
                    </div>
                </div>
            )}

            {videoAnalysis.status === "failed" && videoAnalysis.errorMessage && (
                <div className="flex items-start gap-2 p-3 bg-red-50 border border-red-200 rounded-lg">
                    <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
                    <p className="text-sm text-red-800">{videoAnalysis.errorMessage}</p>
                </div>
            )}
        </div>
    );
}
