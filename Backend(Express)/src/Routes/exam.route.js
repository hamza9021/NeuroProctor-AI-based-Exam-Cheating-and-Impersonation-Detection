import {Router} from "express";
import { createExam, getExams, getExam, updateExam, deleteExam } from "../Controllers/exam.controller.js";
import { verifyJWT } from "../Middleware/index.middleware.js";
import { validateExam } from "../Middleware/validateExam.middleware.js";

const examRouter = Router();

examRouter.post("/create",verifyJWT,validateExam,createExam);
examRouter.get("/",verifyJWT,getExams);
examRouter.get("/:id",verifyJWT,getExam);
examRouter.put("/update/:id",verifyJWT,validateExam,updateExam);
examRouter.delete("/delete/:id",verifyJWT,deleteExam);

export default examRouter;