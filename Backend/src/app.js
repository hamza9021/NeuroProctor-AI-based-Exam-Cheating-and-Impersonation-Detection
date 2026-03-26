import express from "express";
import cors from "cors";
import dotenv from "dotenv";
dotenv.config({ path: "./.env" });

// --------OPTIONS IMPORTS--------
import { corsOptions } from "./options/cors.options.js";

const app = express();
app.use(cors(corsOptions));

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
