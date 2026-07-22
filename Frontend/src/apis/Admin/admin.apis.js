import axiosInstanceExpress from "../../AxiosInstance/axios.express.js";


class Admin {
    async getAdmins(page,
        limit,
        search,) {
        const response = await axiosInstanceExpress.get(
            "/api/v1/admin/admins", {
            params: {
                page,
                limit,
                search: search || undefined,
            },
        }
        );
        return response.data.data;
    }

    async getAdmin(adminId) {
        const response = await axiosInstanceExpress.get(
            `/api/v1/admin/admin/${adminId}`
        );
        return response.data.data;
    }

    async getInvigilators(page,
        limit,
        search,) {
        const response = await axiosInstanceExpress.get(
            "/api/v1/admin/invigilators", {
            params: {
                page,
                limit,
                search: search || undefined
            }
        }
        );
        return response.data.data;
    }

    async getInvigilator(invigilatorId) {
        const response = await axiosInstanceExpress.get(
            `/api/v1/admin/invigilator/${invigilatorId}`
        );
        return response.data.data;
    }

    async getExams(page,
        limit,
        search,) {
        const response = await axiosInstanceExpress.get(
            "/api/v1/admin/exams", {
            params: {
                page,
                limit,
                search: search || undefined
            }
        }
        );
        return response.data.data;
    }

    async verifyInvigilator(invigilatorId) {
        const response = await axiosInstanceExpress.put(
            `/api/v1/admin/verify/invigilator/${invigilatorId}`
        );
        return response.data.data;
    }

    async deleteInvigilator(invigilatorId) {
        const response = await axiosInstanceExpress.delete(
            `/api/v1/admin/delete/invigilator/${invigilatorId}`
        );
        return response.data.data;
    }

    async getExam(examId) {
        const response = await axiosInstanceExpress.get(
            `/api/v1/admin/exam/${examId}`
        );
        return response.data.data;
    }
}

const adminApis = new Admin();

export default adminApis;