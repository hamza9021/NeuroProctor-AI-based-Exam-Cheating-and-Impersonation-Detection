import axios from "axios";

class ApiClient {
    constructor() {
        this.client = axios.create({
            baseURL: import.meta.env.VITE_API_URL,
            withCredentials: true, //do this for cross site oirign
        });
    }
}

export { ApiClient };
