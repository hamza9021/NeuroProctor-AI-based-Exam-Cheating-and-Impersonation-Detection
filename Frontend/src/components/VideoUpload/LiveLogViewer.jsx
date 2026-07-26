import { useEffect, useState, useRef } from 'react';
import { getSocket } from '../../utils/socket';
import { Activity, CheckCircle, AlertTriangle, XCircle, Play, Clock, Terminal } from 'lucide-react';

const LiveLogViewer = ({ sessionId }) => {
  const [logs, setLogs] = useState([]);
  const scrollRef = useRef(null);

  useEffect(() => {
    const socket = getSocket();
    
    const handlePipelineInfo = (data) => {
      if (!sessionId || data.session_id === sessionId) {
        setLogs(prev => [...prev, { type: 'info', message: data.message, timestamp: new Date() }]);
      }
    };

    const handlePipelineWarning = (data) => {
      if (!sessionId || data.session_id === sessionId) {
        setLogs(prev => [...prev, { type: 'warning', message: data.message, timestamp: new Date() }]);
      }
    };

    const handlePipelineError = (data) => {
      if (!sessionId || data.session_id === sessionId) {
        setLogs(prev => [...prev, { type: 'error', message: data.message, timestamp: new Date() }]);
      }
    };

    const handleStageStarted = (data) => {
      if (!sessionId || data.session_id === sessionId) {
        setLogs(prev => [...prev, { type: 'stage-start', message: `Stage started: ${data.stage}`, timestamp: new Date() }]);
      }
    };

    const handleStageCompleted = (data) => {
      if (!sessionId || data.session_id === sessionId) {
        setLogs(prev => [...prev, { type: 'stage-complete', message: `Stage completed: ${data.stage}`, timestamp: new Date() }]);
      }
    };

    const handlePipelineStarted = (data) => {
      if (!sessionId || data.session_id === sessionId) {
        setLogs(prev => [...prev, { type: 'pipeline-start', message: 'Pipeline started', timestamp: new Date() }]);
      }
    };

    const handlePipelineCompleted = (data) => {
      if (!sessionId || data.session_id === sessionId) {
        setLogs(prev => [...prev, { type: 'pipeline-complete', message: 'Pipeline completed', timestamp: new Date() }]);
      }
    };

    const handlePipelineFailed = (data) => {
      if (!sessionId || data.session_id === sessionId) {
        setLogs(prev => [...prev, { type: 'pipeline-failed', message: `Pipeline failed: ${data.error}`, timestamp: new Date() }]);
      }
    };

    socket.on('pipeline_info', handlePipelineInfo);
    socket.on('pipeline_warning', handlePipelineWarning);
    socket.on('pipeline_error', handlePipelineError);
    socket.on('stage_started', handleStageStarted);
    socket.on('stage_completed', handleStageCompleted);
    socket.on('pipeline_started', handlePipelineStarted);
    socket.on('pipeline_completed', handlePipelineCompleted);
    socket.on('pipeline_failed', handlePipelineFailed);

    return () => {
      socket.off('pipeline_info', handlePipelineInfo);
      socket.off('pipeline_warning', handlePipelineWarning);
      socket.off('pipeline_error', handlePipelineError);
      socket.off('stage_started', handleStageStarted);
      socket.off('stage_completed', handleStageCompleted);
      socket.off('pipeline_started', handlePipelineStarted);
      socket.off('pipeline_completed', handlePipelineCompleted);
      socket.off('pipeline_failed', handlePipelineFailed);
    };
  }, [sessionId]);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [logs]);

  const getLogIcon = (type) => {
    switch (type) {
      case 'info':
        return <CheckCircle className="w-4 h-4" />;
      case 'warning':
        return <AlertTriangle className="w-4 h-4" />;
      case 'error':
      case 'pipeline-failed':
        return <XCircle className="w-4 h-4" />;
      case 'stage-start':
      case 'pipeline-start':
        return <Play className="w-4 h-4" />;
      case 'stage-complete':
      case 'pipeline-complete':
        return <CheckCircle className="w-4 h-4" />;
      default:
        return <Activity className="w-4 h-4" />;
    }
  };

  const getLogColor = (type) => {
    switch (type) {
      case 'info':
        return 'text-green-600 bg-green-50 border-green-200';
      case 'warning':
        return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'error':
      case 'pipeline-failed':
        return 'text-red-600 bg-red-50 border-red-200';
      case 'stage-start':
      case 'pipeline-start':
        return 'text-blue-600 bg-blue-50 border-blue-200';
      case 'stage-complete':
      case 'pipeline-complete':
        return 'text-green-600 bg-green-50 border-green-200';
      default:
        return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const formatTime = (timestamp) => {
    return timestamp.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit', 
      second: '2-digit',
      hour12: false 
    });
  };

  if (logs.length === 0) {
    return (
      <div className="bg-white rounded-xl border border-neutral-200 shadow-sm overflow-hidden">
        <div className="px-4 py-3 border-b border-neutral-200 bg-gradient-to-r from-neutral-50 to-white">
          <div className="flex items-center gap-2">
            <Terminal className="w-5 h-5 text-accent" />
            <h3 className="text-sm font-semibold text-neutral-900">AI Processing Logs</h3>
          </div>
        </div>
        <div className="p-6 text-center">
          <Activity className="w-12 h-12 text-neutral-300 mx-auto mb-3" />
          <p className="text-sm text-neutral-500">No logs yet. Upload a video to see real-time processing logs.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl border border-neutral-200 shadow-sm overflow-hidden">
      <div className="px-4 py-3 border-b border-neutral-200 bg-gradient-to-r from-neutral-50 to-white">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Terminal className="w-5 h-5 text-accent" />
            <h3 className="text-sm font-semibold text-neutral-900">AI Processing Logs</h3>
          </div>
          <div className="flex items-center gap-1 text-xs text-neutral-500">
            <Clock className="w-3 h-3" />
            <span>{logs.length} events</span>
          </div>
        </div>
      </div>
      <div
        ref={scrollRef}
        className="h-80 overflow-y-auto bg-neutral-50/50 p-3 space-y-2"
      >
        {logs.map((log, index) => (
          <div 
            key={index} 
            className={`flex items-start gap-3 p-3 rounded-lg border ${getLogColor(log.type)} transition-all duration-200`}
          >
            <div className="flex-shrink-0 mt-0.5">
              {getLogIcon(log.type)}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-neutral-900 break-words">{log.message}</p>
              <p className="text-xs text-neutral-500 mt-1">{formatTime(log.timestamp)}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default LiveLogViewer;
