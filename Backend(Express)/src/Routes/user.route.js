import { Router } from "express";
import { registerUser } from "../Controllers/user.controller.js";
import {
    validateUser,
    upload,
    verifyJWT,
} from "../Middleware/index.middleware.js";

const userRouter = Router();

userRouter.post(
    "/register",
    validateUser,
    upload.fields([{ name: "profileImage", maxCount: 1 }]),
    registerUser
);

export default userRouter;
