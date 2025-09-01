import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import toast, { Toaster } from 'react-hot-toast';
import SparkScreen from './components/SparkScreen';
import RoundtableScreen from './components/RoundtableScreen';
import BriefingScreen from './components/BriefingScreen';

const App = () => {
  const [currentScreen, setCurrentScreen] = useState(() => {
    return localStorage.getItem('llm-discussion-screen') || 'spark';
  });
  const [sessionData, setSessionData] = useState(() => {
    const saved = localStorage.getItem('llm-discussion-session');
    return saved ? JSON.parse(saved) : null;
  });
  const [websocket, setWebsocket] = useState(null);
  const [messages, setMessages] = useState(() => {
    const saved = localStorage.getItem('llm-discussion-messages');
    return saved ? JSON.parse(saved) : [];
  });
  const [isConnected, setIsConnected] = useState(false);
  const [streamingMessages, setStreamingMessages] = useState({}); // id -> { speaker, content, type, timestamp }

  // Initialize WebSocket connection
  // Get API base URL
  const getApiBaseUrl = () => {
    if (process.env.REACT_APP_API_URL) {
      return process.env.REACT_APP_API_URL;
    }
    // In production, use the same host as the frontend
    if (window.location.hostname !== 'localhost') {
      return `${window.location.protocol}//${window.location.host}`;
    }
    // In development, use localhost:8000
    return 'http://localhost:8000';
  };

  const apiBaseUrl = getApiBaseUrl();

  useEffect(() => {
    let ws = null;
    let reconnectTimeout = null;

    const connectWebSocket = () => {
      const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsHost = window.location.hostname !== 'localhost' ? window.location.host : 'localhost:8000';
      const wsUrl = `${wsProtocol}//${wsHost}/ws`;
      
      ws = new WebSocket(wsUrl);
      
      ws.onopen = () => {
        console.log('WebSocket connected');
        setIsConnected(true);
        setWebsocket(ws);
      };
      
      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        handleWebSocketMessage(data);
      };
      
      ws.onclose = () => {
        console.log('WebSocket disconnected');
        setIsConnected(false);
        setWebsocket(null);
        // Only reconnect if not manually closed
        if (!ws._manualClose) {
          reconnectTimeout = setTimeout(connectWebSocket, 3000);
        }
      };
      
      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        toast.error('Connection error - retrying...');
      };
    };

    connectWebSocket();

    return () => {
      if (reconnectTimeout) {
        clearTimeout(reconnectTimeout);
      }
      if (ws && ws.readyState === WebSocket.OPEN) {
        ws._manualClose = true;
        ws.close();
      }
    };
  }, []);

  // Persist state to localStorage
  useEffect(() => {
    localStorage.setItem('llm-discussion-screen', currentScreen);
  }, [currentScreen]);

  useEffect(() => {
    if (sessionData) {
      localStorage.setItem('llm-discussion-session', JSON.stringify(sessionData));
    }
  }, [sessionData]);

  useEffect(() => {
    localStorage.setItem('llm-discussion-messages', JSON.stringify(messages));
  }, [messages]);

  const handleWebSocketMessage = (data) => {
    switch (data.type) {
      case 'discussion_started':
        setSessionData(data.data);
        setCurrentScreen('roundtable');
        toast.success('Discussion started! The AI team is ready.');
        break;
      case 'new_message':
        setMessages(prev => {
          // Check for duplicate messages by id
          if (prev.find(msg => msg.id === data.data.id)) {
            return prev;
          }
          return [...prev, data.data];
        });
        break;
      case 'message_start': {
        const { id, speaker, type, timestamp } = data.data;
        setStreamingMessages(prev => ({
          ...prev,
          [id]: { id, speaker, type, timestamp, content: '' }
        }));
        break;
      }
      case 'message_chunk': {
        const { id, delta } = data.data;
        setStreamingMessages(prev => {
          const existing = prev[id];
          if (!existing) return prev;
          return { ...prev, [id]: { ...existing, content: (existing.content || '') + delta } };
        });
        break;
      }
      case 'message_end': {
        const complete = data.data;
        setStreamingMessages(prev => {
          const { [complete.id]: _, ...rest } = prev;
          return rest;
        });
        setMessages(prev => {
          // Check for duplicate messages by id
          if (prev.find(msg => msg.id === complete.id)) {
            return prev;
          }
          return [...prev, complete];
        });
        break;
      }
      case 'agents_thinking':
        toast.loading('AI agents are thinking...', { id: 'thinking', duration: 5000 });
        break;
      case 'discussion_ended':
        setCurrentScreen('briefing');
        toast.dismiss('thinking');
        toast.success('Discussion complete! Here\'s your briefing.');
        break;
      default:
        console.log('Unknown message type:', data.type);
    }
  };

  const startDiscussion = async (topic, goal = 'explore') => {
    try {
      const response = await fetch(`${apiBaseUrl}/api/discussion/start`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ topic, goal }),
      });
      
      const result = await response.json();
      
      if (result.success) {
        // WebSocket will handle the screen transition
        return result;
      } else {
        throw new Error(result.message || 'Failed to start discussion');
      }
    } catch (error) {
      toast.error(`Error: ${error.message}`);
      throw error;
    }
  };

  const generateNextRound = async () => {
    try {
      const response = await fetch(`${apiBaseUrl}/api/discussion/next`, {
        method: 'POST',
      });
      
      const result = await response.json();
      
      if (!result.success) {
        if (result.message.includes('reached its limit')) {
          // Discussion is done, move to briefing
          setCurrentScreen('briefing');
          toast.success('Discussion complete! Generating your briefing...');
        } else {
          toast.error(result.message);
        }
      }
      
      return result;
    } catch (error) {
      toast.error(`Error: ${error.message}`);
      throw error;
    }
  };

  const addMessage = async (message, username = 'Human') => {
    try {
      const response = await fetch(`${apiBaseUrl}/api/discussion/speak`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message, username }),
      });
      
      const result = await response.json();
      
      if (!result.success) {
        toast.error(result.message || 'Failed to add message');
      }
      
      return result;
    } catch (error) {
      toast.error(`Error: ${error.message}`);
      throw error;
    }
  };

  const getDiscussionSummary = async () => {
    try {
      const response = await fetch(`${apiBaseUrl}/api/discussion/summary`);
      const result = await response.json();
      
      if (result.success) {
        return result.summary;
      } else {
        throw new Error(result.message || 'Failed to get summary');
      }
    } catch (error) {
      toast.error(`Error: ${error.message}`);
      throw error;
    }
  };

  const resetToSpark = () => {
    setCurrentScreen('spark');
    setSessionData(null);
    setMessages([]);
    // Clear localStorage
    localStorage.removeItem('llm-discussion-screen');
    localStorage.removeItem('llm-discussion-session');
    localStorage.removeItem('llm-discussion-messages');
  };

  return (
    <div className="app">
      <AnimatePresence mode="wait">
        {currentScreen === 'spark' && (
          <motion.div
            key="spark"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.5 }}
          >
            <SparkScreen 
              onStartDiscussion={startDiscussion}
              isConnected={isConnected}
            />
          </motion.div>
        )}
        
        {currentScreen === 'roundtable' && (
          <motion.div
            key="roundtable"
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -50 }}
            transition={{ duration: 0.5 }}
          >
            <RoundtableScreen
              sessionData={sessionData}
              messages={messages}
              streamingMessages={streamingMessages}
              onGenerateNext={generateNextRound}
              onAddMessage={addMessage}
              onEndDiscussion={() => setCurrentScreen('briefing')}
              onBackToSpark={resetToSpark}
            />
          </motion.div>
        )}
        
        {currentScreen === 'briefing' && (
          <motion.div
            key="briefing"
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -50 }}
            transition={{ duration: 0.5 }}
          >
            <BriefingScreen
              sessionData={sessionData}
              messages={messages}
              onGetSummary={getDiscussionSummary}
              onStartNew={resetToSpark}
            />
          </motion.div>
        )}
      </AnimatePresence>
      
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 3000,
          style: {
            background: 'rgba(17, 24, 39, 0.95)',
            color: '#fff',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            borderRadius: '12px',
            backdropFilter: 'blur(10px)',
          },
          success: {
            iconTheme: {
              primary: '#10b981',
              secondary: '#fff',
            },
          },
          error: {
            iconTheme: {
              primary: '#ef4444',
              secondary: '#fff',
            },
          },
        }}
      />
    </div>
  );
};

export default App;