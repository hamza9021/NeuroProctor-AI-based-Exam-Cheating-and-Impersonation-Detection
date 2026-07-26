import mongoose from "mongoose";

const videoAnalysisSchema = new mongoose.Schema(
    {
        sessionId: {
            type: mongoose.Schema.Types.ObjectId,
            ref: "ExamSession",
            required: true,
            index: true,
        },
        examId: {
            type: mongoose.Schema.Types.ObjectId,
            ref: "Exam",
            required: true,
            index: true,
        },
        invigilatorId: {
            type: mongoose.Schema.Types.ObjectId,
            ref: "User",
            required: true,
            index: true,
        },
        originalVideo: {
            type: String,
            required: true,
        },
        processedVideo: {
            type: String,
            required: true,
        },
        status: {
            type: String,
            enum: ["pending", "processing", "completed", "failed"],
            default: "pending",
            index: true,
        },
        processingTime: {
            type: Number,
            default: 0,
        },
        uploadedAt: {
            type: Date,
            default: Date.now,
        },
        completedAt: {
            type: Date,
        },
        errorMessage: {
            type: String,
        },
    },
    {
        timestamps: true,
    }
);

// Index for efficient queries
videoAnalysisSchema.index({ sessionId: 1, status: 1 });
videoAnalysisSchema.index({ invigilatorId: 1, createdAt: -1 });

const VideoAnalysis = mongoose.model("VideoAnalysis", videoAnalysisSchema);

export default VideoAnalysis;
