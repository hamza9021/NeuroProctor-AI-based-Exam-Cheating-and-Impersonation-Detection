import { Router } from "express";
import { getAdmins, getAdmin, getInvigilators, getInvigilator, getExams, verifyInvigilator, deleteInvigilator, getExam } from "../Controllers/admin.controller.js";
import { verifyJWT } from "../Middleware/index.middleware.js";

const adminRouter = Router();

adminRouter.get("/admins", verifyJWT, getAdmins);
adminRouter.get("/admin/:id", verifyJWT, getAdmin);
adminRouter.get("/invigilators", verifyJWT, getInvigilators);
adminRouter.get("/invigilator/:id", verifyJWT, getInvigilator);
adminRouter.get("/exams", verifyJWT, getExams);
adminRouter.put("/verify/invigilator/:id", verifyJWT, verifyInvigilator);
adminRouter.delete("/delete/invigilator/:id", verifyJWT, deleteInvigilator);
adminRouter.get("/exam/:id", verifyJWT, getExam);

export default adminRouter;