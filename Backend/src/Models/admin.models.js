import { Schema, model } from "mongoose";
import bcrypt from "bcrypt";
import jwt from "jsonwebtoken";

const adminSchema = new Schema(
    {
        name: { type: String, required: true },
        email: { type: String, required: true, unique: true },
        phone_number: { type: Number, required: true },
        password: { type: String, required: true },
        profile_picture: { type: String, required: true },
        refreshToken: {
            type: String,
        },
    },
    { timestamps: true }
);

adminSchema.pre("save", async function () {
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

adminSchema.methods.isPasswordMatch = async function (password) {
    try {
        return await bcrypt.compare(password, this.password);
    } catch (error) {
        console.error("Error comparing passwords:", error);
        throw error;
    }
};

adminSchema.methods.generateAccessToken = function () {
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

adminSchema.methods.generateRefreshToken = function () {
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

const Admin = model("Admin", adminSchema);

export { Admin };
