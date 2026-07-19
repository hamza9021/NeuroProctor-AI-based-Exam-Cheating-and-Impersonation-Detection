import axiosInstance from "../../AxiosInstance/axios";
class User {
    async register(userData) {
        const response = await axiosInstance.post("/api/v1/users/register", userData);
        return response.data;
    }
}


const user = new User();
export default user;