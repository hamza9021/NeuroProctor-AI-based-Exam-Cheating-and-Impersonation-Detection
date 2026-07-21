import { useForm } from "react-hook-form";
import { useMutation } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import user from "../../apis/Users/user.apis.js";
import Input from "../../components/ui/Input";
import Select from "../../components/ui/Select";
import Button from "../../components/ui/Button";
import Spinner from "../../components/ui/Spinner";
import ErrorState from "../../components/ui/ErrorState";

const Login = () => {
    const navigate = useNavigate();
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
        return (
            <div className="min-h-screen flex items-center justify-center bg-neutral-50">
                <div className="text-center">
                    <Spinner size="lg" />
                    <p className="mt-4 text-neutral-600">Signing in...</p>
                </div>
            </div>
        );
    }

    if (isSuccess) {
        navigate("/invigilator/dashboard");
        return null;
    }

    return (
        <div className="min-h-screen flex items-center justify-center bg-neutral-50 p-4">
            <div className="w-full max-w-md">
                {/* Logo */}
                <div className="text-center mb-8">
                    <div className="inline-flex items-center justify-center w-16 h-16 mb-4">
                        <img src="/src/Assets/Logo.png" alt="NeuroProctor" className="w-full h-full object-contain" />
                    </div>
                    <h1 className="text-2xl font-semibold text-neutral-900">Welcome back</h1>
                    <p className="text-neutral-500 mt-2">Sign in to your NeuroProctor account</p>
                </div>

                {/* Error state */}
                {isError && (
                    <div className="mb-6">
                        <ErrorState
                            title="Authentication failed"
                            description={error?.stack || error?.message || "Please check your credentials and try again."}
                        />
                    </div>
                )}

                {/* Form */}
                <div className="bg-white rounded-2xl shadow-sm border border-neutral-200 p-8">
                    <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
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

                        <Select
                            label="Role"
                            error={errors.role ? "Please select a role" : ""}
                            {...register("role", { required: true })}
                        >
                            <option value="">Select a role</option>
                            <option value="invigilator">Invigilator</option>
                            <option value="admin">Admin</option>
                        </Select>

                        <Button
                            type="submit"
                            className="w-full"
                            isLoading={isLoading}
                        >
                            Sign In
                        </Button>
                    </form>

                    <div className="mt-6 text-center">
                        <p className="text-sm text-neutral-500">
                            Don't have an account?{" "}
                            <a
                                href="/register"
                                className="text-accent hover:text-accent-dark font-medium"
                            >
                                Sign up
                            </a>
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Login;
