import { Router } from "express";

import { registerInvigilator } from "../Controllers/invigilator.controllers.js";
import { upload } from "../Middlewares/multer.middlewares.js";

const invigilatorRouter = Router();

invigilatorRouter
    .route("/register")
    .post(
        upload.fields([{ name: "profile_picture", maxCount: 1 }]),
        registerInvigilator
    );

export { invigilatorRouter };
