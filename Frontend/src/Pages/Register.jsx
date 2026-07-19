import { useForm } from "react-hook-form";
import { useNavigate } from "react-router-dom";
import { useMutation } from "@tanstack/react-query";
import user from "../apis/Users/user.apis";

const Register = () => {
    const {
        register,
        handleSubmit,
        formState: { errors },
    } = useForm();

    const { mutate, isLoading, isError, error, isSuccess } = useMutation({
        mutationFn: (userData) => user.register(userData),
    });

    const onSubmit = (userData) => {
        const formData = new FormData();
        formData.append("fullName", userData.fullName);
        formData.append("email", userData.email);
        formData.append("password", userData.password);
        formData.append("phoneNumber", userData.phoneNumber);
        formData.append("role", userData.role);
        formData.append("profileImage", userData.profileImage[0]);
        mutate(formData);
    };

    if (isLoading) {
        return <p>Loading...</p>;
    }

    if (isSuccess) {
        return (
            <p>
                Registration successful! Please check your email to verify your
                account.
            </p>
        );
    }

    if (isError) {
        return (
            <p>
                Error occurred while registering:{" "}
                {error?.stack || error?.message || "Unknown error"}
            </p>
        );
    }

    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-100">
            <div className="w-full max-w-md bg-white p-6 rounded-lg shadow-md">
                <h2 className="text-2xl font-bold text-center mb-6">
                    Register
                </h2>

                <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                    <div>
                        <label className="block mb-1 font-medium">
                            Full Name
                        </label>
                        <input
                            className="w-full border border-gray-300 rounded-md p-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                            {...register("fullName", { required: true })}
                        />
                        {errors.fullName && (
                            <p className="text-red-500 text-sm mt-1">
                                This field is required
                            </p>
                        )}
                    </div>

                    <div>
                        <label className="block mb-1 font-medium">Email</label>
                        <input
                            className="w-full border border-gray-300 rounded-md p-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                            {...register("email", {
                                required: true,
                                pattern: /^\S+@\S+$/,
                            })}
                        />
                        {errors.email && (
                            <p className="text-red-500 text-sm mt-1">
                                Please enter a valid email
                            </p>
                        )}
                    </div>

                    <div>
                        <label className="block mb-1 font-medium">
                            Password
                        </label>
                        <input
                            type="password"
                            className="w-full border border-gray-300 rounded-md p-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                            {...register("password", {
                                required: true,
                                minLength: 8,
                                maxLength: 30,
                            })}
                        />
                        {errors.password && (
                            <p className="text-red-500 text-sm mt-1">
                                Password must be between 8 and 30 characters
                            </p>
                        )}
                    </div>

                    <div>
                        <label className="block mb-1 font-medium">
                            Phone Number
                        </label>
                        <input
                            className="w-full border border-gray-300 rounded-md p-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                            {...register("phoneNumber", {
                                required: true,
                                pattern: /^[0-9]{10,15}$/,
                            })}
                        />
                        {errors.phoneNumber && (
                            <p className="text-red-500 text-sm mt-1">
                                Please enter a valid phone number
                            </p>
                        )}
                    </div>

                    <div>
                        <label className="block mb-1 font-medium">Role</label>
                        <select
                            className="w-full border border-gray-300 rounded-md p-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                            {...register("role", { required: true })}
                        >
                            <option value="">Select a role</option>
                            <option value="invigilator">Invigilator </option>
                            <option value="admin">Admin</option>
                        </select>
                        {errors.role && (
                            <p className="text-red-500 text-sm mt-1">
                                Please select a role
                            </p>
                        )}
                    </div>

                    <div>
                        <label className="block mb-1 font-medium">
                            Profile Image
                        </label>
                        <input
                            type="file"
                            className="w-full border border-gray-300 rounded-md p-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                            {...register("profileImage", { required: true })}
                        />
                        {errors.profileImage && (
                            <p className="text-red-500 text-sm mt-1">
                                Please upload a profile image
                            </p>
                        )}
                    </div>

                    <button
                        type="submit"
                        className="w-full bg-blue-600 text-white py-2 rounded-md hover:bg-blue-700 transition"
                        disabled={isLoading}
                    >
                        {isLoading ? "Registering..." : "Register"}
                    </button>
                </form>
            </div>
        </div>
    );
};

export default Register;
