import Layout from "../../components/Layout/Layout";
import Card from "../../components/ui/Card";
import { Users, UserCheck, Clock, FileText, TrendingUp, ShieldCheck, UserX } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import adminApis from "../../apis/Admin/admin.apis.js";
import Spinner from "../../components/ui/Spinner";

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
