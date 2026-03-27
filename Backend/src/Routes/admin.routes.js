import { Router } from "express";
import { upload } from "../Middlewares/multer.middlewares.js";
import { verifyJWT } from "../Middlewares/auth.middlewares.js";
import {
    registerAdmin,
    loginAdmin,
    logoutAdmin,
} from "../Controllers/admin.controllers.js";

const adminRouter = Router();

adminRouter.route("/register").post(
    upload.fields([
        {
            name: "profile_picture",
            maxCount: 1,
        },
    ]),
    registerAdmin
);

adminRouter.route("/login").post(loginAdmin);
adminRouter.route("/logout").post(verifyJWT, logoutAdmin);

export { adminRouter };
