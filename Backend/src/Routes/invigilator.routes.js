import { Router } from "express";

import {
    registerInvigilator,
    loginInvigilator,
    getAllInvigilators,
    logoutInvigilator
} from "../Controllers/invigilator.controllers.js";

import { upload } from "../Middlewares/multer.middlewares.js";
import { verifyJWT } from "../Middlewares/auth.middlewares.js";

const invigilatorRouter = Router();

invigilatorRouter
    .route("/register")
    .post(
        upload.fields([{ name: "profile_picture", maxCount: 1 }]),
        registerInvigilator
    );

invigilatorRouter.route("/login").post(loginInvigilator);
invigilatorRouter.route("/logout").post(verifyJWT, logoutInvigilator);
invigilatorRouter.route("/get-all").get(getAllInvigilators);

export { invigilatorRouter };
