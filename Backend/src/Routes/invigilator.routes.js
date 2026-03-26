import { Router } from "express";

import { registerInvigilator } from "../Controllers/invigilator.controllers.js";

const invigilatorRouter = Router();

invigilatorRouter.route("/register").post(registerInvigilator);

export { invigilatorRouter };
