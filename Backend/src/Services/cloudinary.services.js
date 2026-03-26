import { v2 as cloudinary } from "cloudinary";
import fs from "fs";
import dotenv from "dotenv";
dotenv.config({ path: "./.env" });
import { cloudinaryOptions } from "../options/cloudinary.options.js";

cloudinary.config(cloudinaryOptions);

const uploadOnCloudinary = async (localFilePath) => {
    try {
        const response = await cloudinary.uploader.upload(localFilePath, {
            resource_type: "auto",
        });
        return response;
    } catch (e) {
        console.error("Failed to upload to Cloudinary:", error);
        return null;
    } finally {
        fs.unlinkSync(localFilePath);
    }
};

export { uploadOnCloudinary };
