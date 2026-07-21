import { useForm } from "react-hook-form";
import { useNavigate } from "react-router-dom";
import { useMutation } from "@tanstack/react-query";
import user from "../../apis/Users/user.apis.js";
import Input from "../../components/ui/Input";
import Select from "../../components/ui/Select";
import Button from "../../components/ui/Button";
import Spinner from "../../components/ui/Spinner";
import ErrorState from "../../components/ui/ErrorState";

const Register = () => {
    const navigate = useNavigate();
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
        return (
            <div className="min-h-screen flex items-center justify-center bg-neutral-50">
                <div className="text-center">
                    <Spinner size="lg" />
                    <p className="mt-4 text-neutral-600">Creating your account...</p>
                </div>
            </div>
        );
    }

    if (isSuccess) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-neutral-50 p-4">
                <div className="w-full max-w-md text-center">
                    <div className="inline-flex items-center justify-center w-16 h-16 bg-green-100 rounded-full mb-4">
                        <svg className="w-8 h-8 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                    </div>
                    <h1 className="text-2xl font-semibold text-neutral-900 mb-2">Registration successful!</h1>
                    <p className="text-neutral-500 mb-6">Please check your email to verify your account.</p>
                    <Button onClick={() => navigate("/login")}>Go to Login</Button>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen flex items-center justify-center bg-neutral-50 p-4">
            <div className="w-full max-w-md">
                {/* Logo */}
                <div className="text-center mb-8">
                    <div className="inline-flex items-center justify-center w-16 h-16 mb-4">
                        <img src="/src/Assets/Logo.png" alt="NeuroProctor" className="w-full h-full object-contain" />
                    </div>
                    <h1 className="text-2xl font-semibold text-neutral-900">Create an account</h1>
                    <p className="text-neutral-500 mt-2">Sign up to get started with NeuroProctor</p>
                </div>

                {/* Error state */}
                {isError && (
                    <div className="mb-6">
                        <ErrorState
                            title="Registration failed"
                            description={error?.stack || error?.message || "Please check your information and try again."}
                        />
                    </div>
                )}

                {/* Form */}
                <div className="bg-white rounded-2xl shadow-sm border border-neutral-200 p-8">
                    <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
                        <Input
                            label="Full Name"
                            placeholder="John Doe"
                            error={errors.fullName ? "This field is required" : ""}
                            {...register("fullName", { required: true })}
                        />

                        <Input
                            label="Email"
                            type="email"
                            placeholder="you@example.com"
                            error={errors.email ? "Please enter a valid email" : ""}
                            {...register("email", {
                                required: true,
                                pattern: /^\S+@\S+$/,
                            })}
                        />

                        <Input
                            label="Password"
                            type="password"
                            placeholder="••••••••"
                            error={errors.password ? "Password must be between 8 and 30 characters" : ""}
                            {...register("password", {
                                required: true,
                                minLength: 8,
                                maxLength: 30,
                            })}
                        />

                        <Input
                            label="Phone Number"
                            type="tel"
                            placeholder="+1 234 567 8900"
                            error={errors.phoneNumber ? "Please enter a valid phone number" : ""}
                            {...register("phoneNumber", {
                                required: true,
                                pattern: /^[0-9]{10,15}$/,
                            })}
                        />

                        <Select
                            label="Role"
                            error={errors.role ? "Please select a role" : ""}
                            {...register("role", { required: true })}
                        >
                            <option value="">Select a role</option>
                            <option value="invigilator">Invigilator</option>
                            <option value="admin">Admin</option>
                        </Select>

                        <div>
                            <label className="block text-sm font-medium text-neutral-700 mb-1.5">
                                Profile Image
                            </label>
                            <input
                                type="file"
                                accept="image/*"
                                className="w-full px-3 py-2 border border-neutral-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-accent focus:border-transparent"
                                {...register("profileImage", { required: true })}
                            />
                            {errors.profileImage && (
                                <p className="text-sm text-red-600 mt-1.5">
                                    Please upload a profile image
                                </p>
                            )}
                        </div>

                        <Button
                            type="submit"
                            className="w-full"
                            isLoading={isLoading}
                        >
                            Create Account
                        </Button>
                    </form>

                    <div className="mt-6 text-center">
                        <p className="text-sm text-neutral-500">
                            Already have an account?{" "}
                            <a
                                href="/login"
                                className="text-accent hover:text-accent-dark font-medium"
                            >
                                Sign in
                            </a>
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Register;
