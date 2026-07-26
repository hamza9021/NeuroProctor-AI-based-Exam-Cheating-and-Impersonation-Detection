import mongoose from "mongoose";

const examSessionSchema = new mongoose.Schema(
  {
    examId: {
      type: mongoose.Schema.Types.ObjectId,
      ref: "Exam",
      required: true,
      index: true,
    },

    invigilatorId: {
      type: mongoose.Schema.Types.ObjectId,
      ref: "User",
      required: true,
      index: true,
    },

    sessionCode: {
      type: String,
      required: true,
      unique: true,
      trim: true,
      uppercase: true,
    },

    mode: {
      type: String,
      enum: ["offline", "live"],
      default: "offline",
    },

    status: {
      type: String,
      enum: [
        "scheduled",
        "waiting",
        "processing",
        "active",
        "completed",
        "cancelled",
      ],
      default: "scheduled",
    },

    startedAt: {
      type: Date,
      default: null,
    },

    endedAt: {
      type: Date,
      default: null,
    },
  },
  {
    timestamps: true,
  }
);

examSessionSchema.index({ examId: 1 });
examSessionSchema.index({ invigilatorId: 1 });
examSessionSchema.index({ status: 1 });
examSessionSchema.index({ sessionCode: 1 });

const ExamSession = mongoose.model("ExamSession", examSessionSchema);

export default ExamSession;