import {
    ApiError,
    ApiResponse,
    wrapperFunction,
} from "../Utils/index.utils.js";
import VideoAnalysis from "../Models/videoAnalysis.models.js";

const createVideoAnalysis = wrapperFunction(async (req, res) => {
    const { sessionId, examId, invigilatorId, originalVideo, processedVideo, processingTime } = req.body;
    const user = req.user;

    console.log("Creating video analysis with data:", { sessionId, examId, invigilatorId, originalVideo, processedVideo, processingTime });

    if (!user) {
        throw new ApiError(404, "User Not Found");
    }

    if (user.role !== "invigilator" && user.role !== "admin") {
        throw new ApiError(403, "You are not authorized to create video analysis");
    }

    try {
        const videoAnalysis = await VideoAnalysis.create({
            sessionId,
            examId,
            invigilatorId,
            originalVideo,
            processedVideo,
            status: "completed",
            processingTime,
            uploadedAt: new Date(),
            completedAt: new Date(),
        });

        return res.json(new ApiResponse(200, videoAnalysis, "Video Analysis Created Successfully"));
    } catch (error) {
        console.error("Error creating video analysis:", error);
        throw new ApiError(500, `Failed to create video analysis: ${error.message}`);
    }
});

const getVideoAnalysisBySession = wrapperFunction(async (req, res) => {
    const { sessionId } = req.params;
    const user = req.user;

    if (!user) {
        throw new ApiError(404, "User Not Found");
    }

    const videoAnalysis = await VideoAnalysis.findOne({ sessionId });

    if (!videoAnalysis) {
        throw new ApiError(404, "Video Analysis Not Found");
    }

    // Invigilators can only view their own sessions
    if (user.role === "invigilator" && videoAnalysis.invigilatorId.toString() !== user._id.toString()) {
        throw new ApiError(403, "You are not authorized to view this video analysis");
    }

    return res.json(new ApiResponse(200, videoAnalysis, "Video Analysis Data"));
});

const getVideoAnalysesByInvigilator = wrapperFunction(async (req, res) => {
    const user = req.user;

    if (!user) {
        throw new ApiError(404, "User Not Found");
    }

    if (user.role !== "invigilator") {
        throw new ApiError(403, "You are not authorized to view video analyses");
    }

    const videoAnalyses = await VideoAnalysis.find({ invigilatorId: user._id })
        .sort({ createdAt: -1 });

    return res.json(new ApiResponse(200, videoAnalyses, "Video Analyses Data"));
});

const updateVideoAnalysis = wrapperFunction(async (req, res) => {
    const { id } = req.params;
    const { status, errorMessage } = req.body;
    const user = req.user;

    if (!user) {
        throw new ApiError(404, "User Not Found");
    }

    if (user.role !== "invigilator" && user.role !== "admin") {
        throw new ApiError(403, "You are not authorized to update video analysis");
    }

    const videoAnalysis = await VideoAnalysis.findById(id);

    if (!videoAnalysis) {
        throw new ApiError(404, "Video Analysis Not Found");
    }

    // Invigilators can only update their own sessions
    if (user.role === "invigilator" && videoAnalysis.invigilatorId.toString() !== user._id.toString()) {
        throw new ApiError(403, "You are not authorized to update this video analysis");
    }

    const updateData = { status };
    if (errorMessage) {
        updateData.errorMessage = errorMessage;
    }
    if (status === "completed") {
        updateData.completedAt = new Date();
    }

    const updatedVideoAnalysis = await VideoAnalysis.findByIdAndUpdate(
        id,
        updateData,
        { new: true }
    );

    return res.json(new ApiResponse(200, updatedVideoAnalysis, "Video Analysis Updated Successfully"));
});

const deleteVideoAnalysis = wrapperFunction(async (req, res) => {
    const { id } = req.params;
    const user = req.user;

    if (!user) {
        throw new ApiError(404, "User Not Found");
    }

    if (user.role !== "admin") {
        throw new ApiError(403, "You are not authorized to delete video analysis");
    }

    const videoAnalysis = await VideoAnalysis.findByIdAndDelete(id);

    if (!videoAnalysis) {
        throw new ApiError(404, "Video Analysis Not Found");
    }

    return res.json(new ApiResponse(200, null, "Video Analysis Deleted Successfully"));
});

export {
    createVideoAnalysis,
    getVideoAnalysisBySession,
    getVideoAnalysesByInvigilator,
    updateVideoAnalysis,
    deleteVideoAnalysis,
};
