import { Schema, model } from "mongoose";

const invigilatorSchema = new Schema(
    {
        name: { type: String, required: true },
        email: { type: String, required: true, unique: true },
        password: { type: String, required: true },
        phone_number: { type: String, required: true },
        profile_picture: { type: String, required: true },
        status: { type: Boolean, default: false },
    },
    { timestamps: true }
);

const Invigilator = model("Invigilator", invigilatorSchema);

export { Invigilator };
