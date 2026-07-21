import axios from "axios";

const axiosInstancePython = axios.create({
  baseURL: import.meta.env.VITE_API_URL_PYTHON,
  withCredentials: true,
});


export default axiosInstancePython;