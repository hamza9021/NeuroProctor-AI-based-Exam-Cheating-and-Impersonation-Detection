import dotenv from "dotenv";
dotenv.config({path: "./.env"});

const corsOptions = {
    origin: [process.env.CORS_ORIGIN, process.env.CORS_LOCAL],
    credentials: process.env.NODE_ENV === "production",
    methods: ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allowedHeaders: ["Content-Type", "Authorization"],
};

export { corsOptions };
