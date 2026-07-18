import dotenv from "dotenv";
dotenv.config({ path: "./.env" });

const corsOptions = {
    origin: process.env.CORS_ORIGIN,
    methods: ["GET", "POST", "PUT", "DELETE"],
    allowedHeaders: ["Content-Type", "Authorization"],
    credentials: true,
};

console.log("CORS Options:", corsOptions);

export default corsOptions;
