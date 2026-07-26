import Layout from "../../components/Layout/Layout";
import Card from "../../components/ui/Card";
import { Video, AlertTriangle, Activity, Shield } from "lucide-react";
import Spinner from "../../components/ui/Spinner";

const InvigilatorDashboard = () => {
  return (
    <Layout title="Dashboard">
      <div className="space-y-6">
        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card padding="md">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-neutral-500">Active Sessions</p>
                <p className="text-2xl font-semibold text-neutral-900 mt-1">0</p>
              </div>
              <div className="w-12 h-12 bg-accent/10 rounded-lg flex items-center justify-center">
                <Video className="w-6 h-6 text-accent" />
              </div>
            </div>
          </Card>

          <Card padding="md">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-neutral-500">Alerts</p>
                <p className="text-2xl font-semibold text-neutral-900 mt-1">0</p>
              </div>
              <div className="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center">
                <AlertTriangle className="w-6 h-6 text-red-600" />
              </div>
            </div>
          </Card>

          <Card padding="md">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-neutral-500">Monitoring</p>
                <p className="text-2xl font-semibold text-neutral-900 mt-1">0</p>
              </div>
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                <Activity className="w-6 h-6 text-green-600" />
              </div>
            </div>
          </Card>

          <Card padding="md">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-neutral-500">System Status</p>
                <p className="text-2xl font-semibold text-neutral-900 mt-1">Active</p>
              </div>
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                <Shield className="w-6 h-6 text-blue-600" />
              </div>
            </div>
          </Card>
        </div>

        {/* Welcome Card */}
        <Card>
          <div className="text-center py-12">
            <h2 className="text-2xl font-semibold text-neutral-900 mb-2">Welcome to Invigilator Dashboard</h2>
            <p className="text-neutral-500 max-w-md mx-auto">
              Monitor active exam sessions, view AI alerts, and ensure exam integrity in real-time.
            </p>
          </div>
        </Card>
      </div>
    </Layout>
  );
};

export default InvigilatorDashboard;

