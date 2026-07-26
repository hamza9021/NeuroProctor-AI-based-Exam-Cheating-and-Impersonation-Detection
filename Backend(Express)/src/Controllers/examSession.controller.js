import {
    ApiError,
    ApiResponse,
    wrapperFunction,
    generateAccessAndRefreshToken,
} from "../Utils/index.utils.js";
import User from "../Models/user.models.js";
import Exam from "../Models/exam.models.js";
import ExamSession from "../Models/examSession.models.js";


const createExamSession = wrapperFunction(async (req, res) => {
    const { examId, invigilatorId } = req.body;
    const user = req.user;

    if (!user) {
        throw new ApiError(404, "User Not Found");
    }

    if(user.role !== "admin"){
        throw new ApiError(403, "You are not authorized to view this data");
    }

    const invigilator = await User.findById(invigilatorId);

    if (!invigilator) {
        throw new ApiError(404, "Invigilator Not Found");
    }

    const exam = await Exam.findById(examId);

    if (!exam) {
        throw new ApiError(404, "Exam Not Found");
    }   

    const examSession = await ExamSession.create({
        examId,
        invigilatorId,
        mode: "offline",
        status: "active",
        sessionCode: Math.random().toString(36).substring(2, 15),
    });

    return res.json(new ApiResponse(200, examSession, "Exam Session Created Successfully"));
});


const getExamSessions = wrapperFunction(async (req, res) => {
    const user = req.user;

    if (!user) {
        throw new ApiError(404, "User Not Found");
    }

    if (user.role !== "admin") {
        throw new ApiError(403, "You are not authorized to view this data");
    }

    const page = Math.max(parseInt(req.query.page) || 1, 1);
    const limit = Math.max(parseInt(req.query.limit) || 10, 1);
    const skip = (page - 1) * limit;

    const search = req.query.search?.trim() || "";
    const sortBy = req.query.sortBy || "createdAt";
    const sortOrder = req.query.sortOrder === "asc" ? 1 : -1;

    const filter = {};

    if (search) {
        filter.$or = [
            { status: { $regex: search, $options: "i" } },
            { sessionCode: { $regex: search, $options: "i" } },
        ];
    }

    const [examSessions, total] = await Promise.all([
        ExamSession.find(filter)
            .populate("invigilatorId", "name email")
            .populate("examId", "title courseCode")
            .sort({ [sortBy]: sortOrder })
            .skip(skip)
            .limit(limit),
        ExamSession.countDocuments(filter),
    ]);

    return res.json(
        new ApiResponse(
            200,
            {
                examSessions,
                pagination: {
                    total,
                    page,
                    limit,
                    totalPages: Math.ceil(total / limit),
                    hasNextPage: page < Math.ceil(total / limit),
                    hasPrevPage: page > 1,
                },
            },
            "Exam Sessions Data"
        )
    );
});


const getInvigilatorSessions = wrapperFunction(async (req, res) => {
    const user = req.user;

    if (!user) {
        throw new ApiError(404, "User Not Found");
    }

    if (user.role !== "invigilator") {
        throw new ApiError(403, "You are not authorized to view this data");
    }

    const page = Math.max(parseInt(req.query.page) || 1, 1);
    const limit = Math.max(parseInt(req.query.limit) || 10, 1);
    const skip = (page - 1) * limit;


    const [examSessions, total] = await Promise.all([
        ExamSession.find({ invigilatorId: user._id })
            .sort({ createdAt: -1 })
            .skip(skip)
            .limit(limit),
        ExamSession.countDocuments({ invigilatorId: user._id }),
    ]);


    return res.json(
        new ApiResponse(
            200,
            {
                examSessions,
                pagination: {
                    total,
                    page,
                    limit,
                    totalPages: Math.ceil(total / limit),
                    hasNextPage: page < Math.ceil(total / limit),
                    hasPrevPage: page > 1,
                },
            },
            "Exam Sessions Data"
        )
    );
});



const getExamSession = wrapperFunction(async (req, res) => {
    const user = req.user;

    if (!user) {
        throw new ApiError(404, "User Not Found");
    }

    const examSession = await ExamSession.findById(req.params.id)
        .populate("invigilatorId", "name email")
        .populate("examId", "title courseCode");

    if (!examSession) {
        throw new ApiError(404, "Exam Session Not Found");
    }

    console.log("User:", user._id, user.role);
    console.log("Session invigilatorId:", examSession.invigilatorId);

    // Admin can view any session
    if (user.role === "admin") {
        return res.json(new ApiResponse(200, examSession, "Exam Session Data"));
    }

    // Invigilator can only view their assigned sessions
    if (user.role === "invigilator") {
        if (!examSession.invigilatorId) {
            throw new ApiError(403, "No invigilator assigned to this session");
        }
        if (examSession.invigilatorId._id.toString() !== user._id.toString()) {
            throw new ApiError(403, "You are not authorized to view this data");
        }
        return res.json(new ApiResponse(200, examSession, "Exam Session Data"));
    }

    throw new ApiError(403, "You are not authorized to view this data");
});


const deleteExamSession = wrapperFunction(async (req, res) => {
    const user = req.user;

    if (!user) {
        throw new ApiError(404, "User Not Found");
    }

    if (user.role !== "admin") {
        throw new ApiError(403, "You are not authorized to perform this action");
    }

    const examSession = await ExamSession.findById(req.params.id);

    if (!examSession) {
        throw new ApiError(404, "Exam Session Not Found");
    }

    await ExamSession.findByIdAndDelete(req.params.id);

    return res.json(
        new ApiResponse(200, {}, "Exam Session Deleted Successfully")
    );
});

const updateExamSessions = wrapperFunction(async (req, res) => {
    const user = req.user;

    if (!user) {
        throw new ApiError(404, "User Not Found");
    }

    if (user.role !== "admin") {
        throw new ApiError(403, "You are not authorized to perform this action");
    }

    const examSession = await ExamSession.findById(req.params.id);

    if (!examSession) {
        throw new ApiError(404, "Exam Session Not Found");
    }

    await ExamSession.findByIdAndUpdate(req.params.id, req.body, { new: true });

    return res.json(
        new ApiResponse(200, {}, "Exam Session Updated Successfully")
    );
});



export { createExamSession , getInvigilatorSessions, getExamSession, getExamSessions , deleteExamSession, updateExamSessions };
