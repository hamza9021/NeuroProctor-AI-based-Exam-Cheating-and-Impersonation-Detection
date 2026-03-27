import { ApiError } from "./api_error.utils.js";
import { Invigilator } from "../Models/invigilator.models.js";

const generateAccessAndRefreshToken = async (userID) => {
    try {
        const invigilator = await Invigilator.findById(userID);
        const accessToken = invigilator.generateAccessToken();
        const refreshToken = invigilator.generateRefreshToken();
        invigilator.refreshToken = refreshToken;
        await invigilator.save({ validateBeforeSave: false });
        return { accessToken, refreshToken };
    } catch (error) {
        throw new ApiError(
            500,
            "Something Went Wrong While Generating Access And Refresh Token"
        );
    }
};

export { generateAccessAndRefreshToken };
