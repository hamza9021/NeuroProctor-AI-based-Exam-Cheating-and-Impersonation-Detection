import { io } from 'socket.io-client';

const SOCKET_URL = import.meta.env.VITE_API_URL_PYTHON || 'http://localhost:8000';

let socket = null;

export const initializeSocket = () => {
  if (!socket) {
    console.log('Initializing Socket.IO connection to:', SOCKET_URL);
    socket = io(SOCKET_URL, {
      transports: ['websocket', 'polling'],
      withCredentials: true,
    });
    
    socket.on('connect', () => {
      console.log('Socket.IO connected successfully. Socket ID:', socket.id);
    });
    
    socket.on('disconnect', () => {
      console.log('Socket.IO disconnected');
    });
    
    socket.on('error', (error) => {
      console.error('Socket.IO error:', error);
    });
    
    socket.on('connect_error', (error) => {
      console.error('Socket.IO connection error:', error);
    });
    
    // Listen to all events for debugging
    socket.onAny((eventName, ...args) => {
      console.log('Socket.IO received event:', eventName, args);
    });
  }
  
  return socket;
};

export const getSocket = () => {
  if (!socket) {
    return initializeSocket();
  }
  return socket;
};

export const disconnectSocket = () => {
  if (socket) {
    socket.disconnect();
    socket = null;
  }
};
