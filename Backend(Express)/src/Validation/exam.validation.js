import Joi from "joi";


const examValidationSchema = Joi.object({
    title: Joi.string().trim().min(3).max(100).required(),
    description: Joi.string().trim().min(3).max(500).required(),
    courseName: Joi.string().trim().min(3).max(100).required(),
    courseCode: Joi.string().trim().min(3).max(20).required(),
    duration: Joi.number().min(1).required(),
    startTime: Joi.date().required(),
    endTime: Joi.date().greater(Joi.ref('startTime')).required(),
});

export { examValidationSchema };