import { Schema, model } from "mongoose";

const adminSchema = new Schema(
    {
        name: { type: String, required: true },
        email: { type: String, required: true, unique: true },
        password: { type: String, required: true },
        profile_picture: { type: String, required: true },
        refreshToken: {
            type: String,
        },
    },
    { timestamps: true }
);

const Admin = model("Admin", adminSchema);

export { Admin };
