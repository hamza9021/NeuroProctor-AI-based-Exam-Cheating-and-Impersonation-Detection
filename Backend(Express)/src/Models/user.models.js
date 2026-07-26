import { model, Schema } from "mongoose";
import bcrypt from "bcrypt";
import jwt from "jsonwebtoken";

const userSchema = new Schema(
    {
        fullName: {
            type: String,
            required: true,
            trim: true,
        },
        email: {
            type: String,
            required: true,
            unique: true,
            lowercase: true,
            trim: true,
        },
        password: {
            type: String,
            required: true,
        },
        phoneNumber: {
            type: String,
            required: true,
            trim: true,
        },
        role: {
            type: String,
            enum: ["invigilator", "admin"],
            required: true,
        },
        profileImage: {
            type: String,
            required: true,
        },
        isVerified: {
            type: Boolean,
            default: false,
        },
        isActive: {
            type: Boolean,
            default: false,
        },
        refreshToken: {
            type: String,
            default: null,
        },
    },
    {
        timestamps: true,
    }
);

userSchema.index({ email: 1 }, { unique: true });

userSchema.index({ role: 1 });

userSchema.index({ isActive: 1 });

userSchema.index({ isVerified: 1 });

userSchema.index({ role: 1, isActive: 1 });

userSchema.index({ role: 1, isVerified: 1 });

userSchema.index({ createdAt: -1 });

userSchema.pre("save", async function (next) { try { if (this.isModified("password")) { const hashedPassword = await bcrypt.hash(this.password, 10); this.password = hashedPassword; } } catch (error) { console.log(error); next(error); } });
userSchema.methods.isPasswordMatch = async function (password) {
    return bcrypt.compare(password, this.password);
};

userSchema.methods.generateAccessToken = function () {
    return jwt.sign(
        {
            _id: this._id,
            email: this.email,
            fullName: this.fullName,
            role: this.role,
        },
        process.env.ACCESS_TOKEN_SECRET,
        {
            expiresIn: process.env.ACCESS_TOKEN_EXPIRY,
        }
    );
};

userSchema.methods.generateRefreshToken = function () {
    return jwt.sign(
        {
            _id: this._id,
            email: this.email,
            fullName: this.fullName,
            role: this.role,
        },
        process.env.REFRESH_TOKEN_SECRET,
        {
            expiresIn: process.env.REFRESH_TOKEN_EXPIRY,
        }
    );
};

const User = model("User", userSchema);

export default User;