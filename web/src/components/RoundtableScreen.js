import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Send, 
  SkipForward, 
  Users, 
  MessageCircle, 
  ArrowLeft,
  FileText,
  ChevronDown,
  MoreHorizontal
} from 'lucide-react';
import TypewriterText from './TypewriterText';

const RoundtableScreen = ({
  sessionData,
  messages,
  streamingMessages,
  onGenerateNext,
  onAddMessage,
  onEndDiscussion,
  onBackToSpark
}) => {
  const [userMessage, setUserMessage] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [showAllMessages, setShowAllMessages] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // AI Agent personas with distinct styling
  const agentPersonas = {
    'Dr. Data': {
      color: 'from-blue-500 to-blue-600',
      bgColor: 'bg-blue-50',
      borderColor: 'border-blue-200',
      textColor: 'text-blue-900',
      emoji: '📊',
      role: 'Evidence-Based Researcher',
      description: 'Brings hard facts and data'
    },
    'Dr. Synthesis': {
      color: 'from-green-500 to-green-600',
      bgColor: 'bg-green-50',
      borderColor: 'border-green-200',
      textColor: 'text-green-900',
      emoji: '💡',
      role: 'Integrative Thinker',
      description: 'Connects ideas and builds consensus'
    },
    'Dr. Skeptic': {
      color: 'from-red-500 to-red-600',
      bgColor: 'bg-red-50',
      borderColor: 'border-red-200',
      textColor: 'text-red-900',
      emoji: '❓',
      role: 'Critical Analyst',
      description: 'Questions assumptions and identifies flaws'
    },
    'Dr. Discovery': {
      color: 'from-purple-500 to-purple-600',
      bgColor: 'bg-purple-50',
      borderColor: 'border-purple-200',
      textColor: 'text-purple-900',
      emoji: '🔮',
      role: 'Creative Visionary',
      description: 'Generates novel perspectives'
    }
  };

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Focus input when screen loads
  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.focus();
    }
  }, []);


  const handleSendMessage = async (e) => {
    e.preventDefault();
    
    if (!userMessage.trim()) return;
    
    const message = userMessage.trim();
    setUserMessage('');
    
    try {
      await onAddMessage(message);
      inputRef.current?.focus();
    } catch (error) {
      console.error('Failed to send message:', error);
    }
  };

  const handleGenerateNext = async () => {
    setIsGenerating(true);
    try {
      await onGenerateNext();
    } catch (error) {
      console.error('Failed to generate responses:', error);
    } finally {
      setIsGenerating(false);
    }
  };

  const formatMessage = (message) => {
    const timestamp = new Date(message.timestamp);
    const timeString = timestamp.toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    });

    if (message.type === 'human') {
      return (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex justify-end mb-4"
        >
          <div className="max-w-lg bg-white rounded-lg shadow-sm border p-4">
            <div className="flex items-center mb-2">
              <div className="w-8 h-8 bg-gradient-to-r from-gray-400 to-gray-500 rounded-full flex items-center justify-center text-white font-semibold text-sm mr-3">
                👤
              </div>
              <div>
                <div className="font-semibold text-gray-900">{message.speaker}</div>
                <div className="text-xs text-gray-500">{timeString}</div>
              </div>
            </div>
            <div className="text-gray-800 whitespace-pre-wrap">{message.content}</div>
          </div>
        </motion.div>
      );
    }

    if (message.type === 'agent') {
      const persona = agentPersonas[message.speaker] || agentPersonas['Dr. Data'];
      
      return (
        <motion.div
          initial={{ opacity: 0, x: -20, scale: 0.95 }}
          animate={{ opacity: 1, x: 0, scale: 1 }}
          transition={{ duration: 0.5, ease: "easeOut" }}
          className="flex justify-start mb-4"
        >
          <div className={`max-w-2xl ${persona.bgColor} ${persona.borderColor} border rounded-lg shadow-sm p-4`}>
            <div className="flex items-center mb-3">
              <div className={`w-10 h-10 bg-gradient-to-r ${persona.color} rounded-full flex items-center justify-center text-white text-lg mr-3`}>
                {persona.emoji}
              </div>
              <div>
                <div className={`font-semibold ${persona.textColor}`}>{message.speaker}</div>
                <div className="text-xs text-gray-500 flex items-center">
                  <span className="mr-2">{persona.role}</span>
                  <span>•</span>
                  <span className="ml-2">{timeString}</span>
                </div>
              </div>
            </div>
            <div className={`${persona.textColor} whitespace-pre-wrap leading-relaxed`} style={{ 
              wordWrap: 'break-word', 
              overflowWrap: 'break-word',
              maxWidth: '100%',
              display: 'block' 
            }}>
              {message.content}
            </div>
          </div>
        </motion.div>
      );
    }

    return null;
  };

  const displayMessages = showAllMessages ? messages : messages.slice(-10);
  const hasMoreMessages = messages.length > 10 && !showAllMessages;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white border-b border-gray-200 p-4 sticky top-0 z-10"
      >
        <div className="container flex items-center justify-between">
          <div className="flex items-center">
            <button
              onClick={onBackToSpark}
              className="btn btn-ghost btn-small mr-4"
            >
              <ArrowLeft className="w-4 h-4" />
              Back
            </button>
            
            <div>
              <h1 className="heading-3 text-gray-900">Live Discussion</h1>
              <p className="text-gray-600 text-sm truncate max-w-md">
                {sessionData?.topic || 'Loading...'}
              </p>
            </div>
          </div>
          
          <div className="flex items-center space-x-3">
            <div className="flex items-center text-sm text-gray-500">
              <Users className="w-4 h-4 mr-1" />
              4 AI agents
            </div>
            <button
              onClick={onEndDiscussion}
              className="btn btn-secondary btn-small"
            >
              <FileText className="w-4 h-4" />
              Get Briefing
            </button>
          </div>
        </div>
      </motion.div>

      {/* Messages Area */}
      <div className="container py-6">
        <div className="max-w-4xl mx-auto">
          
          {/* Agent Intro Cards */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="grid md:grid-cols-2 gap-4 mb-8"
          >
            {Object.entries(agentPersonas).map(([name, persona]) => (
              <div key={name} className={`${persona.bgColor} ${persona.borderColor} border rounded-lg p-4`}>
                <div className="flex items-center">
                  <div className={`w-8 h-8 bg-gradient-to-r ${persona.color} rounded-full flex items-center justify-center text-white mr-3`}>
                    {persona.emoji}
                  </div>
                  <div>
                    <h3 className={`font-semibold ${persona.textColor}`}>{name}</h3>
                    <p className="text-xs text-gray-600">{persona.description}</p>
                  </div>
                </div>
              </div>
            ))}
          </motion.div>

          {/* Messages */}
          <div className="bg-white rounded-lg shadow-sm border min-h-96 mb-6">
            <div className="p-6">
              
              {/* Show more messages button */}
              {hasMoreMessages && (
                <div className="text-center mb-6">
                  <button
                    onClick={() => setShowAllMessages(true)}
                    className="btn btn-ghost btn-small"
                  >
                    <ChevronDown className="w-4 h-4" />
                    Show {messages.length - 10} earlier messages
                  </button>
                </div>
              )}
              
              {/* Message list */}
              <AnimatePresence>
                {displayMessages.length > 0 ? (
                  <>
                    {displayMessages.map((message, index) => (
                      <div key={`${message.timestamp}-${index}`}>
                        {formatMessage(message)}
                      </div>
                    ))}
                    {/* Live streaming messages */}
                    {Object.values(streamingMessages || {}).map((msg) => {
                      const persona = agentPersonas[msg.speaker] || agentPersonas['Dr. Data'];
                      const timeString = new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
                      return (
                        <motion.div
                          key={`stream-${msg.id}`}
                          initial={{ opacity: 0, x: -20, scale: 0.95 }}
                          animate={{ opacity: 1, x: 0, scale: 1 }}
                          transition={{ duration: 0.4, ease: "easeOut" }}
                          className="flex justify-start mb-4"
                        >
                          <div className={`max-w-2xl ${persona.bgColor} ${persona.borderColor} border rounded-lg shadow-sm p-4`}>
                            <div className="flex items-center mb-3">
                              <div className={`w-10 h-10 bg-gradient-to-r ${persona.color} rounded-full flex items-center justify-center text-white text-lg mr-3`}>
                                {persona.emoji}
                              </div>
                              <div>
                                <div className={`font-semibold ${persona.textColor}`}>{msg.speaker}</div>
                                <div className="text-xs text-gray-500 flex items-center">
                                  <span className="mr-2">{persona.role}</span>
                                  <span>•</span>
                                  <span className="ml-2">{timeString}</span>
                                </div>
                              </div>
                            </div>
                            <div className={`${persona.textColor} whitespace-pre-wrap leading-relaxed`} style={{ 
                              wordWrap: 'break-word', 
                              overflowWrap: 'break-word',
                              maxWidth: '100%',
                              display: 'block' 
                            }}>
                              <TypewriterText text={msg.content} incremental={true} speed={30} className="leading-relaxed" />
                            </div>
                          </div>
                        </motion.div>
                      );
                    })}
                  </>
                ) : (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="text-center py-12"
                  >
                    <MessageCircle className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                    <h3 className="heading-3 text-gray-500 mb-2">Ready to brainstorm!</h3>
                    <p className="text-gray-400">
                      Click "Let agents discuss" to start the AI roundtable, or add your own thoughts first.
                    </p>
                  </motion.div>
                )}
              </AnimatePresence>
              
              {/* Typing indicator */}
              {isGenerating && (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="flex items-center text-gray-500 mb-4"
                >
                  <div className="flex space-x-1 mr-3">
                    <motion.div
                      animate={{ scale: [1, 1.2, 1] }}
                      transition={{ duration: 0.6, repeat: Infinity, delay: 0 }}
                      className="w-2 h-2 bg-gray-400 rounded-full"
                    />
                    <motion.div
                      animate={{ scale: [1, 1.2, 1] }}
                      transition={{ duration: 0.6, repeat: Infinity, delay: 0.2 }}
                      className="w-2 h-2 bg-gray-400 rounded-full"
                    />
                    <motion.div
                      animate={{ scale: [1, 1.2, 1] }}
                      transition={{ duration: 0.6, repeat: Infinity, delay: 0.4 }}
                      className="w-2 h-2 bg-gray-400 rounded-full"
                    />
                  </div>
                  <span className="text-sm">AI agents are thinking...</span>
                </motion.div>
              )}
              
              <div ref={messagesEndRef} />
            </div>
          </div>

          {/* Input Area */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white rounded-lg shadow-sm border p-4"
          >
            <form onSubmit={handleSendMessage} className="flex gap-3">
              <textarea
                ref={inputRef}
                value={userMessage}
                onChange={(e) => setUserMessage(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleSendMessage(e);
                  }
                }}
                placeholder="Add your thoughts to the discussion..."
                disabled={isGenerating}
                className="flex-1 px-4 py-3 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                style={{
                  color: '#1f2937 !important',
                  backgroundColor: '#ffffff !important',
                  border: '2px solid #e5e7eb',
                  fontSize: '16px',
                  fontFamily: 'Inter, sans-serif',
                  minHeight: '48px',
                  maxHeight: '120px',
                  lineHeight: '1.5',
                  textSecurity: 'none',
                  WebkitTextSecurity: 'none',
                  WebkitTextFillColor: '#1f2937 !important'
                }}
                rows={1}
              />
              <button
                type="submit"
                disabled={!userMessage.trim() || isGenerating}
                className="btn btn-primary"
                style={{
                  backgroundColor: 'rgba(59, 130, 246, 0.9)',
                  color: 'white',
                  border: 'none',
                  padding: '12px',
                  borderRadius: '8px',
                  minWidth: '48px',
                  opacity: (!userMessage.trim() || isGenerating) ? 0.5 : 1
                }}
              >
                <Send className="w-4 h-4" />
              </button>
            </form>
            
            <div className="flex justify-between items-center mt-4 pt-4 border-t border-gray-100">
              <p className="text-sm text-gray-500">
                💡 Add your thoughts or let the AI team continue the discussion
              </p>
              
              <button
                onClick={handleGenerateNext}
                disabled={isGenerating}
                className="btn btn-secondary flex items-center"
                style={{
                  backgroundColor: 'rgba(59, 130, 246, 0.8)',
                  color: 'white',
                  border: '2px solid rgba(59, 130, 246, 0.6)',
                  padding: '12px 20px',
                  borderRadius: '8px',
                  fontWeight: '600',
                  minWidth: '160px'
                }}
              >
                {isGenerating ? (
                  <>
                    <MoreHorizontal className="w-4 h-4 animate-pulse" />
                    Generating...
                  </>
                ) : (
                  <>
                    <SkipForward className="w-4 h-4" />
                    Let agents discuss
                  </>
                )}
              </button>
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  );
};

export default RoundtableScreen;