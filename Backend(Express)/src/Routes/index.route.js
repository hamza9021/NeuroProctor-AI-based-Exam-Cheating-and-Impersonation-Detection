import userRouter from "./user.route.js";
import examRouter from "./exam.route.js";
import adminRouter from "./admin.route.js";

const initializeRoutes = (app) => {
    app.use("/api/v1/users", userRouter);
    app.use("/api/v1/exams", examRouter);
    app.use("/api/v1/admin", adminRouter);
    app.use((req, res) => {
        return res.status(404).json({
            success: false,
            message: `Cannot ${req.method} ${req.originalUrl}`,
        });
    });
};

export default initializeRoutes;
