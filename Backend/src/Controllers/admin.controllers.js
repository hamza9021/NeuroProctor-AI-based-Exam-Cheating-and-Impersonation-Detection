import { wrapperFunction } from "../Utils/async_wrap.utils.js";
import { ApiError } from "../Utils/api_error.utils.js";
import { ApiResponse } from "../Utils/api_response.utils.js";
import { Admin } from "../Models/admin.models.js";
import { uploadOnCloudinary } from "../Services/cloudinary.services.js";
import { generateAccessAndRefreshToken } from "../Utils/generate_access_and_refresh_token.js";
import { cookieOptions } from "../options/cookie.options.js";

const registerAdmin = wrapperFunction(async (req, res) => {
    const { name, email, password, phone_number } = req.body;

    if (!name || !email || !password || !phone_number) {
        throw new ApiError("All fields are required", 400);
    }

    const admin = await Admin.findOne({ email });

    if (admin) {
        throw new ApiError("Admin with this email already exists", 400);
    }

    if ((await Admin.countDocuments()) >= 1) {
        throw new ApiError(400, "Only one admin can be registered");
    }

    const profilePictureLocalPath = req.files?.profile_picture?.[0]?.path;

    if (!profilePictureLocalPath) {
        throw new ApiError(400, "Profile picture is required");
    }

    const profilePictureUrl = await uploadOnCloudinary(profilePictureLocalPath);
    if (!profilePictureUrl) {
        throw new ApiError(500, "Failed to upload profile picture");
    }

    const newAdmin = await Admin.create({
        name,
        email,
        password,
        phone_number,
        profile_picture: profilePictureUrl.url,
    });

    const createdAdmin = await Admin.findById(newAdmin._id).select(
        "-password -refreshToken"
    );
    return res
        .status(201)
        .json(
            new ApiResponse(201, createdAdmin, "Admin registered successfully")
        );
});

const loginAdmin = wrapperFunction(async (req, res) => {
    const { email, password } = req.body;
    if (!email || !password) {
        throw new ApiError("Email and password are required", 400);
    }

    let admin = await Admin.findOne({ email });
    if (!admin) {
        throw new ApiError("Invalid email or password", 401);
    }

    if (!(await admin.isPasswordMatch(password))) {
        throw new ApiError("Invalid email or password", 401);
    }

    const { accessToken, refreshToken } = await generateAccessAndRefreshToken(
        admin._id,
        Admin
    );

    if (!accessToken || !refreshToken) {
        throw new ApiError(500, "Failed to generate access and refresh token");
    }

    admin = await Admin.findById(admin._id).select("-password -refreshToken");

    return res
        .cookie("accessToken", accessToken, cookieOptions)
        .cookie("refreshToken", refreshToken, cookieOptions)
        .status(200)
        .json(new ApiResponse(200, admin, "Admin logged in successfully"));
});

const logoutAdmin = wrapperFunction(async (req, res) => {
    await Admin.findByIdAndUpdate(
        req.admin._id,
        {
            $unset: { refreshToken: "" },
        },
        {
            returnDocument: "after",
            runValidators: true,
        }
    );

    res.status(200)
        .clearCookie("accessToken", cookieOptions)
        .clearCookie("refreshToken", cookieOptions)
        .json(new ApiResponse(200, {}, "Logout Successfully"));
});

export { registerAdmin, loginAdmin, logoutAdmin };
