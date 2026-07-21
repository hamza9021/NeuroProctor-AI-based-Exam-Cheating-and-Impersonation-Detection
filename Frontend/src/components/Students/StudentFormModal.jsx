import { useForm } from "react-hook-form";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import studentApis from "../../apis/Students/student.apis.js";
import Modal from "../ui/Modal";
import Input from "../ui/Input";
import Button from "../ui/Button";

const StudentFormModal = ({ isOpen, onClose }) => {
  const queryClient = useQueryClient();

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm();

  const { mutate, isLoading, isError, error, isSuccess } = useMutation({
    mutationFn: (studentData) => studentApis.createStudent(studentData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["students"] });
      reset();
      onClose();
    },
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

  if (!isOpen) return null;

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Add New Student"
      size="md"
    >
      {isError && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-sm font-medium text-red-900 mb-1">Failed to add student</p>
          <p className="text-sm text-red-700">
            {error?.response?.data?.message || error?.message || "Please check your information and try again."}
          </p>
        </div>
      )}

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
        <Input
          label="Full Name"
          placeholder="John Doe"
          error={errors.full_name ? "This field is required" : ""}
          {...register("full_name", { required: true })}
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
          label="Registration Number"
          placeholder="SP23-BCS-183"
          error={errors.registration_number ? "Format must be like SP23-BCS-183" : ""}
          {...register("registration_number", {
            required: true,
            pattern: {
              value: /^(SP|FA)\d{2}-[A-Z]{2,5}-\d{3}$/,
              message: "Format must be like SP23-BCS-183",
            },
          })}
        />

        <Input
          label="Department"
          placeholder="Computer Science"
          error={errors.department ? "Please enter department name" : ""}
          {...register("department", {
            required: true,
          })}
        />

        <Input
          label="Semester"
          type="number"
          placeholder="1"
          error={errors.semester ? "Please enter semester number" : ""}
          {...register("semester", {
            required: true,
          })}
        />

        <div>
          <label className="block text-sm font-medium text-neutral-700 mb-1.5">
            Profile Image
          </label>
          <input
            type="file"
            accept="image/*"
            className="w-full px-3 py-2 border border-neutral-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-accent focus:border-transparent"
            {...register("profile_image", { required: true })}
          />
          {errors.profile_image && (
            <p className="text-sm text-red-600 mt-1.5">
              Please upload a profile image
            </p>
          )}
        </div>

        <div className="flex justify-end gap-3 pt-4">
          <Button
            type="button"
            variant="outline"
            onClick={onClose}
            disabled={isLoading}
          >
            Cancel
          </Button>

          <Button
            type="submit"
            isLoading={isLoading}
          >
            Add Student
          </Button>
        </div>
      </form>
    </Modal>
  );
};

export default StudentFormModal;


