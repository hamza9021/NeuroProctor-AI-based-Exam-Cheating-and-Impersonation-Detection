import { Router } from "express";
import { createExamSession , getInvigilatorSessions, getExamSession, getExamSessions , deleteExamSession, updateExamSessions } from "../Controllers/examSession.controller.js";
import { verifyJWT } from "../Middleware/index.middleware.js";


const examSessionRouter = Router();

examSessionRouter.post("/create",verifyJWT,createExamSession);
examSessionRouter.get("/invigilator/:id",verifyJWT,getInvigilatorSessions);
examSessionRouter.get("/:id",verifyJWT,getExamSession);
examSessionRouter.get("/",verifyJWT,getExamSessions);
examSessionRouter.delete("/delete/:id",verifyJWT,deleteExamSession);
examSessionRouter.put("/update/:id",verifyJWT,updateExamSessions);

export default examSessionRouter;