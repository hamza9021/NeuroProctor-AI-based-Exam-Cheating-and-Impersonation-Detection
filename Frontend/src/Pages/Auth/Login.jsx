import { useForm } from "react-hook-form";
import { useMutation } from "@tanstack/react-query";
import user from "../../apis/Users/user.apis.js";

const Login = () => {
    const {
        register,
        handleSubmit,
        formState: { errors },
    } = useForm();

    const { mutate, isLoading, isError, error, isSuccess } = useMutation({
        mutationFn: (userData) => user.login(userData),
    });

    const onSubmit = (userData) => {
        mutate(userData);
    };

    if (isLoading) {
        return <p>Loading...</p>;
    }

    if (isSuccess) {
        return <p>Login successful!</p>;
    }

    if (isError) {
        return (
            <p>
                Error occurred while Logging:{" "}
                {error?.stack || error?.message || "Unknown error"}
            </p>
        );
    }

    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-100">
            <div className="w-full max-w-md bg-white p-6 rounded-lg shadow-md">
                <h2 className="text-2xl font-bold text-center mb-6">Login</h2>

                <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
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

                    <button
                        type="submit"
                        className="w-full bg-blue-600 text-white py-2 rounded-md hover:bg-blue-700 transition"
                        disabled={isLoading}
                    >
                        {isLoading ? "Logging..." : "Login"}
                    </button>
                </form>
            </div>
        </div>
    );
};

export default Login;
