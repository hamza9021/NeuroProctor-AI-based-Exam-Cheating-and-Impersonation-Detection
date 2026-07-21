import axios from "axios";

const axiosInstanceExpress = axios.create({
  baseURL: import.meta.env.VITE_API_URL_EXPRESSJS,
  withCredentials: true,
});


export default axiosInstanceExpress;