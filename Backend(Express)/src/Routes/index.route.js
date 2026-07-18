import userRouter from "./user.route.js";

const initializeRoutes = (app) => {
    app.use("/api/v1/users", userRouter);
};

export default initializeRoutes;
