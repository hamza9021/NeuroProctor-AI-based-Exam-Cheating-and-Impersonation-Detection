import userValidationSchema from "../Validation/user.validation.js";

export const validateUser = (req, res, next) => {
    const { error, value } = userValidationSchema.validate(req.body, {
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


export default validateUser;