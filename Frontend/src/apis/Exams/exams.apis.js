import axiosInstanceExpress from "../../AxiosInstance/axios.express.js";


class Exam {
    async createExam(examData) {
        const response = await axiosInstanceExpress.post(
            "/api/v1/exams/create",
            examData
        );
        return response.data;
    }

    async getExams(page,
        limit,
        search,
        sortBy,
        sortOrder) {
        const response = await axiosInstanceExpress.get(
            "/api/v1/exams", {
            params: {
                page,
                limit,
                search: search || undefined,
                sortBy,
                sortOrder
            },
        }
        );
        return response.data.data;
    }

    async getExam(examId) {
        const response = await axiosInstanceExpress.get(
            `/api/v1/exams/${examId}`
        );
        return response.data.data;
    }

    async deleteExam(examId) {
        const response = await axiosInstanceExpress.delete(
            `/api/v1/exams/delete/${examId}`
        );
        return response.data;
    }

    async updateExam(examId, examData) {
        const response = await axiosInstanceExpress.put(
            `/api/v1/exams/update/${examId}`,
            examData
        );
        return response.data;
    }

}

const examApis = new Exam();
export default examApis;