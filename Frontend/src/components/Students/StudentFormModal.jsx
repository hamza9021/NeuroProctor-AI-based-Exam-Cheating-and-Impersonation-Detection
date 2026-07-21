import { useForm } from "react-hook-form";
import { useNavigate } from "react-router-dom";
import { useMutation } from "@tanstack/react-query";
import studentApis from "../../apis/Students/student.apis.js";

const StudentFormModal = ({ isOpen, onClose }) => {
  if (!isOpen) return null;

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm();

  const { mutate, isLoading, isError, error, isSuccess } = useMutation({
    mutationFn: (studentData) => studentApis.createStudent(studentData),
  });

  const onSubmit = (studentData) => {
    const formData = new FormData();
    formData.append("full_name", studentData.full_name);
    formData.append("email", studentData.email);
    formData.append("registration_number", studentData.registration_number);
    formData.append("department", studentData.department);
    formData.append("semester", studentData.semester);
    formData.append("profile_image", studentData.profile_image[0]);
    mutate(formData);
  };

  if (isLoading) {
    return <p>Loading...</p>;
  }

  if (isSuccess) {
    return (
      <p>
        Student Added Successfully!
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
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center">
      <div className="bg-white rounded-lg shadow-lg w-full max-w-md p-6">
        <h2 className="text-2xl font-bold mb-4">Add Student</h2>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div>
            <label className="block mb-1 font-medium">
              Full Name
            </label>
            <input
              className="w-full border border-gray-300 rounded-md p-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              {...register("full_name", { required: true })}
            />
            {errors.full_name && (
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
              Registration Number
            </label>
            <input
              type="text"
              className="w-full border border-gray-300 rounded-md p-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              {...register("registration_number", {
                required: true,
                pattern: {
                  value: /^(SP|FA)\d{2}-[A-Z]{2,5}-\d{3}$/,
                  message: "Format must be like SP23-BCS-183",
                },
              })}
            />
            {errors.registration_number && (
              <p className="text-red-500 text-sm mt-1">
                Please enter a valid registration number
              </p>
            )}
          </div>


          <div>
            <label className="block mb-1 font-medium">Department</label>
            <input
              className="w-full border border-gray-300 rounded-md p-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              {...register("department", {
                required: true,
              })}
            />
            {errors.department && (
              <p className="text-red-500 text-sm mt-1">
                Please enter department name
              </p>
            )}
          </div>


          <div>
            <label className="block mb-1 font-medium">Semester</label>
            <input
              className="w-full border border-gray-300 rounded-md p-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              {...register("semester", {
                required: true,
              })}
            />
            {errors.semester && (
              <p className="text-red-500 text-sm mt-1">
                Please enter semester number
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
              {...register("profile_image", { required: true })}
            />
            {errors.profile_image && (
              <p className="text-red-500 text-sm mt-1">
                Please upload a profile image
              </p>
            )}
          </div>
          <div className="flex justify-end gap-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 bg-gray-300 rounded-md hover:bg-gray-400"
            >
              Cancel
            </button>

            <button
              type="submit"
              className="w-full bg-blue-600 text-white py-2 rounded-md hover:bg-blue-700 transition"
              disabled={isLoading}
            >
              {isLoading ? "Adding..." : "Add Student"}
            </button>
          </div>


        </form>

      </div>
    </div>
  );
};

export default StudentFormModal;


