import { examValidationSchema } from "../Validation/exam.validation.js";

const validateExam = (req, res, next) => {
    const { error, value } = examValidationSchema.validate(req.body, {
        abortEarly: false,
        stripUnknown: true,
    });

    if (error) {
        return res.status(400).json({
            success: false,
            message: "Validation failed",
            errors: error.details.map((err) => err.message),
        });
    }

    req.body = value;
    next();
};

export { validateExam };