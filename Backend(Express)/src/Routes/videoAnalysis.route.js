import express from "express";
import { verifyJWT } from "../Middleware/auth.middleware.js";
import {
    createVideoAnalysis,
    getVideoAnalysisBySession,
    getVideoAnalysesByInvigilator,
    updateVideoAnalysis,
    deleteVideoAnalysis,
} from "../Controllers/videoAnalysis.controller.js";

const router = express.Router();

// All routes require JWT authentication
router.use(verifyJWT);

// Create video analysis (called by FastAPI service)
router.post("/", createVideoAnalysis);

// Get video analysis by session ID
router.get("/session/:sessionId", getVideoAnalysisBySession);

// Get all video analyses for current invigilator
router.get("/invigilator", getVideoAnalysesByInvigilator);

// Update video analysis status
router.put("/:id", updateVideoAnalysis);

// Delete video analysis (admin only)
router.delete("/:id", deleteVideoAnalysis);

export default router;
