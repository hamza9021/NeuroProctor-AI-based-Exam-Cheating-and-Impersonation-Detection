import Joi from "joi";

const userValidationSchema = Joi.object({
    fullName: Joi.string().trim().min(3).max(100).required(),

    email: Joi.string().trim().lowercase().email().required(),

    password: Joi.string().min(8).max(30).required(),

    phoneNumber: Joi.string()
        .trim()
        .pattern(/^[0-9]{10,15}$/)
        .required(),

    role: Joi.string().valid("user", "admin").required(),
});

export default userValidationSchema;