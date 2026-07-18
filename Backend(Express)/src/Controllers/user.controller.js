import {
    ApiError,
    ApiResponse,
    wrapperFunction,
} from "../Utils/index.utils.js";
import { uploadOnCloudinary } from "../Services/cloudinary.service.js";

import User from "../Models/user.models.js";

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


export { registerUser };