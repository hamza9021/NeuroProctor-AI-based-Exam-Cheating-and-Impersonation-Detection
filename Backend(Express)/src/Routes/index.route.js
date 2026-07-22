import userRouter from "./user.route.js";
import examRouter from "./exam.route.js";

const initializeRoutes = (app) => {
    app.use("/api/v1/users", userRouter);
    app.use("/api/v1/exams", examRouter);
};

export default initializeRoutes;
