import express from "express";
import cors from "cors";
import dotenv from "dotenv";
dotenv.config({ path: "./.env" });

const app = express();
app.use(
    cors({
        origin: "*",
    })
);

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
