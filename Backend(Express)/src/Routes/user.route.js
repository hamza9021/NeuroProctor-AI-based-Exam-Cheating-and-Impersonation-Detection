import { Router } from "express";
import { registerUser, loginUser,getUser,logoutUser } from "../Controllers/user.controller.js";
import {
    registerValidation,
    loginValidation,
    upload,
    verifyJWT,
} from "../Middleware/index.middleware.js";

const userRouter = Router();

userRouter.post(
    "/register",
    registerValidation,
    upload.fields([{ name: "profileImage", maxCount: 1 }]),
    registerUser
);

userRouter.post("/login", loginValidation, loginUser);
userRouter.post("/logout",verifyJWT,logoutUser);
userRouter.get("/",verifyJWT,getUser);
export default userRouter;
