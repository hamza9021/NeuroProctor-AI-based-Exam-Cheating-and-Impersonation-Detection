import Layout from "../../components/Layout/Layout";
import Card from "../../components/ui/Card";
import { Users, CheckCircle, AlertTriangle, Clock, FileText } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import studentApis from "../../apis/Students/student.apis.js";
import examApis from "../../apis/Exams/exams.apis.js";
import Spinner from "../../components/ui/Spinner";
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";

const InvigilatorDashboard = () => {
  const { data: studentsData, isLoading: studentsLoading, isError: studentsError, error: studentsErrorData } = useQuery({
    queryKey: ["students-stats"],
    queryFn: () => studentApis.getStudents(1, 100, undefined, "created_at", "desc"),
    retry: false,
  });

  // Log the raw response for debugging
  console.log("Raw students data response:", studentsData);

  const { data: examsData, isLoading: examsLoading, isError: examsError, error: examsErrorData } = useQuery({
    queryKey: ["invigilator-exams-stats"],
    queryFn: () => examApis.getExams(1, 100, "", "", ""),
    retry: false,
  });

  const totalStudents = studentsData?.pagination?.total || studentsData?.total || 0;
  const students = studentsData?.students || studentsData?.data || [];
  const totalExams = examsData?.pagination?.total || examsData?.total || 0;
  const exams = examsData?.exams || examsData?.data || [];

  const embeddedStudents = students.filter(s => 
    s.face_embeddings?.every(face => face.quality_score > 0)
  ).length || 0;
  const pendingStudents = students.filter(s => 
    !s.face_embeddings?.every(face => face.quality_score > 0)
  ).length || 0;

  const scheduledExams = exams.filter(e => e.status === 'scheduled').length || 0;
  const ongoingExams = exams.filter(e => e.status === 'ongoing').length || 0;
  const completedExams = exams.filter(e => e.status === 'completed').length || 0;

  // Chart data
  const studentStatusData = [
    { name: 'Embedded', value: embeddedStudents, color: '#22c55e' },
    { name: 'Pending', value: pendingStudents, color: '#eab308' },
  ];

  // Debug logging
  console.log("Students array:", students);
  console.log("Students length:", students.length);
  console.log("First student:", students[0]);
  console.log("Embedded count:", embeddedStudents, "Pending count:", pendingStudents);
  console.log("Student status data:", studentStatusData);

  // Only show chart if there's data
  const hasStudentData = embeddedStudents > 0 || pendingStudents > 0;

  const examStatusData = [
    { name: 'Scheduled', value: scheduledExams, color: '#6366f1' },
    { name: 'Ongoing', value: ongoingExams, color: '#22c55e' },
    { name: 'Completed', value: completedExams, color: '#3b82f6' },
  ];

  if (examsLoading) {
    return (
      <Layout title="Dashboard">
        <div className="flex flex-col items-center justify-center min-h-screen space-y-4">
          <Spinner size="lg" />
          <p className="text-neutral-500">Loading dashboard data...</p>
        </div>
      </Layout>
    );
  }

  // Show dashboard even if student data fails, with zero values
  if (studentsError) {
    console.error("Student data loading error:", studentsErrorData);
  }

  return (
    <Layout title="Dashboard">
      <div className="space-y-6">
        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card padding="md">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-neutral-500">Total Students</p>
                <p className="text-2xl font-semibold text-neutral-900 mt-1">{totalStudents}</p>
              </div>
              <div className="w-12 h-12 bg-accent/10 rounded-lg flex items-center justify-center">
                <Users className="w-6 h-6 text-accent" />
              </div>
            </div>
          </Card>

          <Card padding="md">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-neutral-500">Embedded</p>
                <p className="text-2xl font-semibold text-neutral-900 mt-1">{embeddedStudents}</p>
              </div>
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                <CheckCircle className="w-6 h-6 text-green-600" />
              </div>
            </div>
          </Card>

          <Card padding="md">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-neutral-500">Pending</p>
                <p className="text-2xl font-semibold text-neutral-900 mt-1">{pendingStudents}</p>
              </div>
              <div className="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center">
                <AlertTriangle className="w-6 h-6 text-yellow-600" />
              </div>
            </div>
          </Card>

          <Card padding="md">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-neutral-500">Total Exams</p>
                <p className="text-2xl font-semibold text-neutral-900 mt-1">{totalExams}</p>
              </div>
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                <FileText className="w-6 h-6 text-blue-600" />
              </div>
            </div>
          </Card>
        </div>

        {/* Charts Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Student Status Pie Chart */}
          <Card>
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-neutral-900">Student Face Embedding Status</h3>
              {hasStudentData ? (
                <ResponsiveContainer width="100%" height={250}>
                  <PieChart>
                    <Pie
                      data={studentStatusData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {studentStatusData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <div className="flex items-center justify-center h-64 text-neutral-500">
                  <p>No student data available</p>
                </div>
              )}
            </div>
          </Card>

          {/* Exam Status Bar Chart */}
          <Card>
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-neutral-900">Exam Status</h3>
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={examStatusData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="value" fill="#6366f1" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </Card>
        </div>

        {/* Welcome Card */}
        <Card>
          <div className="text-center py-12">
            <h2 className="text-2xl font-semibold text-neutral-900 mb-2">Welcome to NeuroProctor</h2>
            <p className="text-neutral-500 max-w-md mx-auto">
              Your AI-powered exam proctoring dashboard. Monitor students, manage face embeddings, and ensure exam integrity.
            </p>
          </div>
        </Card>
      </div>
    </Layout>
  );
};

export default InvigilatorDashboard;

