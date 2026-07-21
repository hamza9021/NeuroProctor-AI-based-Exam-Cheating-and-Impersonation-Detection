import axiosInstanceExpress from "../../AxiosInstance/axios.express.js";

class User {
    async register(userData) {
        const response = await axiosInstanceExpress.post(
            "/api/v1/users/register",
            userData
        );
        return response.data;
    }

    async login(userData) {
        const response = await axiosInstanceExpress.post(
            "/api/v1/users/login",
            userData
        );
        return response.data;
    }

    async getUserData() {
        try {
            const response = await axiosInstanceExpress.get("/api/v1/users");
            console.log(response.data.data)
            return response.data.data;
        } catch (error) {
            console.log(error.message + "CAN NOT GET USER DATA");
        }
    }
}

const user = new User();
export default user;
