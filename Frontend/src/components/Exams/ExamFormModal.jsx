import { useForm } from "react-hook-form";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import examApis from "../../apis/Exams/exams.apis.js";
import Modal from "../ui/Modal";
import Input from "../ui/Input";
import Button from "../ui/Button";

const ExamFormModal = ({ isOpen, onClose, examData, isEdit = false, onUpdate, isLoading: externalLoading }) => {
  const queryClient = useQueryClient();

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm({
    defaultValues: isEdit && examData ? {
      title: examData.title,
      description: examData.description,
      courseName: examData.courseName,
      courseCode: examData.courseCode,
      duration: examData.duration,
      startTime: examData.startTime ? new Date(examData.startTime).toISOString().slice(0, 16) : '',
      endTime: examData.endTime ? new Date(examData.endTime).toISOString().slice(0, 16) : '',
    } : {}
  });

  const { mutate, isLoading, isError, error, isSuccess } = useMutation({
    mutationFn: (examData) => examApis.createExam(examData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["exams"] });
      reset();
      onClose();
    },
  });

  const onSubmit = (examData) => {
    if (isEdit && onUpdate) {
      onUpdate(examData);
    } else {
      mutate(examData);
    }
  };

  if (!isOpen) return null;

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={isEdit ? "Edit Exam" : "Add New Exam"}
      size="md"
    >
      {isError && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-sm font-medium text-red-900 mb-1">Failed to add exam</p>
          <p className="text-sm text-red-700">
            {error?.response?.data?.message || error?.message || "Please check your information and try again."}
          </p>
        </div>
      )}

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
        <Input
          label="Title"
          placeholder="Midterm Examination"
          error={errors.title ? "This field is required" : ""}
          {...register("title", { required: true })}
        />

        <Input
          label="Description"
          placeholder="Exam description"
          error={errors.description ? "This field is required" : ""}
          {...register("description", { required: true })}
        />

        <Input
          label="Course Name"
          placeholder="Data Structures and Algorithms"
          error={errors.courseName ? "This field is required" : ""}
          {...register("courseName", { required: true })}
        />

        <Input
          label="Course Code"
          placeholder="CS-201"
          error={errors.courseCode ? "This field is required" : ""}
          {...register("courseCode", { required: true })}
        />

        <Input
          label="Duration (minutes)"
          type="number"
          placeholder="90"
          error={errors.duration ? "Please enter duration" : ""}
          {...register("duration", {
            required: true,
            valueAsNumber: true,
          })}
        />

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-neutral-700 mb-1.5">
              Start Time
            </label>
            <input
              type="datetime-local"
              className="w-full px-3 py-2 border border-neutral-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-accent focus:border-transparent"
              {...register("startTime", { required: true })}
            />
            {errors.startTime && (
              <p className="text-sm text-red-600 mt-1.5">
                Please select start time
              </p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-neutral-700 mb-1.5">
              End Time
            </label>
            <input
              type="datetime-local"
              className="w-full px-3 py-2 border border-neutral-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-accent focus:border-transparent"
              {...register("endTime", { required: true })}
            />
            {errors.endTime && (
              <p className="text-sm text-red-600 mt-1.5">
                Please select end time
              </p>
            )}
          </div>
        </div>

        <div className="flex justify-end gap-3 pt-4">
          <Button
            type="button"
            variant="outline"
            onClick={onClose}
            disabled={isLoading || externalLoading}
          >
            Cancel
          </Button>

          <Button
            type="submit"
            isLoading={isLoading || externalLoading}
          >
            {isEdit ? "Update Exam" : "Add Exam"}
          </Button>
        </div>
      </form>
    </Modal>
  );
};

export default ExamFormModal;
