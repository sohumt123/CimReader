import React, { useState, useRef, useEffect } from 'react';
import { 
  Box, 
  Paper, 
  Typography, 
  TextField, 
  Button, 
  CircularProgress,
  Avatar,
  Divider 
} from '@mui/material';
import { useAuth } from './Auth';
import { toast } from 'react-toastify';
import SendIcon from '@mui/icons-material/Send';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import PersonIcon from '@mui/icons-material/Person';

interface Message {
  id: string;
  content: string;
  isUser: boolean;
  timestamp: Date;
}

interface PDFChatProps {
  documentId?: string;
  documentTitle?: string;
}

const PDFChat: React.FC<PDFChatProps> = ({ documentId, documentTitle }) => {
  const { session } = useAuth();
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Add welcome message when component mounts
  useEffect(() => {
    if (documentTitle && messages.length === 0) {
      const welcomeMessage: Message = {
        id: 'welcome',
        content: `Hi! I'm your AI assistant. I've analyzed "${documentTitle}" and I'm ready to answer any questions you have about the document. What would you like to know?`,
        isUser: false,
        timestamp: new Date()
      };
      setMessages([welcomeMessage]);
    }
  }, [documentTitle]);

  const handleSendMessage = async () => {
    if (!inputValue.trim() || !session || !documentId) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputValue.trim(),
      isUser: true,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8000/chat-pdf', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${session.access_token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          question: userMessage.content,
          document_id: documentId
        })
      });

      if (!response.ok) {
        throw new Error('Failed to get response');
      }

      const data = await response.json();

      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: data.answer,
        isUser: false,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      toast.error('Failed to get AI response');
      console.error('Chat error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <Paper 
      elevation={3} 
      sx={{ 
        backgroundColor: 'var(--bg-secondary)', 
        border: '1px solid var(--border-primary)',
        borderRadius: 'var(--radius-xl)',
        overflow: 'hidden',
        boxShadow: 'var(--shadow-xl)',
        height: '600px',
        display: 'flex',
        flexDirection: 'column'
      }}
    >
      {/* Header */}
      <Box sx={{ 
        p: 3, 
        borderBottom: '1px solid var(--border-primary)', 
        backgroundColor: 'var(--bg-tertiary)' 
      }}>
        <Typography 
          variant="h6"
          sx={{
            color: 'var(--text-primary)',
            fontWeight: 600,
            fontSize: 'var(--font-size-lg)',
            display: 'flex',
            alignItems: 'center',
            gap: 1
          }}
        >
          💬 Chat with PDF
          {documentTitle && (
            <Typography 
              component="span" 
              sx={{ 
                color: 'var(--text-secondary)', 
                fontSize: 'var(--font-size-sm)',
                fontWeight: 400,
                ml: 1
              }}
            >
              • {documentTitle}
            </Typography>
          )}
        </Typography>
      </Box>

      {/* Messages Area */}
      <Box sx={{ 
        flex: 1, 
        overflowY: 'auto', 
        p: 2,
        display: 'flex',
        flexDirection: 'column',
        gap: 2
      }}>
        {messages.map((message) => (
          <Box
            key={message.id}
            sx={{
              display: 'flex',
              flexDirection: message.isUser ? 'row-reverse' : 'row',
              alignItems: 'flex-start',
              gap: 2
            }}
          >
            <Avatar
              sx={{
                bgcolor: message.isUser ? 'var(--primary-600)' : 'var(--success)',
                width: 32,
                height: 32
              }}
            >
              {message.isUser ? <PersonIcon fontSize="small" /> : <SmartToyIcon fontSize="small" />}
            </Avatar>
            
            <Paper
              elevation={0}
              sx={{
                p: 2,
                maxWidth: '70%',
                backgroundColor: message.isUser ? 'var(--primary-600)' : 'var(--bg-tertiary)',
                color: message.isUser ? 'white' : 'var(--text-primary)',
                borderRadius: 'var(--radius-lg)',
                border: `1px solid ${message.isUser ? 'var(--primary-700)' : 'var(--border-primary)'}`,
                wordBreak: 'break-word'
              }}
            >
              <Typography 
                variant="body1" 
                sx={{ 
                  fontSize: 'var(--font-size-sm)',
                  lineHeight: 'var(--leading-relaxed)',
                  whiteSpace: 'pre-wrap'
                }}
              >
                {message.content}
              </Typography>
              <Typography 
                variant="caption" 
                sx={{ 
                  display: 'block',
                  mt: 1,
                  opacity: 0.7,
                  fontSize: 'var(--font-size-xs)'
                }}
              >
                {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </Typography>
            </Paper>
          </Box>
        ))}
        
        {isLoading && (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Avatar sx={{ bgcolor: 'var(--success)', width: 32, height: 32 }}>
              <SmartToyIcon fontSize="small" />
            </Avatar>
            <Paper
              elevation={0}
              sx={{
                p: 2,
                backgroundColor: 'var(--bg-tertiary)',
                borderRadius: 'var(--radius-lg)',
                border: '1px solid var(--border-primary)',
                display: 'flex',
                alignItems: 'center',
                gap: 1
              }}
            >
              <CircularProgress size={16} sx={{ color: 'var(--primary-500)' }} />
              <Typography sx={{ color: 'var(--text-secondary)', fontSize: 'var(--font-size-sm)' }}>
                Thinking...
              </Typography>
            </Paper>
          </Box>
        )}
        
        <div ref={messagesEndRef} />
      </Box>

      <Divider sx={{ borderColor: 'var(--border-primary)' }} />

      {/* Input Area */}
      <Box sx={{ 
        p: 3, 
        backgroundColor: 'var(--bg-tertiary)',
        display: 'flex',
        gap: 2,
        alignItems: 'flex-end'
      }}>
        <TextField
          fullWidth
          multiline
          maxRows={3}
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Ask a question about the document..."
          disabled={isLoading}
          sx={{
            '& .MuiOutlinedInput-root': {
              backgroundColor: 'var(--bg-secondary)',
              borderRadius: 'var(--radius-lg)',
              '& fieldset': {
                borderColor: 'var(--border-primary)',
              },
              '&:hover fieldset': {
                borderColor: 'var(--border-secondary)',
              },
              '&.Mui-focused fieldset': {
                borderColor: 'var(--primary-500)',
              },
            },
            '& .MuiInputBase-input': {
              color: 'var(--text-primary)',
              fontSize: 'var(--font-size-sm)',
              '&::placeholder': {
                color: 'var(--text-muted)',
                opacity: 1,
              },
            },
          }}
        />
        <Button
          variant="contained"
          onClick={handleSendMessage}
          disabled={!inputValue.trim() || isLoading}
          sx={{
            backgroundColor: 'var(--primary-600)',
            color: 'white',
            fontWeight: 500,
            borderRadius: 'var(--radius-lg)',
            minWidth: '60px',
            height: '56px',
            '&:hover': {
              backgroundColor: 'var(--primary-700)',
            },
            '&:disabled': {
              backgroundColor: 'var(--bg-quaternary)',
              color: 'var(--text-muted)'
            }
          }}
        >
          {isLoading ? (
            <CircularProgress size={20} color="inherit" />
          ) : (
            <SendIcon />
          )}
        </Button>
      </Box>
    </Paper>
  );
};

export default PDFChat; 