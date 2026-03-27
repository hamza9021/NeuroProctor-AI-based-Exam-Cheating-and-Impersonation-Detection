import { ApiClient } from "../ApiClient.js";

class InvigilatorApi {
    constructor() {
        this.apiClient = new ApiClient();
    }

    async registerInvigilator(invigilatorData) {
        try {
            const response = await this.apiClient.client.post(
                "/invigilator/register",
                invigilatorData
            );
            return response.data;
        } catch (error) {
            console.error("Error registering invigilator:", error);
            throw error;
        }
    }

    async loginInvigilator(credentials) {
        try {
            const response = await this.apiClient.client.post(
                "/invigilator/login",
                credentials
            );
            console.log("Response Cookies:", response.headers["set-cookie"]);
            return response.data.data;
        } catch (error) {
            console.error("Error logging in invigilator:", error);
            throw error;
        }
    }


    async getAllInvigilators() {
        try {
            const response = await this.apiClient.client.get("/invigilator/get-all");
            return response.data.data;
        } catch (error) {
            console.error("Error fetching invigilators:", error);
            throw error;
        }
    }
}

export { InvigilatorApi };
