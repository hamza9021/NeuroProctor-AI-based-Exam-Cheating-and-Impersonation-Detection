import Layout from "../../components/Layout/Layout";
import Card from "../../components/ui/Card";
import { Video, Play, Clock, ArrowRight, Upload, CheckCircle, AlertCircle } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import examSessionApis from "../../apis/ExamSessions/examSessions.apis.js";
import videoAnalysisApis from "../../apis/VideoAnalysis/videoAnalysis.apis.js";
import Spinner from "../../components/ui/Spinner";
import Badge from "../../components/ui/Badge";
import { useAuth } from "../../contexts/AuthContext";
import { useNavigate, useParams } from "react-router-dom";
import VideoUpload from "../../components/VideoUpload/VideoUpload.jsx";
import VideoAnalysisCard from "../../components/VideoUpload/VideoAnalysisCard.jsx";
import LiveLogViewer from "../../components/VideoUpload/LiveLogViewer.jsx";
import ProgressPanel from "../../components/VideoUpload/ProgressPanel.jsx";
import { useState, useEffect } from "react";
import { initializeSocket } from "../../utils/socket";

const InvigilatorSessions = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const { sessionId } = useParams();
  const [selectedSession, setSelectedSession] = useState(null);

  // Initialize Socket.IO connection
  useEffect(() => {
    initializeSocket();
  }, []);

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
  const activeSessions = sessions.filter(s => s.status === 'active');
  const scheduledSessions = sessions.filter(s => s.status === 'scheduled');
  const completedSessions = sessions.filter(s => s.status === 'completed');

  // If sessionId is in URL, find and select that session
  useEffect(() => {
    if (sessionId && sessions.length > 0) {
      const session = sessions.find(s => s._id === sessionId);
      if (session) {
        setSelectedSession(session);
      }
    }
  }, [sessionId, sessions]);

  const handleVideoUploadSuccess = (data) => {
    refetchVideoAnalysis();
  };

  const handleSessionSelect = (session) => {
    setSelectedSession(session);
    navigate(`/invigilator/sessions/${session._id}`);
  };

  const handleBackToSessions = () => {
    setSelectedSession(null);
    navigate('/invigilator/sessions');
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
      <Layout title="Exam Sessions">
        <div className="flex items-center justify-center min-h-screen">
          <Spinner size="lg" />
        </div>
      </Layout>
    );
  }

  // Single session view
  if (selectedSession) {
    return (
      <Layout title={`Session: ${selectedSession.sessionCode}`}>
        <div className="space-y-6">
          {/* Session Header */}
          <Card>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <button
                  onClick={handleBackToSessions}
                  className="p-2 hover:bg-neutral-100 rounded-lg transition-colors"
                >
                  <ArrowRight className="w-5 h-5 text-neutral-600 rotate-180" />
                </button>
                <div>
                  <h2 className="text-xl font-semibold text-neutral-900">{selectedSession.sessionCode}</h2>
                  <p className="text-sm text-neutral-500">
                    {new Date(selectedSession.createdAt).toLocaleDateString()} at {new Date(selectedSession.createdAt).toLocaleTimeString()}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                {getStatusBadge(selectedSession.status)}
                <span className="text-xs text-neutral-500 uppercase">{selectedSession.mode}</span>
              </div>
            </div>
          </Card>

          {/* AI Video Processing */}
          {selectedSession.status === 'active' && (
            <Card>
              <div className="space-y-6">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold text-neutral-900">AI Video Processing</h3>
                  <Upload className="w-5 h-5 text-accent" />
                </div>
                
                <div className="p-4 bg-gradient-to-r from-accent/5 to-accent/10 rounded-lg border border-accent/20">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-accent/20 rounded-lg flex items-center justify-center">
                      <Video className="w-5 h-5 text-accent" />
                    </div>
                    <div>
                      <p className="font-medium text-neutral-900">Upload Exam Footage</p>
                      <p className="text-sm text-neutral-600">AI-powered cheating detection and analysis</p>
                    </div>
                  </div>
                </div>

                <VideoUpload
                  sessionId={selectedSession._id}
                  examId={selectedSession.examId?._id || selectedSession.examId}
                  onSuccess={handleVideoUploadSuccess}
                />

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <ProgressPanel sessionId={selectedSession._id} />
                  <LiveLogViewer sessionId={selectedSession._id} />
                </div>

                {videoAnalysisData?.data && !videoAnalysisLoading && (
                  <div className="pt-6 border-t border-neutral-200">
                    <div className="flex items-center gap-2 mb-4">
                      <CheckCircle className="w-5 h-5 text-green-600" />
                      <h4 className="font-semibold text-neutral-900">Analysis Complete</h4>
                    </div>
                    <VideoAnalysisCard videoAnalysis={videoAnalysisData.data} />
                  </div>
                )}
              </div>
            </Card>
          )}

          {/* Completed Session Info */}
          {selectedSession.status === 'completed' && (
            <Card>
              <div className="text-center py-8">
                <CheckCircle className="w-16 h-16 text-green-600 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-neutral-900 mb-2">Session Completed</h3>
                <p className="text-neutral-500">This exam session has been completed.</p>
                {videoAnalysisData?.data && (
                  <div className="mt-6">
                    <VideoAnalysisCard videoAnalysis={videoAnalysisData.data} />
                  </div>
                )}
              </div>
            </Card>
          )}
        </div>
      </Layout>
    );
  }

  // Sessions list view
  return (
    <Layout title="Exam Sessions">
      <div className="space-y-6">
        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card padding="md">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-neutral-500">Active Sessions</p>
                <p className="text-2xl font-semibold text-neutral-900 mt-1">{activeSessions.length}</p>
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
                <p className="text-2xl font-semibold text-neutral-900 mt-1">{scheduledSessions.length}</p>
              </div>
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                <Clock className="w-6 h-6 text-blue-600" />
              </div>
            </div>
          </Card>

          <Card padding="md">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-neutral-500">Completed</p>
                <p className="text-2xl font-semibold text-neutral-900 mt-1">{completedSessions.length}</p>
              </div>
              <div className="w-12 h-12 bg-accent/10 rounded-lg flex items-center justify-center">
                <CheckCircle className="w-6 h-6 text-accent" />
              </div>
            </div>
          </Card>
        </div>

        {/* Sessions List */}
        <Card>
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-neutral-900">All Exam Sessions</h3>
            {sessions.length === 0 ? (
              <div className="text-center py-12 text-neutral-500">
                <Video className="w-12 h-12 mx-auto mb-4 text-neutral-300" />
                <p>No exam sessions assigned to you</p>
              </div>
            ) : (
              <div className="space-y-3">
                {sessions.map((session) => (
                  <div 
                    key={session._id} 
                    className="flex items-center justify-between p-4 rounded-lg bg-neutral-50 hover:bg-neutral-100 border-2 border-transparent hover:border-accent/30 cursor-pointer transition-all duration-200"
                    onClick={() => handleSessionSelect(session)}
                  >
                    <div className="flex items-center gap-4">
                      <div className="w-12 h-12 bg-accent/10 rounded-lg flex items-center justify-center">
                        <Video className="w-6 h-6 text-accent" />
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
                      <span className="text-xs text-neutral-500 uppercase font-medium">{session.mode}</span>
                      {session.status === 'active' && (
                        <span className="flex items-center gap-1 text-xs text-accent font-medium">
                          <Upload className="w-3 h-3" />
                          Upload
                        </span>
                      )}
                      <ArrowRight className="w-4 h-4 text-neutral-400" />
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </Card>
      </div>
    </Layout>
  );
};

export default InvigilatorSessions;
