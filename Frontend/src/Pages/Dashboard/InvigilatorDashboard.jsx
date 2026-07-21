import Layout from "../../components/Layout/Layout";
import Card from "../../components/ui/Card";
import { Users, CheckCircle, AlertTriangle, Clock } from "lucide-react";

const InvigilatorDashboard = () => {
  return (
    <Layout title="Dashboard">
      <div className="space-y-6">
        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card padding="md">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-neutral-500">Total Students</p>
                <p className="text-2xl font-semibold text-neutral-900 mt-1">156</p>
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
                <p className="text-2xl font-semibold text-neutral-900 mt-1">142</p>
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
                <p className="text-2xl font-semibold text-neutral-900 mt-1">14</p>
              </div>
              <div className="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center">
                <AlertTriangle className="w-6 h-6 text-yellow-600" />
              </div>
            </div>
          </Card>

          <Card padding="md">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-neutral-500">Active Exams</p>
                <p className="text-2xl font-semibold text-neutral-900 mt-1">3</p>
              </div>
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                <Clock className="w-6 h-6 text-blue-600" />
              </div>
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

