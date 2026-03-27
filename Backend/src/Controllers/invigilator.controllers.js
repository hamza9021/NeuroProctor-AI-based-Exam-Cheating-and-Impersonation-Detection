import { wrapperFunction } from "../Utils/async_wrap.utils.js";
import { ApiError } from "../Utils/api_error.utils.js";
import { ApiResponse } from "../Utils/api_response.utils.js";
import { Invigilator } from "../Models/invigilator.models.js";
import { uploadOnCloudinary } from "../Services/cloudinary.services.js";

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

export { registerInvigilator };
