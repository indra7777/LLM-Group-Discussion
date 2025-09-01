import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

const TypewriterText = ({
  text,
  speed = 50,
  onComplete = () => {},
  className = '',
  cursorColor = 'var(--text-accent)',
  incremental = false
}) => {
  const [displayText, setDisplayText] = useState('');
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isComplete, setIsComplete] = useState(false);

  useEffect(() => {
    if (incremental) {
      // Animate toward latest text by adding a character every tick until we match
      if (displayText.length < text.length) {
        const timer = setTimeout(() => {
          setDisplayText(prev => text.slice(0, prev.length + 1));
        }, Math.max(10, speed));
        return () => clearTimeout(timer);
      }
      return;
    }

    if (currentIndex < text.length) {
      const timer = setTimeout(() => {
        setDisplayText(prev => prev + text[currentIndex]);
        setCurrentIndex(prev => prev + 1);
      }, speed);

    	return () => clearTimeout(timer);
    } else if (!isComplete) {
      setIsComplete(true);
      setTimeout(() => {
        onComplete();
      }, 500);
    }
  }, [incremental, displayText.length, currentIndex, text, speed, onComplete, isComplete]);

  // Reset when text changes (only for non-incremental mode)
  useEffect(() => {
    if (!incremental) {
      setDisplayText('');
      setCurrentIndex(0);
      setIsComplete(false);
    }
  }, [text, incremental]);

  return (
    <span className={className}>
      {displayText}
      {!isComplete && (
        <motion.span
          animate={{ opacity: [1, 0] }}
          transition={{ 
            duration: 0.5, 
            repeat: Infinity, 
            repeatType: "reverse" 
          }}
          style={{ 
            color: cursorColor,
            marginLeft: '2px'
          }}
        >
          |
        </motion.span>
      )}
    </span>
  );
};

export default TypewriterText;