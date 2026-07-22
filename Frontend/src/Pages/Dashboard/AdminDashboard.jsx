import Layout from "../../components/Layout/Layout";
import Card from "../../components/ui/Card";
import { Users, UserCheck, Clock, FileText, TrendingUp, ShieldCheck, UserX } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import adminApis from "../../apis/Admin/admin.apis.js";
import Spinner from "../../components/ui/Spinner";
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";

const AdminDashboard = () => {
  const { data: adminsData, isLoading: adminsLoading } = useQuery({
    queryKey: ["admin-stats"],
    queryFn: () => adminApis.getAdmins(1, 100, ""),
  });

  const { data: invigilatorsData, isLoading: invigilatorsLoading } = useQuery({
    queryKey: ["invigilator-stats"],
    queryFn: () => adminApis.getInvigilators(1, 100, ""),
  });

  const { data: examsData, isLoading: examsLoading } = useQuery({
    queryKey: ["admin-exams-stats"],
    queryFn: () => adminApis.getExams(1, 100, ""),
  });

  const totalAdmins = adminsData?.pagination?.total || 0;
  const totalInvigilators = invigilatorsData?.pagination?.total || 0;
  const totalExams = examsData?.pagination?.total || 0;
  const totalUsers = totalAdmins + totalInvigilators;

  const verifiedInvigilators = invigilatorsData?.invigilators?.filter(i => i.isVerified).length || 0;
  const pendingInvigilators = invigilatorsData?.invigilators?.filter(i => !i.isVerified).length || 0;

  // Chart data
  const userDistributionData = [
    { name: 'Admins', value: totalAdmins, color: '#8b5cf6' },
    { name: 'Invigilators', value: totalInvigilators, color: '#6366f1' },
  ];

  const verificationStatusData = [
    { name: 'Verified', value: verifiedInvigilators, color: '#22c55e' },
    { name: 'Pending', value: pendingInvigilators, color: '#eab308' },
  ];

  const examStatusData = [
    { name: 'Scheduled', value: examsData?.exams?.filter(e => e.status === 'scheduled').length || 0, color: '#6366f1' },
    { name: 'Ongoing', value: examsData?.exams?.filter(e => e.status === 'ongoing').length || 0, color: '#22c55e' },
    { name: 'Completed', value: examsData?.exams?.filter(e => e.status === 'completed').length || 0, color: '#3b82f6' },
    { name: 'Cancelled', value: examsData?.exams?.filter(e => e.status === 'cancelled').length || 0, color: '#ef4444' },
  ];

  const COLORS = ['#8b5cf6', '#6366f1', '#22c55e', '#eab308', '#3b82f6', '#ef4444'];

  if (adminsLoading || invigilatorsLoading || examsLoading) {
    return (
      <Layout title="Admin Dashboard">
        <div className="flex items-center justify-center min-h-screen">
          <Spinner size="lg" />
        </div>
      </Layout>
    );
  }

  return (
    <Layout title="Admin Dashboard">
      <div className="space-y-6">
        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card padding="md">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-neutral-500">Total Users</p>
                <p className="text-2xl font-semibold text-neutral-900 mt-1">{totalUsers}</p>
              </div>
              <div className="w-12 h-12 bg-accent/10 rounded-lg flex items-center justify-center">
                <Users className="w-6 h-6 text-accent" />
              </div>
            </div>
          </Card>

          <Card padding="md">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-neutral-500">Verified Users</p>
                <p className="text-2xl font-semibold text-neutral-900 mt-1">{verifiedInvigilators}</p>
              </div>
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                <UserCheck className="w-6 h-6 text-green-600" />
              </div>
            </div>
          </Card>

          <Card padding="md">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-neutral-500">Pending Verification</p>
                <p className="text-2xl font-semibold text-neutral-900 mt-1">{pendingInvigilators}</p>
              </div>
              <div className="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center">
                <Clock className="w-6 h-6 text-yellow-600" />
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

        {/* Additional Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <Card padding="md">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-neutral-500">Total Admins</p>
                <p className="text-2xl font-semibold text-neutral-900 mt-1">{totalAdmins}</p>
              </div>
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                <ShieldCheck className="w-6 h-6 text-purple-600" />
              </div>
            </div>
          </Card>

          <Card padding="md">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-neutral-500">Total Invigilators</p>
                <p className="text-2xl font-semibold text-neutral-900 mt-1">{totalInvigilators}</p>
              </div>
              <div className="w-12 h-12 bg-indigo-100 rounded-lg flex items-center justify-center">
                <UserCheck className="w-6 h-6 text-indigo-600" />
              </div>
            </div>
          </Card>

          <Card padding="md">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-neutral-500">System Health</p>
                <p className="text-2xl font-semibold text-neutral-900 mt-1">98%</p>
              </div>
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                <TrendingUp className="w-6 h-6 text-green-600" />
              </div>
            </div>
          </Card>
        </div>

        {/* Charts Section */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* User Distribution Pie Chart */}
          <Card>
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-neutral-900">User Distribution</h3>
              <ResponsiveContainer width="100%" height={250}>
                <PieChart>
                  <Pie
                    data={userDistributionData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {userDistributionData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </Card>

          {/* Verification Status Pie Chart */}
          <Card>
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-neutral-900">Invigilator Verification</h3>
              <ResponsiveContainer width="100%" height={250}>
                <PieChart>
                  <Pie
                    data={verificationStatusData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {verificationStatusData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
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
            <h2 className="text-2xl font-semibold text-neutral-900 mb-2">Welcome to Admin Dashboard</h2>
            <p className="text-neutral-500 max-w-md mx-auto">
              Manage users, verify accounts, oversee exam operations, and monitor system performance.
            </p>
          </div>
        </Card>
      </div>
    </Layout>
  );
};

export default AdminDashboard;
