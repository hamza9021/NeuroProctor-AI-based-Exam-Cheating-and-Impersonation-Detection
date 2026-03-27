import { ApiError } from "./api_error.utils.js";

const generateAccessAndRefreshToken = async (userID, model) => {
    try {
        const user = await model.findById(userID);
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
