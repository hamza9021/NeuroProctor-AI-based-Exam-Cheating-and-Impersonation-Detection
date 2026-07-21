import { useParams } from "react-router-dom";
import {
    useQuery,
    useMutation,
    useQueryClient,
} from "@tanstack/react-query";
import studentApis from "../../apis/Students/student.apis.js";

const StudentDetail = () => {
    const { studentId } = useParams();
    const queryClient = useQueryClient();

    const {
        data,
        isLoading,
        isError,
        error,
    } = useQuery({
        queryKey: ["student", studentId],
        queryFn: () => studentApis.getStudent(studentId),
    });

    const {
        mutate,
        isPending,
        isError: faceError,
        error: faceErrorMessage,
    } = useMutation({
        mutationFn: (formData) =>
            studentApis.updateFace(studentId, formData),

        onSuccess: () => {
            queryClient.invalidateQueries({
                queryKey: ["student", studentId],
            });
        },
    });

    const handleUpload = (e, pose) => {
        e.preventDefault();

        const file = e.target.image.files[0];

        if (!file) {
            alert("Please select an image.");
            return;
        }

        const formData = new FormData();
        formData.append("image", file);
        formData.append("pose", pose);

        mutate(formData);

        e.target.reset();
    };

    if (isLoading) return <h2>Loading...</h2>;

    if (isError) return <h2>{error.message}</h2>;

    return (
        <div style={{ padding: 20 }}>
            <h1>Student Detail</h1>

            <img
                src={data.profile_image}
                alt="Profile"
                width={150}
            />

            <h2>{data.full_name}</h2>
            <p>{data.email}</p>
            <p>{data.registration_number}</p>
            <p>{data.department}</p>
            <p>{data.semester}</p>

            <hr />

            <h2>Face Embeddings</h2>

            {data.face_embeddings?.map((face) => (
                <div
                    key={face.pose}
                    style={{
                        border: "1px solid #ddd",
                        borderRadius: "8px",
                        padding: "20px",
                        marginBottom: "20px",
                    }}
                >
                    <h3>{face.pose.toUpperCase()}</h3>

                    {face.quality_score > 0 ? (
                        <>
                            <p style={{ color: "green" }}>
                                ✅ Embedded
                            </p>

                            <p>
                                Quality Score:{" "}
                                {face.quality_score}
                            </p>

                            {face.captured_at && (
                                <p>
                                    Captured At:{" "}
                                    {new Date(
                                        face.captured_at
                                    ).toLocaleString()}
                                </p>
                            )}
                        </>
                    ) : (
                        <form
                            onSubmit={(e) =>
                                handleUpload(
                                    e,
                                    face.pose
                                )
                            }
                        >
                            <input
                                type="file"
                                name="image"
                                accept="image/*"
                            />

                            <br />
                            <br />

                            <button
                                type="submit"
                                disabled={isPending}
                            >
                                {isPending
                                    ? "Uploading..."
                                    : `Upload ${face.pose}`}
                            </button>

                            {faceError && (
                                <p
                                    style={{
                                        color: "red",
                                    }}
                                >
                                    {
                                        faceErrorMessage.message
                                    }
                                </p>
                            )}
                        </form>
                    )}
                </div>
            ))}
        </div>
    );
};

export default StudentDetail;