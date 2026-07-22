import {
    ApiError,
    ApiResponse,
    wrapperFunction,
    generateAccessAndRefreshToken,
} from "../Utils/index.utils.js";
import User from "../Models/user.models.js";
import Exam from "../Models/exam.models.js";




const createExam = wrapperFunction(async (req, res) => {
    const { title, description, courseName, courseCode, duration, startTime, endTime } = req.body;
    const user = req.user;

    if (!user) {
        throw new ApiError(404, "User Not Found");
    }

    const exam = await Exam.create({
        title,
        description,
        courseName,
        courseCode,
        duration,
        startTime,
        endTime,
        createdBy: user._id,
    });

    return res.json(new ApiResponse(200, exam, "Exam Created Successfully"));
});

const getExams = wrapperFunction(async (req, res) => {
    const user = req.user;

    if (!user) {
        throw new ApiError(404, "User Not Found");
    }

    const page = Math.max(parseInt(req.query.page) || 1, 1);
    const limit = Math.max(parseInt(req.query.limit) || 10, 1);
    const search = req.query.search || "";
    const sortBy = req.query.sortBy || "createdAt";
    const sortOrder = req.query.sortOrder === "asc" ? 1 : -1;

    const filter = {
        createdBy: user._id,
    };

    if (search) {
        filter.$or = [
            { title: { $regex: search, $options: "i" } },
            { courseName: { $regex: search, $options: "i" } },
            { courseCode: { $regex: search, $options: "i" } },
            { status: { $regex: search, $options: "i" } },
        ];
    }

    const total = await Exam.countDocuments(filter);

    const exams = await Exam.find(filter)
        .sort({ [sortBy]: sortOrder })
        .skip((page - 1) * limit)
        .limit(limit);

    return res.json(
        new ApiResponse(
            200,
            {
                exams,
                pagination: {
                    total,
                    page,
                    limit,
                    totalPages: Math.ceil(total / limit),
                    hasNextPage: page < Math.ceil(total / limit),
                    hasPrevPage: page > 1,
                },
            },
            "Exams fetched successfully"
        )
    );
});

const deleteExam = wrapperFunction(async (req, res) => {
    const user = req.user;

    if (!user) {
        throw new ApiError(404, "User Not Found");
    }

    const exam = await Exam.findById(req.params.id);

    if (!exam) {
        throw new ApiError(404, "Exam Not Found");
    }

    if (exam.createdBy.toString() !== user._id.toString()) {
        throw new ApiError(403, "You are not authorized to delete this exam");
    }

    await Exam.findByIdAndDelete(req.params.id);

    return res.json(new ApiResponse(200, {}, "Exam Deleted Successfully"));
})

const cancelExam = wrapperFunction(async (req, res) => {
    const user = req.user;

    if (!user) {
        throw new ApiError(404, "User Not Found");
    }

    const exam = await Exam.findById(req.params.id);

    if (!exam) {
        throw new ApiError(404, "Exam Not Found");
    }

    if (exam.createdBy.toString() !== user._id.toString()) {
        throw new ApiError(403, "You are not authorized to cancel this exam");
    }

    await Exam.findByIdAndUpdate(req.params.id, { status: "cancelled" }, { new: true });

    return res.json(new ApiResponse(200, {}, "Exam Cancelled Successfully"));
})

const getExamsByStatus = wrapperFunction(async (req, res) => {
    const user = req.user;

    if (!user) {
        throw new ApiError(404, "User Not Found");
    }

    const exams = await Exam.find({ createdBy: user._id, status: req.params.status });

    return res.json(new ApiResponse(200, exams, "Exams Data"));
});

const getExam = wrapperFunction(async (req, res) => {
    const user = req.user;

    if (!user) {
        throw new ApiError(404, "User Not Found");
    }

    const exam = await Exam.findById(req.params.id);

    if (!exam) {
        throw new ApiError(404, "Exam Not Found");
    }

    if (exam.createdBy.toString() !== user._id.toString()) {
        throw new ApiError(403, "You are not authorized to view this exam");
    }

    return res.json(new ApiResponse(200, exam, "Exams Data"));
})

const updateExam = wrapperFunction(async (req, res) => {
    const user = req.user;

    if (!user) {
        throw new ApiError(404, "User Not Found");
    }

    const exam = await Exam.findById(req.params.id);

    if (!exam) {
        throw new ApiError(404, "Exam Not Found");
    }

    if (exam.createdBy.toString() !== user._id.toString()) {
        throw new ApiError(403, "You are not authorized to update this exam");
    }

    await Exam.findByIdAndUpdate(req.params.id, req.body, { new: true });

    return res.json(new ApiResponse(200, {}, "Exam Updated Successfully"));
})

export { createExam, getExams, updateExam, deleteExam, cancelExam, getExamsByStatus, getExam };