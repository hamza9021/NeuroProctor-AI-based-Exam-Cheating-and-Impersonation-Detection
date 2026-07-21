import axiosInstancePython from "../../AxiosInstance/axios.python.js";

class Student {
    async createStudent(studentData) {
        console.log(studentData);
        const response = await axiosInstancePython.post(
            "/api/v1/students",
            studentData
        );
        return response.data;
    }


    async getStudents(page,
        limit,
        search,
        sortBy,
        sortOrder) {

        const response = await axiosInstancePython.get("/api/v1/students", {
            params: {
                page,
                limit,
                search: search || undefined,
                sort_by: sortBy,
                sort_order: sortOrder,
            },
        });
        console.log(response.data.data);
        return response.data.data;
    }

    async getStudent(studentId) {
        const response = await axiosInstancePython.get(
            `/api/v1/students/${studentId}`
        );
        return response.data.data;
    }

    async updateFace(studentId, faceData) {
        const response = await axiosInstancePython.put(
            `/api/v1/students/${studentId}/face`,
            faceData
        );
        return response.data;
    }

    async deleteStudent(studentId) {
        const response = await axiosInstancePython.delete(
            `/api/v1/students/${studentId}`
        );
        return response.data;
    }
    
}

const studentApis = new Student();
export default studentApis;
