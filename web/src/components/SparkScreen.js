import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Lightbulb, 
  Zap, 
  Brain, 
  Wifi, 
  WifiOff, 
  Sparkles,
  ArrowRight,
  Play,
  TrendingUp,
  Users,
  Clock
} from 'lucide-react';

const SparkScreen = ({ onStartDiscussion, isConnected }) => {
  const [topic, setTopic] = useState('');
  const [selectedGoal, setSelectedGoal] = useState('explore');
  const [isLoading, setIsLoading] = useState(false);
  const [currentPlaceholder, setCurrentPlaceholder] = useState(0);
  const [showGoals, setShowGoals] = useState(false);
  const inputRef = useRef(null);

  const placeholderExamples = [
    "Why do some people become millionaires while others with the same skills stay broke?",
    "The hidden psychology behind why Netflix shows get cancelled after one season", 
    "Why your brain craves social media but leaves you feeling empty afterward",
    "The surprising reason why introverts often become the most successful CEOs",
    "Why do we remember song lyrics from 20 years ago but forget where we put our keys?",
    "The dark truth about why 'follow your passion' is terrible career advice"
  ];

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentPlaceholder((prev) => (prev + 1) % placeholderExamples.length);
    }, 4000);
    return () => clearInterval(interval);
  }, [placeholderExamples.length]);

  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.focus();
    }
  }, []);

  useEffect(() => {
    if (topic.trim().length > 10 && !showGoals) {
      setShowGoals(true);
    } else if (topic.trim().length <= 10 && showGoals) {
      setShowGoals(false);
    }
  }, [topic, showGoals]);

  const goals = [
    {
      id: 'explore',
      label: 'Find Hidden Angles',
      icon: Lightbulb,
      description: 'Uncover surprising perspectives that make people think',
      color: '#f59e0b',
      time: '3-5 min'
    },
    {
      id: 'outline',
      label: 'Build Viral Content',
      icon: TrendingUp,
      description: 'Structure that hooks viewers and keeps them watching',
      color: '#3b82f6',
      time: '5-7 min'
    },
    {
      id: 'stress_test',
      label: 'Bulletproof Ideas',
      icon: Zap,
      description: 'Prepare for critics and tough questions',
      color: '#ef4444',
      time: '4-6 min'
    }
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!topic.trim()) {
      inputRef.current?.focus();
      return;
    }

    setIsLoading(true);
    
    try {
      await onStartDiscussion(topic.trim(), selectedGoal);
    } catch (error) {
      console.error('Failed to start discussion:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const containerStyle = {
    minHeight: '100vh',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '2rem'
  };

  const mainCardStyle = {
    background: 'rgba(255, 255, 255, 0.05)',
    backdropFilter: 'blur(20px)',
    border: '1px solid rgba(255, 255, 255, 0.1)',
    borderRadius: '24px',
    padding: '3rem',
    maxWidth: '600px',
    width: '100%',
    boxShadow: '0 25px 50px rgba(0, 0, 0, 0.3)'
  };

  const inputStyle = {
    width: '100%',
    height: '120px',
    padding: '1.5rem',
    fontSize: '16px',
    background: 'rgba(255, 255, 255, 0.05)',
    border: '2px solid rgba(255, 255, 255, 0.1)',
    borderRadius: '16px',
    color: 'white',
    resize: 'none',
    outline: 'none',
    fontFamily: 'Inter, sans-serif',
    lineHeight: 1.6
  };

  const goalCardStyle = (goal, isSelected) => ({
    background: isSelected ? 'rgba(59, 130, 246, 0.2)' : 'rgba(255, 255, 255, 0.05)',
    border: `2px solid ${isSelected ? 'rgba(59, 130, 246, 0.5)' : 'rgba(255, 255, 255, 0.1)'}`,
    borderRadius: '16px',
    padding: '1.5rem',
    cursor: 'pointer',
    transition: 'all 0.3s ease',
    marginBottom: '12px'
  });

  return (
    <div style={containerStyle}>
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
        style={mainCardStyle}
      >
        {/* Header */}
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '1rem' }}>
            <motion.div
              animate={{ 
                rotate: [0, 360],
                scale: [1, 1.1, 1]
              }}
              transition={{ 
                duration: 4,
                repeat: Infinity,
                ease: "easeInOut"
              }}
              style={{ marginRight: '12px' }}
            >
              <Brain style={{ width: '48px', height: '48px', color: '#60a5fa' }} />
            </motion.div>
            <div>
              <h2 style={{ fontSize: '1.5rem', fontWeight: 'bold', color: 'white', marginBottom: '4px' }}>
                AI Dream Team
              </h2>
              <p style={{ color: '#93c5fd', fontSize: '14px' }}>Content Strategy Platform</p>
            </div>
          </div>
          
          <h1 className="heading-display" style={{ marginBottom: '1rem' }}>
            Turn Ideas Into Viral Content
          </h1>
          
          <p style={{ fontSize: '18px', color: '#d1d5db', lineHeight: 1.6, marginBottom: '1rem' }}>
            4 AI specialists analyze, strategize, and optimize your content ideas in real-time.
          </p>

          {/* Connection Status */}
          <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '2rem' }}>
            {isConnected ? (
              <div style={{
                display: 'flex',
                alignItems: 'center',
                background: 'rgba(16, 185, 129, 0.2)',
                border: '1px solid rgba(16, 185, 129, 0.3)',
                borderRadius: '12px',
                padding: '8px 16px',
                gap: '8px'
              }}>
                <Wifi style={{ width: '16px', height: '16px', color: '#10b981' }} />
                <span style={{ color: '#10b981', fontWeight: 500 }}>AI Team Online</span>
                <div style={{ width: '8px', height: '8px', background: '#10b981', borderRadius: '50%' }} />
              </div>
            ) : (
              <div style={{
                display: 'flex',
                alignItems: 'center',
                background: 'rgba(251, 191, 36, 0.2)',
                border: '1px solid rgba(251, 191, 36, 0.3)',
                borderRadius: '12px',
                padding: '8px 16px',
                gap: '8px'
              }}>
                <WifiOff style={{ width: '16px', height: '16px', color: '#f59e0b' }} />
                <span style={{ color: '#f59e0b' }}>Connecting...</span>
              </div>
            )}
          </div>
        </div>

        {/* Input Form */}
        <form onSubmit={handleSubmit}>
          {/* Text Input */}
          <div style={{ position: 'relative', marginBottom: '2rem' }}>
            <textarea
              ref={inputRef}
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={placeholderExamples[currentPlaceholder]}
              style={inputStyle}
              disabled={isLoading || !isConnected}
            />
            <motion.div
              style={{ position: 'absolute', top: '16px', right: '16px' }}
              animate={{ 
                rotate: [0, 360],
                scale: [1, 1.1, 1]
              }}
              transition={{ 
                duration: 3,
                repeat: Infinity,
                ease: "easeInOut"
              }}
            >
              <Sparkles style={{ width: '24px', height: '24px', color: 'rgba(96, 165, 250, 0.5)' }} />
            </motion.div>
          </div>

          {/* Goals Section */}
          <AnimatePresence>
            {showGoals && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                transition={{ duration: 0.5 }}
                style={{ marginBottom: '2rem' }}
              >
                <div style={{ textAlign: 'center', marginBottom: '1.5rem' }}>
                  <h4 style={{ fontSize: '18px', fontWeight: 600, color: 'white', marginBottom: '8px' }}>
                    Choose your approach:
                  </h4>
                  <p style={{ color: '#9ca3af', fontSize: '14px' }}>
                    Different strategies for different goals
                  </p>
                </div>

                <div>
                  {goals.map((goal, index) => {
                    const IconComponent = goal.icon;
                    const isSelected = selectedGoal === goal.id;
                    
                    return (
                      <motion.button
                        key={goal.id}
                        type="button"
                        onClick={() => setSelectedGoal(goal.id)}
                        style={goalCardStyle(goal, isSelected)}
                        whileHover={{ y: -2 }}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.1 * index }}
                        disabled={isLoading}
                      >
                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                            <div style={{
                              padding: '12px',
                              borderRadius: '12px',
                              background: `linear-gradient(135deg, ${goal.color}22, ${goal.color}44)`,
                              border: `1px solid ${goal.color}66`
                            }}>
                              <IconComponent style={{ width: '20px', height: '20px', color: goal.color }} />
                            </div>
                            <div style={{ textAlign: 'left' }}>
                              <h5 style={{ fontWeight: 'bold', color: 'white', fontSize: '16px', marginBottom: '4px' }}>
                                {goal.label}
                              </h5>
                              <p style={{ color: '#d1d5db', fontSize: '14px' }}>
                                {goal.description}
                              </p>
                            </div>
                          </div>
                          
                          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '4px', color: '#9ca3af', fontSize: '12px' }}>
                              <Clock style={{ width: '12px', height: '12px' }} />
                              <span>{goal.time}</span>
                            </div>
                            {isSelected && (
                              <motion.div
                                initial={{ scale: 0 }}
                                animate={{ scale: 1 }}
                              >
                                <ArrowRight style={{ width: '20px', height: '20px', color: '#60a5fa' }} />
                              </motion.div>
                            )}
                          </div>
                        </div>
                      </motion.button>
                    );
                  })}
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Submit Button */}
          <motion.button
            type="submit"
            disabled={!topic.trim() || isLoading || !isConnected}
            className="btn btn-primary btn-large"
            style={{ width: '100%', fontSize: '18px', padding: '20px' }}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              {isLoading ? (
                <>
                  <motion.div
                    animate={{ rotate: 360 }}
                    transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                    style={{
                      width: '24px',
                      height: '24px',
                      border: '2px solid white',
                      borderTop: '2px solid transparent',
                      borderRadius: '50%',
                      marginRight: '12px'
                    }}
                  />
                  Assembling AI Team...
                </>
              ) : (
                <>
                  <Play style={{ width: '24px', height: '24px', marginRight: '12px' }} />
                  {showGoals ? 'Start Analysis' : 'Analyze My Idea'}
                </>
              )}
            </div>
          </motion.button>
        </form>

        {/* Trust Indicators */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8 }}
          style={{ 
            display: 'flex', 
            justifyContent: 'center', 
            gap: '2rem', 
            marginTop: '2rem',
            fontSize: '14px',
            color: '#9ca3af'
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div style={{ width: '8px', height: '8px', background: '#10b981', borderRadius: '50%' }} />
            <span>Real-time AI Analysis</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div style={{ width: '8px', height: '8px', background: '#60a5fa', borderRadius: '50%' }} />
            <span>Research Powered</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div style={{ width: '8px', height: '8px', background: '#8b5cf6', borderRadius: '50%' }} />
            <span>Export Ready</span>
          </div>
        </motion.div>
      </motion.div>
    </div>
  );
};

export default SparkScreen;