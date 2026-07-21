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
}

const studentApis = new Student();
export default studentApis;
