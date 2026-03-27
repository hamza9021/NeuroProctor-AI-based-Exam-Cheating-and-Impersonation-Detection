import { ApiClient } from "../ApiClient.js";

class AdminApi {

    constructor() {
        this.apiClient = new ApiClient();
    }


    async registerAdmin(adminData) {
        try {
            const response = await this.apiClient.client.post(
                "/admin/register",
                adminData
            );
            return response.data;
        } catch (error) {
            console.error("Error registering admin:", error);
            throw error;
        }
    }


    async loginAdmin(credentials) {
        try {
            const response = await this.apiClient.client.post(
                "/admin/login",
                credentials
            );
            return response.data.data;
        } catch (error) {
            console.error("Error logging in admin:", error);
            throw error;
        }
    }
}


export { AdminApi };