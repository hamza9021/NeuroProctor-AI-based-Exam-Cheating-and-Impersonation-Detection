import { wrapperFunction } from "../Utils/async_wrap.utils.js";
import { ApiError } from "../Utils/api_error.utils.js";
import { ApiResponse } from "../Utils/api_response.utils.js";
import { Invigilator } from "../Models/invigilator.models.js";

const registerInvigilator = wrapperFunction(async (req, res) => {
    const { name, email, phone_number } = req.body;

    if (!name || !email || !password || !phone_number) {
        throw new ApiError(400, "All fields are required");
    }

    if (await Invigilator.findOne({ email })) {
        throw new ApiError(400, "Invigilator already exists");
    }

    
});


export { registerInvigilator };
