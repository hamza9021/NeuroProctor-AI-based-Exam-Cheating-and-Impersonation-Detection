import axiosInstancePython from "../../AxiosInstance/axios.python.js";
import axiosInstanceExpress from "../../AxiosInstance/axios.express.js";

const videoAnalysisApis = {
    // Process video through FastAPI AI Services
    processVideo: async (videoFile, sessionId, examId) => {
        const formData = new FormData();
        formData.append("video", videoFile);
        formData.append("sessionId", sessionId);
        formData.append("examId", examId);

        const response = await axiosInstancePython.post(
            `/api/v1/video/process`,
            formData,
            {
                headers: {
                    "Content-Type": "multipart/form-data",
                },
            }
        );

        return response.data;
    },

    // Get video analysis by session ID
    getVideoAnalysisBySession: async (sessionId) => {
        const response = await axiosInstanceExpress.get(
            `/api/v1/videoAnalysis/session/${sessionId}`,
            {
                withCredentials: true,
            }
        );

        return response.data;
    },

    // Get all video analyses for current invigilator
    getInvigilatorVideoAnalyses: async () => {
        const response = await axiosInstanceExpress.get(
            "/api/v1/videoAnalysis/invigilator"
        );

        return response.data;
    },
};

export default videoAnalysisApis;
