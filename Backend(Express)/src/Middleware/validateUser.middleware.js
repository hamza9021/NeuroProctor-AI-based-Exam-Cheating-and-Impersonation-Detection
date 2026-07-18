import {
    registerValidationSchema,
    loginValidationSchema,
} from "../Validation/index.validation.js";

const registerValidation = (req, res, next) => {
    const { error, value } = registerValidationSchema.validate(req.body, {
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

const loginValidation = (req, res, next) => {
    const { error, value } = loginValidationSchema.validate(req.body, {
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
    console.log(req.body);
    next();
};

export { registerValidation, loginValidation };
