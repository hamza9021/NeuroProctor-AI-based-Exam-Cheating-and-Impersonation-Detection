import {
    ApiError,
    ApiResponse,
    wrapperFunction,
    generateAccessAndRefreshToken,
} from "../Utils/index.utils.js";
import User from "../Models/user.models.js";
import Exam from "../Models/exam.models.js";


const createExamSession = wrapperFunction(async (req, res) => {
    const { examId, invigilatorId } = req.body;
    const user = req.user;

    if (!user) {
        throw new ApiError(404, "User Not Found");
    }

    if(user.role !== "admin"){
        throw new ApiError(403, "You are not authorized to view this data");
    }