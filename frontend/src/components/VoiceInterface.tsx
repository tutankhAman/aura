import React, { useState, useEffect, useRef } from 'react';
import { Box, Button, Typography, CircularProgress } from '@mui/material';
import MicIcon from '@mui/icons-material/Mic';
import MicOffIcon from '@mui/icons-material/MicOff';

interface VoiceInterfaceProps {
  onTranscript?: (text: string) => void;
}

const VoiceInterface: React.FC<VoiceInterfaceProps> = ({ onTranscript }) => {
  const [isRecording, setIsRecording] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [status, setStatus] = useState('Disconnected');
  
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const websocketRef = useRef<WebSocket | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const streamRef = useRef<MediaStream | null>(null);

  useEffect(() => {
    // Initialize WebSocket connection
    const ws = new WebSocket('ws://localhost:8000/ws/voice');
    
    ws.onopen = () => {
      setIsConnected(true);
      setStatus('Connected');
    };
    
    ws.onclose = () => {
      setIsConnected(false);
      setStatus('Disconnected');
    };
    
    ws.onmessage = (event) => {
      const response = JSON.parse(event.data);
      if (response.type === 'transcript' && onTranscript) {
        onTranscript(response.text);
      }
    };
    
    websocketRef.current = ws;
    
    return () => {
      ws.close();
      stopRecording();
    };
  }, [onTranscript]);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;
      
      // Create audio context and processor
      const audioContext = new AudioContext();
      audioContextRef.current = audioContext;
      
      const source = audioContext.createMediaStreamSource(stream);
      const processor = audioContext.createScriptProcessor(1024, 1, 1);
      
      processor.onaudioprocess = (e) => {
        if (isRecording && websocketRef.current?.readyState === WebSocket.OPEN) {
          const inputData = e.inputBuffer.getChannelData(0);
          // Convert Float32Array to Int16Array
          const pcmData = new Int16Array(inputData.length);
          for (let i = 0; i < inputData.length; i++) {
            pcmData[i] = inputData[i] * 0x7FFF;
          }
          
          // Send audio data through WebSocket
          websocketRef.current?.send(pcmData.buffer);
        }
      };
      
      source.connect(processor);
      processor.connect(audioContext.destination);
      
      setIsRecording(true);
      setStatus('Recording...');
      
    } catch (error) {
      console.error('Error accessing microphone:', error);
      setStatus('Error accessing microphone');
    }
  };

  const stopRecording = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
    
    if (audioContextRef.current) {
      audioContextRef.current.close();
      audioContextRef.current = null;
    }
    
    setIsRecording(false);
    setStatus('Connected');
  };

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        gap: 2,
        p: 2,
        border: '1px solid #ccc',
        borderRadius: 2,
        maxWidth: 400,
        mx: 'auto',
      }}
    >
      <Typography variant="h6" color="primary">
        Voice Interface
      </Typography>
      
      <Typography variant="body2" color={isConnected ? 'success.main' : 'error.main'}>
        Status: {status}
      </Typography>
      
      <Button
        variant="contained"
        color={isRecording ? 'error' : 'primary'}
        onClick={isRecording ? stopRecording : startRecording}
        disabled={!isConnected}
        startIcon={isRecording ? <MicOffIcon /> : <MicIcon />}
        sx={{ minWidth: 150 }}
      >
        {isRecording ? 'Stop Recording' : 'Start Recording'}
      </Button>
      
      {isRecording && (
        <CircularProgress size={24} sx={{ mt: 1 }} />
      )}
    </Box>
  );
};

export default VoiceInterface; 