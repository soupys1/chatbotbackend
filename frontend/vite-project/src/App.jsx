import React, { useState, useRef, useEffect } from 'react';
import { 
  Send, User, Bot, Loader2, Heart, AlertTriangle, Activity, Brain, 
  HelpCircle, Shield, Zap, Mic, Image, Paperclip, Stethoscope
} from 'lucide-react';

const urgencyColors = {
  emergency: '#ef4444',
  medium: '#f59e0b',
  low: '#10b981'
};

const categoryIcons = {
  physical_symptoms: <Activity style={{ width: '16px', height: '16px' }} />,
  mental_health: <Brain style={{ width: '16px', height: '16px' }} />,
  chronic_conditions: <Heart style={{ width: '16px', height: '16px' }} />,
  lifestyle: <Zap style={{ width: '16px', height: '16px' }} />
};

const HealthChatBot = () => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      text: "Hi! I'm your AI health assistant. Tell me about any health concerns, symptoms, or lifestyle questions you have, and I'll provide personalized health advice and recommendations.",
      sender: 'bot',
      timestamp: new Date(),
    },
  ]);
  const [inputText, setInputText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [lastAnalysis, setLastAnalysis] = useState(null);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSendMessage = async () => {
    if (!inputText.trim()) return;

    const userMessage = {
      id: Date.now(),
      text: inputText,
      sender: 'user',
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputText('');
    setIsTyping(true);

    try {
      // Call the health analysis API
      const response = await fetch('http://localhost:5000/analyze-health', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text: inputText }),
      });

      const data = await response.json();
      console.log('API response:', data); // Debug log

      if (data.success && data.data) {
        const analysis = data.data;
        setLastAnalysis(analysis);
        
        // Generate response based on analysis
        let responseText = generateHealthResponse(analysis);
        
        const botResponse = {
          id: Date.now() + 1,
          text: responseText,
          sender: 'bot',
          timestamp: new Date(),
          analysis: analysis,
          isJSX: true,
        };
        
        setMessages((prev) => [...prev, botResponse]);
      } else {
        // Handle API error or unexpected response
        const errorMsg = data.error || 'Sorry, I could not analyze your health concern. Please try again or consult a healthcare provider.';
        const botResponse = {
          id: Date.now() + 1,
          text: errorMsg,
          sender: 'bot',
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, botResponse]);
        setLastAnalysis(null);
      }
    } catch (error) {
      console.error('Error calling health API:', error);
      
      const botResponse = {
        id: Date.now() + 1,
        text: "I'm sorry, I'm unable to connect to my health analysis system right now. Please try again later or consult a healthcare provider for immediate assistance.",
        sender: 'bot',
        timestamp: new Date(),
      };
      
      setMessages((prev) => [...prev, botResponse]);
      setLastAnalysis(null);
    }

      setIsTyping(false);
  };

  const generateHealthResponse = (analysis) => {
    if (!analysis || typeof analysis !== 'object') {
      return <span>Sorry, I could not analyze your health concern. Please try again or consult a healthcare provider.</span>;
    }
    // Defensive destructuring with defaults
    const {
      emergency_check = {},
      health_categories = {},
      urgency_level = '',
      health_advice = [],
      recommendation = ''
    } = analysis;

    let response = [];

    // Emergency warning
    if (emergency_check && emergency_check.is_emergency) {
      response.push(
        <div key="emergency" style={{ 
          backgroundColor: '#fee2e2', 
          border: '1px solid #fecaca', 
          borderRadius: '8px', 
          padding: '12px', 
          marginBottom: '12px',
          color: '#dc2626'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
            <AlertTriangle size={16} />
            <strong>EMERGENCY WARNING</strong>
          </div>
          <p style={{ margin: 0, fontSize: '14px' }}>
            {emergency_check.advice || 'Call emergency services (911) immediately!'} The symptoms you described may require immediate medical attention.
          </p>
        </div>
      );
    }

    // Health categories detected
    const detectedCategories = Object.entries(health_categories)
      .filter(([_, score]) => score > 0.3)
      .sort(([_, a], [__, b]) => b - a);

    if (detectedCategories.length > 0) {
      response.push(
        <div key="categories" style={{ marginBottom: '12px' }}>
          <p style={{ margin: '0 0 8px 0', fontSize: '14px', color: '#6b7280' }}>
            I detected the following health areas in your concern:
          </p>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
            {detectedCategories.map(([category, score]) => (
              <span key={category} style={{
                display: 'flex',
                alignItems: 'center',
                gap: '4px',
                padding: '4px 8px',
                backgroundColor: '#374151',
                borderRadius: '12px',
                fontSize: '12px',
                color: '#d1d5db'
              }}>
                {categoryIcons[category]}
                {category.replace('_', ' ')}
              </span>
            ))}
          </div>
        </div>
      );
    }

    // Urgency level
    response.push(
      <div key="urgency" style={{ 
        display: 'flex', 
        alignItems: 'center', 
        gap: '8px', 
        marginBottom: '12px',
        padding: '8px 12px',
        backgroundColor: '#1f2937',
        borderRadius: '8px',
        border: `1px solid ${urgencyColors[urgency_level] || '#6b7280'}`
      }}>
        <div style={{ 
          width: '8px', 
          height: '8px', 
          borderRadius: '50%', 
          backgroundColor: urgencyColors[urgency_level] || '#6b7280' 
        }} />
        <span style={{ fontSize: '14px', color: '#d1d5db' }}>
          <strong>Urgency Level:</strong> {urgency_level ? (urgency_level.charAt(0).toUpperCase() + urgency_level.slice(1)) : 'Unknown'}
        </span>
      </div>
    );

    // Health advice
    if (Array.isArray(health_advice) && health_advice.length > 0) {
      response.push(
        <div key="advice" style={{ marginBottom: '12px' }}>
          <p style={{ margin: '0 0 8px 0', fontSize: '14px', color: '#d1d5db' }}>
            <strong>Health Advice:</strong>
          </p>
          <ul style={{ margin: 0, paddingLeft: '20px', fontSize: '14px', color: '#d1d5db' }}>
            {health_advice.map((advice, index) => (
              <li key={index} style={{ marginBottom: '4px' }}>{advice}</li>
            ))}
          </ul>
        </div>
      );
    }

    // Recommendation
    if (recommendation) {
      response.push(
        <div key="recommendation" style={{ 
          backgroundColor: '#1e40af', 
          border: '1px solid #3b82f6', 
          borderRadius: '8px', 
          padding: '12px',
          marginTop: '12px'
        }}>
          <p style={{ margin: 0, fontSize: '14px', color: '#dbeafe' }}>
            <strong>Recommendation:</strong> {recommendation}
          </p>
        </div>
      );
    }

    return response;
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const formatTime = (timestamp) => {
    return timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const styles = {
    container: {
      backgroundColor: '#111827',
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      color: 'white',
      fontFamily: 'system-ui, -apple-system, sans-serif',
      padding: '16px',
    },
    chatContainer: {
      width: '100%',
      maxWidth: '672px',
      backgroundColor: '#1f2937',
      borderRadius: '16px',
      boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
      border: '1px solid #374151',
      display: 'flex',
      flexDirection: 'column',
      height: '85vh',
      overflow: 'hidden',
    },
    header: {
      backgroundColor: '#1f2937',
      borderBottom: '1px solid #374151',
      padding: '16px 24px',
      display: 'flex',
      alignItems: 'center',
      gap: '12px',
    },
    headerIcon: {
      width: '40px',
      height: '40px',
      background: 'linear-gradient(to right, #10b981, #059669)',
      borderRadius: '50%',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
    },
    headerTitle: {
      fontWeight: '600',
      fontSize: '18px',
      margin: 0,
    },
    headerSubtitle: {
      fontSize: '14px',
      color: '#9ca3af',
      margin: 0,
    },
    statusBar: {
      padding: '12px 24px',
      backgroundColor: '#374151',
      borderBottom: '1px solid #374151',
    },
    statusContent: {
      display: 'flex',
      alignItems: 'center',
      gap: '8px',
      fontSize: '14px',
      color: '#d1d5db',
    },
    messagesArea: {
      flex: 1,
      overflowY: 'auto',
      padding: '24px',
      display: 'flex',
      flexDirection: 'column',
      gap: '24px',
    },
    messageWrapper: {
      display: 'flex',
      animation: 'fadeIn 0.5s ease-out',
    },
    messageWrapperUser: {
      justifyContent: 'flex-end',
    },
    messageContent: {
      display: 'flex',
      alignItems: 'flex-start',
      gap: '16px',
      maxWidth: '448px',
    },
    messageContentUser: {
      flexDirection: 'row-reverse',
    },
    avatar: {
      width: '40px',
      height: '40px',
      borderRadius: '50%',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      flexShrink: 0,
    },
    avatarUser: {
      background: 'linear-gradient(to right, #3b82f6, #8b5cf6)',
    },
    avatarBot: {
      background: 'linear-gradient(to right, #10b981, #059669)',
    },
    messageBubble: {
      borderRadius: '16px',
      padding: '16px 20px',
    },
    messageBubbleUser: {
      background: 'linear-gradient(to right, #3b82f6, #8b5cf6)',
      color: 'white',
    },
    messageBubbleBot: {
      backgroundColor: '#374151',
      color: '#f3f4f6',
    },
    messageText: {
      fontSize: '14px',
      lineHeight: '1.5',
      margin: 0,
    },
    messageTime: {
      fontSize: '12px',
      marginTop: '8px',
      opacity: 0.7,
    },
    inputArea: {
      padding: '24px',
      backgroundColor: '#1f2937',
      borderTop: '1px solid #374151',
    },
    inputWrapper: {
      display: 'flex',
      alignItems: 'flex-end',
      gap: '12px',
    },
    inputButton: {
      padding: '12px',
      color: '#9ca3af',
      backgroundColor: 'transparent',
      border: 'none',
      borderRadius: '12px',
      cursor: 'pointer',
      transition: 'all 0.2s',
    },
    inputContainer: {
      flex: 1,
      backgroundColor: '#374151',
      borderRadius: '16px',
    },
    textarea: {
      width: '100%',
      backgroundColor: 'transparent',
      color: 'white',
      border: 'none',
      outline: 'none',
      resize: 'none',
      padding: '16px',
      borderRadius: '16px',
      minHeight: '52px',
      maxHeight: '128px',
      fontSize: '14px',
      fontFamily: 'inherit',
    },
    sendButton: {
      background: 'linear-gradient(to right, #10b981, #059669)',
      color: 'white',
      padding: '12px',
      borderRadius: '12px',
      border: 'none',
      cursor: 'pointer',
      transition: 'all 0.2s',
      boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
    },
    sendButtonDisabled: {
      background: 'linear-gradient(to right, #4b5563, #4b5563)',
      cursor: 'not-allowed',
    },
    typingIndicator: {
      display: 'flex',
      justifyContent: 'flex-start',
      animation: 'fadeIn 0.5s ease-out',
    },
    typingContent: {
      display: 'flex',
      alignItems: 'flex-start',
      gap: '16px',
      maxWidth: '448px',
    },
    typingBubble: {
      backgroundColor: '#374151',
      borderRadius: '16px',
      padding: '16px 20px',
    },
    typingText: {
      display: 'flex',
      alignItems: 'center',
      gap: '12px',
    },
  };

  return (
    <div style={styles.container}>
      <div style={styles.chatContainer}>
        {/* Chat Header */}
        <div style={styles.header}>
          <div style={styles.headerIcon}>
            <Stethoscope size={24} color="white" />
          </div>
          <div>
            <h2 style={styles.headerTitle}>AI Health Assistant</h2>
            <p style={styles.headerSubtitle}>Get personalized health advice and recommendations</p>
          </div>
        </div>

        {/* ML/Rule-based Status Bar */}
        <div style={{ ...styles.statusBar, backgroundColor: '#d1fae5', color: '#065f46', borderBottom: '1px solid #374151', display: 'flex', alignItems: 'center', gap: 12 }}>
          <span style={{ fontWeight: 600 }}>
            🤖 ML-Enhanced (RoBERTa)
          </span>
          <span style={{ fontSize: 13, opacity: 0.8 }}>
            Using RoBERTa for sentiment analysis
          </span>
        </div>

        {/* Status Bar for last analysis (urgency, etc.) */}
        {lastAnalysis && (
          <div style={styles.statusBar}>
            <div style={styles.statusContent}>
              <div style={{ 
                width: '8px', 
                height: '8px', 
                borderRadius: '50%', 
                backgroundColor: urgencyColors[lastAnalysis && lastAnalysis.urgency_level] || '#6b7280' 
              }} />
              <span>
                <strong>Urgency:</strong> {lastAnalysis && lastAnalysis.urgency_level ? (lastAnalysis.urgency_level.charAt(0).toUpperCase() + lastAnalysis.urgency_level.slice(1)) : 'Unknown'}
              </span>
              {lastAnalysis && lastAnalysis.emergency_check && lastAnalysis.emergency_check.is_emergency && (
                <span style={{ color: '#ef4444', fontWeight: '600' }}>
                  • EMERGENCY DETECTED
                </span>
              )}
              {/* Show analysis method for this result */}
              <span style={{ marginLeft: 16, fontSize: 13, opacity: 0.7 }}>
                <strong>Analysis:</strong> ML (RoBERTa)
              </span>
            </div>
          </div>
        )}

        {/* Messages Area */}
        <div style={styles.messagesArea}>
          {messages.map((message) => (
            <div
              key={message.id}
              style={{
                ...styles.messageWrapper,
                ...(message.sender === 'user' ? styles.messageWrapperUser : {}),
              }}
            >
              <div
                style={{
                ...styles.messageContent,
                ...(message.sender === 'user' ? styles.messageContentUser : {}),
                }}
              >
                <div
                  style={{
                  ...styles.avatar,
                  ...(message.sender === 'user' ? styles.avatarUser : styles.avatarBot),
                  }}
                >
                  {message.sender === 'user' ? (
                    <User size={20} color="white" />
                  ) : (
                    <Bot size={20} color="white" />
                  )}
                </div>
                <div
                  style={{
                  ...styles.messageBubble,
                  ...(message.sender === 'user' ? styles.messageBubbleUser : styles.messageBubbleBot),
                  }}
                >
                  <div style={styles.messageText}>
                    {message.isJSX ? message.text : message.text}
                  </div>
                  <div style={styles.messageTime}>
                    {formatTime(message.timestamp)}
                  </div>
                </div>
              </div>
            </div>
          ))}
          
          {/* Typing Indicator */}
          {isTyping && (
            <div style={styles.typingIndicator}>
              <div style={styles.typingContent}>
                <div style={styles.avatar}>
                  <Bot size={20} color="white" />
                </div>
                <div style={styles.typingBubble}>
                  <div style={styles.typingText}>
                    <Loader2 size={16} className="animate-spin" />
                    <span>Analyzing your health concern...</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div style={styles.inputArea}>
          <div style={styles.inputWrapper}>
            <button style={styles.inputButton}>
              <Mic size={20} />
            </button>
            <div style={styles.inputContainer}>
              <textarea
                style={styles.textarea}
                placeholder="Describe your health concern, symptoms, or ask for health advice..."
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                onKeyPress={handleKeyPress}
                rows={1}
              />
            </div>
            <button
              style={{
                ...styles.sendButton,
                ...(isTyping || !inputText.trim() ? styles.sendButtonDisabled : {}),
              }}
              onClick={handleSendMessage}
              disabled={isTyping || !inputText.trim()}
            >
              <Send size={20} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HealthChatBot;