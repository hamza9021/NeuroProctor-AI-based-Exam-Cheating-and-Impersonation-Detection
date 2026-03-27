import { wrapperFunction } from "../Utils/async_wrap.utils.js";
import { ApiError } from "../Utils/api_error.utils.js";
import { ApiResponse } from "../Utils/api_response.utils.js";
import { Invigilator } from "../Models/invigilator.models.js";
import { uploadOnCloudinary } from "../Services/cloudinary.services.js";
import { generateAccessAndRefreshToken } from "../Utils/generate_access_and_refresh_token.js";
import { cookieOptions } from "../options/cookie.options.js";

const registerInvigilator = wrapperFunction(async (req, res) => {
    const { name, email, password, phone_number } = req.body;

    if (!name || !email || !password || !phone_number) {
        throw new ApiError(400, "All fields are required");
    }

    if (await Invigilator.findOne({ email })) {
        throw new ApiError(400, "Invigilator already exists");
    }

    const profilePictureLocalPath = req.files?.profile_picture?.[0]?.path;

    if (!profilePictureLocalPath) {
        throw new ApiError(400, "Profile picture is required");
    }

    const profilePictureUrl = await uploadOnCloudinary(profilePictureLocalPath);

    if (!profilePictureUrl) {
        throw new ApiError(500, "Failed to upload profile picture");
    }

    const newInvigilator = await Invigilator.create({
        name,
        email,
        password,
        phone_number,
        profile_picture: profilePictureUrl.url,
    });

    const createdInvigilator = await Invigilator.findById(
        newInvigilator._id
    ).select("-password -refreshToken");

    return res
        .status(201)
        .json(
            new ApiResponse(
                201,
                createdInvigilator,
                "Invigilator registered successfully"
            )
        );
});

const loginInvigilator = wrapperFunction(async (req, res) => {
    const { email, password } = req.body;

    if (!email || !password) {
        throw new ApiError(400, "Email and password are required");
    }

    let invigilator = await Invigilator.findOne({ email });

    if (!invigilator) {
        throw new ApiError(404, "Invigilator not found");
    }

    if (!(await invigilator.isPasswordMatch(password))) {
        throw new ApiError(401, "Invalid credentials");
    }

    const { accessToken, refreshToken } = await generateAccessAndRefreshToken(
        invigilator._id
    );

    if (!accessToken || !refreshToken) {
        throw new ApiError(500, "Failed to generate access and refresh token");
    }

    invigilator = await Invigilator.findOne({ email }).select(
        "-password -refreshToken"
    );

    return res
        .cookie("accessToken", accessToken, cookieOptions)
        .cookie("refreshToken", refreshToken, cookieOptions)
        .status(200)
        .json(
            new ApiResponse(
                200,
                invigilator,
                "Invigilator logged in successfully"
            )
        );
});

const logoutInvigilator = wrapperFunction(async (req, res) => {
    await Invigilator.findByIdAndUpdate(
        req.invigilator._id,
        { $set: { refreshToken: undefined } },
        { new: true }
    );

    res.status(200)
        .clearCookie("accessToken", cookieOptions)
        .clearCookie("refreshToken", cookieOptions)
        .json(new ApiResponse(200, {}, "Logout Successfully"));
});

const getAllInvigilators = wrapperFunction(async (req, res) => {
    const invigilators = await Invigilator.find().select(
        "-password -refreshToken"
    );
    return res
        .status(200)
        .json(
            new ApiResponse(
                200,
                invigilators,
                "Invigilators retrieved successfully"
            )
        );
});

export { registerInvigilator, loginInvigilator, getAllInvigilators, logoutInvigilator };
