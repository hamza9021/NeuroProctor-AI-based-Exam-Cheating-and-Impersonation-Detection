import { Schema, model } from "mongoose";
import bcrypt from "bcrypt";
import jwt from "jsonwebtoken";

const invigilatorSchema = new Schema(
    {
        name: { type: String, required: true },
        email: { type: String, required: true, unique: true },
        password: { type: String, required: true },
        phone_number: { type: Number, required: true },
        profile_picture: { type: String, required: true },
        status: { type: Boolean, default: false },
        refreshToken: {
            type: String,
        },
    },
    { timestamps: true }
);

invigilatorSchema.pre("save", async function () {
    try {
        if (this.isModified("password")) {
            const hashedPassword = await bcrypt.hash(this.password, 10);
            this.password = hashedPassword;
        }

    } catch (error) {
        console.error("Error hashing password:", error);
        throw error;
    }
});

invigilatorSchema.methods.isPasswordMatch = async function (password) {
    try {
        return await bcrypt.compare(password, this.password);
    } catch (error) {
        console.error("Error comparing passwords:", error);
        throw error;
    }
};

invigilatorSchema.methods.generateAccessToken = function () {
    try {
        return jwt.sign(
            { _id: this._id, name: this.name, email: this.email },
            process.env.ACCESS_TOKEN_SECRET,
            { expiresIn: process.env.ACCESS_TOKEN_EXPIRY }
        );
    } catch (error) {
        console.error("Error generating access token:", error);
        throw error;
    }
};

invigilatorSchema.methods.generateRefreshToken = function () {
    try {
        return jwt.sign(
            { _id: this._id, name: this.name, email: this.email },
            process.env.REFRESH_TOKEN_SECRET,
            { expiresIn: process.env.REFRESH_TOKEN_EXPIRY }
        );
    } catch (error) {
        console.error("Error generating refresh token:", error);
        throw error;
    }
};

const Invigilator = model("Invigilator", invigilatorSchema);

export { Invigilator };
