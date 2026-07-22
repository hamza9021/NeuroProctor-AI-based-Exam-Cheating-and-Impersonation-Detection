import Joi from "joi";


const examValidationSchema = Joi.object({
    title: Joi.string().trim().min(3).max(100).required(),
    description: Joi.string().trim().min(3).max(100).required(),
    courseName: Joi.string().trim().min(3).max(100).required(),
    courseCode: Joi.string().trim().min(3).max(100).required(),
    duration: Joi.number().required(),
    startTime: Joi.date().required(),
    endTime: Joi.date().required(),
});

export { examValidationSchema };