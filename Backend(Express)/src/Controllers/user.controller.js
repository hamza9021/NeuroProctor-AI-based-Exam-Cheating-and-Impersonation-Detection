import {
    ApiError,
    ApiResponse,
    wrapperFunction,
    generateAccessAndRefreshToken,
} from "../Utils/index.utils.js";

import { uploadOnCloudinary } from "../Services/cloudinary.service.js";
import User from "../Models/user.models.js";
import { cookieOptions } from "../Options/cookie.options.js";

const registerUser = wrapperFunction(async (req, res) => {
    const { fullName, email, password, phoneNumber, role } = req.body;

    if (await User.findOne({ $or: [{ phoneNumber }, { email }] })) {
        throw new ApiError(409, "User Already Exists");
    }

    const profileImageLocalPath = await req.files?.profileImage?.[0]?.path;
    if (!profileImageLocalPath) {
        throw new ApiError(400, "Profile Image Should Be Required");
    }

    const profileImage = await uploadOnCloudinary(profileImageLocalPath);
    if (!profileImage) {
        throw new ApiError(400, "Profile Image is not uploaded on cloud");
    }

    const user = await User.create({
        fullName,
        email,
        password,
        phoneNumber,
        role,
        profileImage: profileImage.secure_url,
    });

    const createdUser = await User.findById(user._id).select(
        "-password -refreshToken"
    );

    console.log(createdUser);

    return res
        .status(200)
        .json(new ApiResponse(200, createdUser, "User Created Successfully"));
});

const loginUser = wrapperFunction(async (req, res) => {
    console.log(req.body);
    const { email, password, role } = req.body;

    const user = await User.findOne({ email });

    if (!user) {
        throw new ApiError(404, "User Not Found");
    }

    if (!(await user.isPasswordMatch(password))) {
        throw new ApiError(401, "Incorrect Password");
    }

    if (user.role !== role) {
        throw new ApiError(403, "Invalid Role");
    }

    if (!user.isVerified) {
        throw new ApiError(
            403,
            "You are not verified yet. You Will be verified by current admin. Please wait for verification."
        );
    }

    const { accessToken, refreshToken } = await generateAccessAndRefreshToken(
        user._id
    );
    const updateUser = await User.findById(user._id).select(
        "-password -refreshToken"
    );

    return res
        .cookie("accessToken", accessToken, cookieOptions)
        .cookie("refreshToken", refreshToken, cookieOptions)
        .status(200)
        .json(new ApiResponse(200, updateUser, "User Logged In Successfully"));
});

export { registerUser, loginUser };
