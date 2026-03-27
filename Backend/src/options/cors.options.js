import dotenv from "dotenv";
dotenv.config({path: "./.env"});

const corsOptions = {
    origin: [process.env.CORS_ORIGIN, process.env.CORS_LOCAL],
    credentials: true,
    methods: ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allowedHeaders: ["Content-Type", "Authorization"],
};

export { corsOptions };
