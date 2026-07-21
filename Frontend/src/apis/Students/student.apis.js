import axiosInstancePython from "../../AxiosInstance/axios.python.js";

class Student {
    async createStudent(studentData) {
        const response = await axiosInstancePython.post(
            "/api/v1/students",
            studentData
        );
        return response.data;
    }
}

const studentApis = new Student();
export default studentApis;
