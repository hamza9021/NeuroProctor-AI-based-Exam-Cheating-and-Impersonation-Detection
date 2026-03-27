import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { InvigilatorApi } from "../../../Api/Invigilator/Invigilator.Api.js";

const InvigilatorRegister = () => {
    const navigate = useNavigate();
    const invigilatorApi = new InvigilatorApi();

    const [formData, setFormData] = useState({
        name: "",
        email: "",
        password: "",
        phone_number: "",
        profile_picture: null,
    });

    const handleChange = (event) => {
        const { name, value, type, files } = event.target;

        setFormData((prevData) => ({
            ...prevData,
            [name]: type === "file" ? files[0] : value,
        }));
    };

    const handleFormData = async (event) => {
        event.preventDefault();

        const { name, email, phone_number, password, profile_picture } =
            formData;

        if (!name || !email || !phone_number || !password || !profile_picture) {
            alert("All fields are required");
            return;
        }

        if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
            alert("Invalid email format");
            return;
        }

        const form = new FormData();
        form.append("name", name);
        form.append("email", email);
        form.append("phone_number", phone_number);
        form.append("password", password);
        form.append("profile_picture", profile_picture);

        try {
            await invigilatorApi.registerInvigilator(form);
            navigate("/");
        } catch (error) {
            console.error("Error registering invigilator:", error);
        }

        navigate("/");
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-100">
            <form
                onSubmit={handleFormData}
                className="bg-white p-6 rounded shadow-md w-full max-w-sm"
            >
                <h2 className="text-xl font-semibold mb-4 text-center">
                    Register
                </h2>

                {/* Name */}
                <input
                    type="text"
                    name="name"
                    placeholder="Name"
                    value={formData.name}
                    onChange={handleChange}
                    className="w-full border p-2 mb-3 rounded"
                />

                {/* Email */}
                <input
                    type="email"
                    name="email"
                    placeholder="Email"
                    value={formData.email}
                    onChange={handleChange}
                    className="w-full border p-2 mb-3 rounded"
                />

                {/* Phone */}
                <input
                    type="text"
                    name="phone_number"
                    placeholder="Phone Number"
                    value={formData.phone_number}
                    onChange={handleChange}
                    className="w-full border p-2 mb-3 rounded"
                />

                {/* Password */}
                <input
                    type="password"
                    name="password"
                    placeholder="Password"
                    value={formData.password}
                    onChange={handleChange}
                    className="w-full border p-2 mb-3 rounded"
                />

                {/* Profile Picture */}
                <input
                    type="file"
                    name="profile_picture"
                    accept="image/*"
                    onChange={handleChange}
                    className="w-full mb-4"
                />

                {/* Button */}
                <button
                    type="submit"
                    className="w-full bg-blue-500 text-white p-2 rounded hover:bg-blue-600"
                >
                    Register
                </button>
            </form>
        </div>
    );
};

export default InvigilatorRegister;
