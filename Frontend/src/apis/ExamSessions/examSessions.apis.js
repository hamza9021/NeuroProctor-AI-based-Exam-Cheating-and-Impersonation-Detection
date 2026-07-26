import axiosInstanceExpress from "../../AxiosInstance/axios.express.js";

class ExamSession {
    async createExamSession(examSessionData) {
        const response = await axiosInstanceExpress.post(
            "/api/v1/examSession/create",
            examSessionData
        );
        return response.data;
    }

    async getExamSessions(page, limit, search, sortBy, sortOrder) {
        const response = await axiosInstanceExpress.get("/api/v1/examSession", {
            params: {
                page,
                limit,
                search: search || undefined,
                sortBy,
                sortOrder
            },
        });
        return response.data.data;
    }

    async getExamSession(sessionId) {
        const response = await axiosInstanceExpress.get(
            `/api/v1/examSession/${sessionId}`
        );
        return response.data.data;
    }

    async getInvigilatorSessions(page, limit, invigilatorId) {
        const response = await axiosInstanceExpress.get(
            `/api/v1/examSession/invigilator/${invigilatorId}`,
            {
                params: {
                    page,
                    limit
                }
            }
        );
        return response.data.data;
    }

    async deleteExamSession(sessionId) {
        const response = await axiosInstanceExpress.delete(
            `/api/v1/examSession/delete/${sessionId}`
        );
        return response.data;
    }

    async updateExamSession(sessionId, examSessionData) {
        const response = await axiosInstanceExpress.put(
            `/api/v1/examSession/update/${sessionId}`,
            examSessionData
        );
        return response.data;
    }
}

const examSessionApis = new ExamSession();
export default examSessionApis;
