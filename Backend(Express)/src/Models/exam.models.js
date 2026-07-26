import { model, Schema } from "mongoose";

const examSchema = new Schema(
    {
        title: {
            type: String,
            required: true,
            trim: true,
        },
        description: {
            type: String,
            required: true,
            trim: true,
        },
        courseName: {
            type: String,
            required: true,
            trim: true,
        },
        courseCode: {
            type: String,
            required: true,
            trim: true,
            uppercase: true,
        },
        duration: {
            type: Number,
            required: true,
        },
        startTime: {
            type: Date,
            required: true,
        },
        endTime: {
            type: Date,
            required: true,
        },
        status: {
            type: String,
            enum: [
                "scheduled",
                "ongoing",
                "completed",
                "cancelled",
            ],
            default: "scheduled",
        },
        createdBy: {
            type: Schema.Types.ObjectId,
            ref: "User",
            required: true,
        },
    },
    {
        timestamps: true,
    }
);


examSchema.index({ status: 1 });

examSchema.index({ createdBy: 1 });

examSchema.index({ startTime: 1 });

examSchema.index({ endTime: 1 });

examSchema.index({ courseCode: 1 });

examSchema.index({ courseName: 1 });

examSchema.index({
    status: 1,
    startTime: 1,
});

examSchema.index({
    createdBy: 1,
    status: 1,
});

const Exam = model("Exam", examSchema);

export default Exam;