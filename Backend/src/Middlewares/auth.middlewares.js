import jwt from "jsonwebtoken";
import { wrapperFunction } from "../Utils/async_wrap.utils.js";
import { ApiError } from "../Utils/api_error.utils.js";
import { Invigilator } from "../Models/invigilator.models.js";

const verifyJWT = wrapperFunction(async (req, _, next) => {
    const token = req.cookies.accessToken;

    if (!token) {
        throw new ApiError(401, "Token Not Found");
    }

    const decodedToken = jwt.verify(token, process.env.ACCESS_TOKEN_SECRET);

    const invigilator = await Invigilator.findById(decodedToken._id).select(
        "-password -refreshToken"
    );

    if (!invigilator) {
        throw new ApiError(401, "Invalid Token");
    }
    req.invigilator = invigilator;
    next();
});

export { verifyJWT };
