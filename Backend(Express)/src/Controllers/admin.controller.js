import {
    ApiError,
    ApiResponse,
    wrapperFunction,
    generateAccessAndRefreshToken,
} from "../Utils/index.utils.js";
import User from "../Models/user.models.js";
import Exam from "../Models/exam.models.js";

const getAdmins = wrapperFunction(async (req, res) => {
    const user = req.user;

    if (!user) {
        throw new ApiError(404, "User Not Found");
    }

    if (user.role !== "admin") {
        throw new ApiError(403, "You are not authorized to view this data");
    }

    const page = parseInt(req.query.page) || 1;
    const limit = parseInt(req.query.limit) || 10;
    const search = req.query.search?.trim() || "";

    const skip = (page - 1) * limit;

    const filter = {
        role: "admin",
    };

    if (search) {
        filter.$or = [
            {
                fullName: {
                    $regex: search,
                    $options: "i",
                },
            },
            {
                email: {
                    $regex: search,
                    $options: "i",
                },
            },
        ];
    }

    const [admins, total] = await Promise.all([
        User.find(filter)
            .skip(skip)
            .limit(limit),
        User.countDocuments(filter),
    ]);

    return res.json(
        new ApiResponse(
            200,
            {
                admins,
                pagination: {
                    total,
                    page,
                    limit,
                    totalPages: Math.ceil(total / limit),
                },
            },
            "Admins Data"
        )
    );
});

const getAdmin = wrapperFunction(async (req, res) => {
    const user = req.user;

    if (!user) {
        throw new ApiError(404, "User Not Found");
    }

    if (user.role !== "admin") {
        throw new ApiError(403, "You are not authorized to view this data");
    }

    const admin = await User.findById(req.params.id);

    return res.json(new ApiResponse(200, admin, "Admin Data"));
})

const getInvigilators = wrapperFunction(async (req, res) => {
    const user = req.user;

    if (!user) {
        throw new ApiError(404, "User Not Found");
    }

    if (user.role !== "admin") {
        throw new ApiError(403, "You are not authorized to view this data");
    }

    const page = parseInt(req.query.page) || 1;
    const limit = parseInt(req.query.limit) || 10;
    const search = req.query.search?.trim() || "";

    const skip = (page - 1) * limit;

    const filter = {
        role: "invigilator",
    };

    if (search) {
        filter.$or = [
            {
                fullName: {
                    $regex: search,
                    $options: "i",
                },
            },
            {
                email: {
                    $regex: search,
                    $options: "i",
                },
            },
        ];
    }

    const [invigilators, total] = await Promise.all([
        User.find(filter)
            .skip(skip)
            .limit(limit),
        User.countDocuments(filter),
    ]);

    return res.json(
        new ApiResponse(
            200,
            {
                invigilators,
                pagination: {
                    total,
                    page,
                    limit,
                    totalPages: Math.ceil(total / limit),
                },
            },
            "Invigilators Data"
        )
    );
});

const getInvigilator = wrapperFunction(async (req, res) => {
    const user = req.user;

    if (!user) {
        throw new ApiError(404, "User Not Found");
    }

    if (user.role !== "admin") {
        throw new ApiError(403, "You are not authorized to view this data");
    }

    const invigilator = await User.findById(req.params.id);

    return res.json(new ApiResponse(200, invigilator, "Invigilator Data"));
});

const getExams = wrapperFunction(async (req, res) => {
    const user = req.user;

    if (!user) {
        throw new ApiError(404, "User Not Found");
    }

    if (user.role !== "admin") {
        throw new ApiError(403, "You are not authorized to view this data");
    }

    const page = parseInt(req.query.page) || 1;
    const limit = parseInt(req.query.limit) || 10;
    const search = req.query.search?.trim() || "";

    const skip = (page - 1) * limit;

    const filter = {};

    if (search) {
        filter.title = {
            $regex: search,
            $options: "i",
        };
    }

    const [exams, total] = await Promise.all([
        Exam.find(filter)
            .populate("createdBy")
            .skip(skip)
            .limit(limit),
        Exam.countDocuments(filter),
    ]);

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
                },
            },
            "Exams Data"
        )
    );
});

const verifyInvigilator = wrapperFunction(async (req, res) => {
    const user = req.user;

    if (!user) {
        throw new ApiError(404, "User Not Found");
    }

    if (user.role !== "admin") {
        throw new ApiError(403, "You are not authorized to view this data");
    }

    const invigilator = await User.findById(req.params.id);

    if (!invigilator) {
        throw new ApiError(404, "Invigilator Not Found");
    }

    if (invigilator.role !== "invigilator") {
        throw new ApiError(403, "You are not authorized to verify this invigilator");
    }

    if (invigilator.isVerified) {
        throw new ApiError(400, "Invigilator is already verified");
    }

    invigilator.isVerified = true;
    await invigilator.save();

    return res.json(new ApiResponse(200, invigilator, "Invigilator Verified Successfully"));
});

const deleteInvigilator = wrapperFunction(async (req, res) => {
    const user = req.user;

    if (!user) {
        throw new ApiError(404, "User Not Found");
    }

    if (user.role !== "admin") {
        throw new ApiError(403, "You are not authorized to perform this action");
    }

    const invigilator = await User.findById(req.params.id);

    if (!invigilator) {
        throw new ApiError(404, "Invigilator Not Found");
    }

    if (invigilator.role !== "invigilator") {
        throw new ApiError(403, "You are not authorized to delete this invigilator");
    }

    await Exam.deleteMany({ createdBy: invigilator._id });

    await User.findByIdAndDelete(invigilator._id);

    return res.json(
        new ApiResponse(200, {}, "Invigilator Deleted Successfully")
    );
});

const getExam = wrapperFunction(async (req, res) => {
    const user = req.user;

    if (!user) {
        throw new ApiError(404, "User Not Found");
    }

    if (user.role !== "admin") {
        throw new ApiError(403, "You are not authorized to view this data");
    }

    const exam = await Exam.findById(req.params.id).populate("createdBy");

    return res.json(new ApiResponse(200, exam, "Exam Data"));
});



export { getAdmins, getAdmin, getInvigilators, getInvigilator, getExams, verifyInvigilator, deleteInvigilator ,getExam};