import mongoose from "mongoose";
import { dbConnectionOptions } from "../options/dbConnections.options.js";

const connectDB = async () => {
    try {
        const connectionInstance = await mongoose.connect(
            process.env.MONGO_URI,
            dbConnectionOptions
        );
        console.log("MONGO DB CONNECTED ", connectionInstance.connection.host);
    } catch (error) {
        console.log(error);
        process.exit(1);
    }
};

export { connectDB };
