import { model, Schema } from "mongoose";
import User from "./user.models.js";

const examSchema = new Schema(
    {
        title: {
            type: String,
            required: true,
        },
        description: {
            type: String,
            required: true,
        },
        courseName: {
            type: String,
            required: true
        },
        courseCode: {
            type: String,
            required: true
        },
        duration: {
            type: Number,
            required: true
        },
        startTime: {
            type: Date,
            required: true
        },
        endTime: {
            type: Date,
            required: true
        },
        status: {
            enum: [
                "scheduled",
                "ongoing",
                "completed",
                "cancelled",
            ],
            type: String,
            default: "draft",
        },
        createdBy: {
            type: Schema.Types.ObjectId,
            ref: User,
            required: true,
        }
    },
    {
        timestamps: true,
    }
);

const Exam = model("Exam", examSchema);
export default Exam;
