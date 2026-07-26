import { useEffect, useState } from 'react';
import { getSocket } from '../../utils/socket';

const ProgressPanel = ({ sessionId }) => {
  const [currentFrame, setCurrentFrame] = useState(0);
  const [totalFrames, setTotalFrames] = useState(0);
  const [currentStage, setCurrentStage] = useState('');
  const [percentage, setPercentage] = useState(0);

  useEffect(() => {
    const socket = getSocket();

    const handleStageStarted = (data) => {
      if (!sessionId || data.session_id === sessionId) {
        setCurrentStage(data.stage);
      }
    };

    const handleStageCompleted = (data) => {
      if (!sessionId || data.session_id === sessionId) {
        setCurrentStage('');
      }
    };

    const handlePipelineStarted = (data) => {
      if (!sessionId || data.session_id === sessionId) {
        setCurrentStage('Initializing');
        setPercentage(0);
      }
    };

    const handlePipelineCompleted = (data) => {
      if (!sessionId || data.session_id === sessionId) {
        setCurrentStage('Completed');
        setPercentage(100);
      }
    };

    const handlePipelineFailed = (data) => {
      if (!sessionId || data.session_id === sessionId) {
        setCurrentStage('Failed');
        setPercentage(0);
      }
    };

    socket.on('stage_started', handleStageStarted);
    socket.on('stage_completed', handleStageCompleted);
    socket.on('pipeline_started', handlePipelineStarted);
    socket.on('pipeline_completed', handlePipelineCompleted);
    socket.on('pipeline_failed', handlePipelineFailed);

    return () => {
      socket.off('stage_started', handleStageStarted);
      socket.off('stage_completed', handleStageCompleted);
      socket.off('pipeline_started', handlePipelineStarted);
      socket.off('pipeline_completed', handlePipelineCompleted);
      socket.off('pipeline_failed', handlePipelineFailed);
    };
  }, [sessionId]);

  if (!currentStage && percentage === 0) {
    return null;
  }

  return (
    <div className="bg-neutral-50 rounded-lg p-4 border border-neutral-200">
      <h3 className="text-sm font-semibold text-neutral-700 mb-3">Progress</h3>
      
      <div className="space-y-3">
        {/* Frame Progress */}
        <div>
          <div className="flex justify-between text-xs text-neutral-600 mb-1">
            <span>Frame</span>
            <span>{currentFrame} / {totalFrames || '--'}</span>
          </div>
          <div className="w-full bg-neutral-200 rounded-full h-2">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${percentage}%` }}
            />
          </div>
          <div className="text-right text-xs text-neutral-500 mt-1">{percentage}%</div>
        </div>

        {/* Current Stage */}
        <div>
          <div className="text-xs text-neutral-600 mb-1">Current Stage</div>
          <div className="text-sm font-medium text-neutral-800">{currentStage || 'Idle'}</div>
        </div>
      </div>
    </div>
  );
};

export default ProgressPanel;
