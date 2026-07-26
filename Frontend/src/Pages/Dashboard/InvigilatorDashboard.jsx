import Layout from "../../components/Layout/Layout";
import Card from "../../components/ui/Card";
import { Video, AlertTriangle, Activity, Shield, Play, Clock, ArrowRight } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import examSessionApis from "../../apis/ExamSessions/examSessions.apis.js";
import videoAnalysisApis from "../../apis/VideoAnalysis/videoAnalysis.apis.js";
import Spinner from "../../components/ui/Spinner";
import Badge from "../../components/ui/Badge";
import { useAuth } from "../../contexts/AuthContext";
import { useNavigate } from "react-router-dom";
import VideoUpload from "../../components/VideoUpload/VideoUpload.jsx";
import VideoAnalysisCard from "../../components/VideoUpload/VideoAnalysisCard.jsx";
import { useState } from "react";

const InvigilatorDashboard = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [selectedSession, setSelectedSession] = useState(null);

  const { data: sessionsData, isLoading: sessionsLoading } = useQuery({
    queryKey: ["invigilator-sessions", user?._id],
    queryFn: () => examSessionApis.getInvigilatorSessions(1, 10, user?._id),
    enabled: !!user?._id,
  });

  const { data: videoAnalysisData, refetch: refetchVideoAnalysis, isLoading: videoAnalysisLoading } = useQuery({
    queryKey: ["video-analysis", selectedSession?._id],
    queryFn: () => videoAnalysisApis.getVideoAnalysisBySession(selectedSession?._id),
    enabled: !!selectedSession?._id,
    retry: false,
  });

  const sessions = sessionsData?.examSessions || [];
  const totalSessions = sessionsData?.pagination?.total || 0;
  const activeSessions = sessions.filter(s => s.status === 'active').length;
  const scheduledSessions = sessions.filter(s => s.status === 'scheduled').length;

  const handleVideoUploadSuccess = (data) => {
    refetchVideoAnalysis();
  };

  const handleSessionSelect = (session) => {
    setSelectedSession(session);
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'active':
        return <Badge variant="success">Active</Badge>;
      case 'scheduled':
        return <Badge variant="neutral">Scheduled</Badge>;
      case 'completed':
        return <Badge variant="info">Completed</Badge>;
      case 'cancelled':
        return <Badge variant="error">Cancelled</Badge>;
      default:
        return <Badge variant="neutral">{status}</Badge>;
    }
  };

  if (sessionsLoading) {
    return (
      <Layout title="Dashboard">
        <div className="flex items-center justify-center min-h-screen">
          <Spinner size="lg" />
        </div>
      </Layout>
    );
  }

  return (
    <Layout title="Dashboard">
      <div className="space-y-6">
        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card padding="md">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-neutral-500">Total Sessions</p>
                <p className="text-2xl font-semibold text-neutral-900 mt-1">{totalSessions}</p>
              </div>
              <div className="w-12 h-12 bg-accent/10 rounded-lg flex items-center justify-center">
                <Video className="w-6 h-6 text-accent" />
              </div>
            </div>
          </Card>

          <Card padding="md">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-neutral-500">Active</p>
                <p className="text-2xl font-semibold text-neutral-900 mt-1">{activeSessions}</p>
              </div>
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                <Play className="w-6 h-6 text-green-600" />
              </div>
            </div>
          </Card>

          <Card padding="md">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-neutral-500">Scheduled</p>
                <p className="text-2xl font-semibold text-neutral-900 mt-1">{scheduledSessions}</p>
              </div>
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                <Clock className="w-6 h-6 text-blue-600" />
              </div>
            </div>
          </Card>

          <Card padding="md">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-neutral-500">System Status</p>
                <p className="text-2xl font-semibold text-neutral-900 mt-1">Active</p>
              </div>
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                <Shield className="w-6 h-6 text-green-600" />
              </div>
            </div>
          </Card>
        </div>

        {/* AI Video Processing */}
        {selectedSession && selectedSession.status === 'active' && (
          <Card>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-neutral-900">AI Video Processing</h3>
                <button
                  onClick={() => setSelectedSession(null)}
                  className="text-sm text-neutral-500 hover:text-neutral-700"
                >
                  Clear Selection
                </button>
              </div>
              
              <div className="p-4 bg-neutral-50 rounded-lg">
                <p className="text-sm text-neutral-600 mb-2">
                  Selected Session: <span className="font-medium text-neutral-900">{selectedSession.sessionCode}</span>
                </p>
                <p className="text-xs text-neutral-500">
                  Upload exam footage for AI-powered cheating detection
                </p>
              </div>

              <VideoUpload
                sessionId={selectedSession._id}
                examId={selectedSession.examId?._id || selectedSession.examId}
                onSuccess={handleVideoUploadSuccess}
              />

              {videoAnalysisData?.data && !videoAnalysisLoading && (
                <div className="pt-4 border-t border-neutral-200">
                  <VideoAnalysisCard videoAnalysis={videoAnalysisData.data} />
                </div>
              )}
            </div>
          </Card>
        )}

        {/* Recent Sessions */}
        <Card>
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-neutral-900">Recent Exam Sessions</h3>
            {sessions.length === 0 ? (
              <div className="text-center py-8 text-neutral-500">
                <p>No exam sessions assigned to you</p>
              </div>
            ) : (
              <div className="space-y-3">
                {sessions.slice(0, 5).map((session) => (
                  <div 
                    key={session._id} 
                    className={`flex items-center justify-between p-4 rounded-lg cursor-pointer transition-colors ${
                      selectedSession?._id === session._id
                        ? "bg-accent/10 border-2 border-accent"
                        : "bg-neutral-50 hover:bg-neutral-100 border-2 border-transparent"
                    }`}
                    onClick={() => handleSessionSelect(session)}
                  >
                    <div className="flex items-center gap-4">
                      <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                        selectedSession?._id === session._id
                          ? "bg-accent"
                          : "bg-accent/10"
                      }`}>
                        <Video className={`w-5 h-5 ${
                          selectedSession?._id === session._id
                            ? "text-white"
                            : "text-accent"
                        }`} />
                      </div>
                      <div>
                        <p className="font-medium text-neutral-900">{session.sessionCode}</p>
                        <p className="text-sm text-neutral-500">
                          {new Date(session.createdAt).toLocaleDateString()} at {new Date(session.createdAt).toLocaleTimeString()}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      {getStatusBadge(session.status)}
                      <span className="text-xs text-neutral-500 uppercase">{session.mode}</span>
                      {session.status === 'active' && (
                        <span className="text-xs text-accent font-medium">Upload Video</span>
                      )}
                      <ArrowRight className="w-4 h-4 text-neutral-400" />
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </Card>

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

