import express from "express";
import cors from "cors";
import dotenv from "dotenv";
import cookieParser from "cookie-parser";
dotenv.config({ path: "./.env" });

// --------OPTIONS IMPORTS--------
import { corsOptions } from "./options/cors.options.js";

// --------ROUTES IMPORTS--------
import { invigilatorRouter } from "./Routes/invigilator.routes.js";

const app = express();
app.use(cors(corsOptions));
app.use(express.json());
app.use(express.urlencoded({ extended: true, limit: "20kb" }));
app.use(cookieParser());
app.use(express.static("./Public"));

app.use("/api/v1/invigilator", invigilatorRouter);

app.get("/", (req, res) => {
    res.json({ message: "Welcome to the NeuroProctor API" });
});
app.get("/health", (req, res) => {
    res.json({
        status: "OK",
        uptime: process.uptime(),
        timestamp: Date.now(),
        message: "NeuroProctor API is healthy and running smoothly!",
    });
});

export { app };
