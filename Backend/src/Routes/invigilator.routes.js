import { Router } from "express";

import {
    registerInvigilator,
    loginInvigilator,
    getAllInvigilators,
} from "../Controllers/invigilator.controllers.js";

import { upload } from "../Middlewares/multer.middlewares.js";

const invigilatorRouter = Router();

invigilatorRouter
    .route("/register")
    .post(
        upload.fields([{ name: "profile_picture", maxCount: 1 }]),
        registerInvigilator
    );

invigilatorRouter.route("/login").post(loginInvigilator);
invigilatorRouter.route("/get-all").get(getAllInvigilators);

export { invigilatorRouter };
