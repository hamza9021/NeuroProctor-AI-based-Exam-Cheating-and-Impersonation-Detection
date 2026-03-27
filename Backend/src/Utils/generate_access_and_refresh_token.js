import { ApiError } from "./api_error.utils.js";
import { Invigilator } from "../Models/invigilator.models.js";

const generateAccessAndRefreshToken = async (userID) => {
    try {
        const user = await Invigilator.findById(userID);
        const accessToken = user.generateAccessToken();
        const refreshToken = user.generateRefreshToken();
        user.refreshToken = refreshToken;
        await user.save({ validateBeforeSave: false });
        return { accessToken, refreshToken };
    } catch (error) {
        throw new ApiError(
            500,
            "Something Went Wrong While Generating Access And Refresh Token"
        );
    }
};

export { generateAccessAndRefreshToken };
