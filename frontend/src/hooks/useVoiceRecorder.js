import { useState, useCallback, useRef, useEffect } from 'react';
import { useVAD } from './useVAD';

export const useVoiceRecorder = (onTranscription) => {
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const mediaRecorderRef = useRef(null);
  const audioContextRef = useRef(null);
  const audioWorkletNodeRef = useRef(null);
  const streamRef = useRef(null);
  const chunksRef = useRef([]);
  const wsRef = useRef(null);
  const { isSpeaking, startVAD, stopVAD } = useVAD();

  const cleanup = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.close();
    }
    wsRef.current = null;

    if (mediaRecorderRef.current?.state === 'recording') {
      mediaRecorderRef.current.stop();
    }
    mediaRecorderRef.current = null;

    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }

    if (audioContextRef.current) {
      audioContextRef.current.close();
      audioContextRef.current = null;
    }

    chunksRef.current = [];
    setIsRecording(false);
    setIsProcessing(false);
    stopVAD();
  }, [stopVAD]);

  const initializeAudioContext = useCallback(async () => {
    try {
      // Request microphone access
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;

      // Create audio context
      const audioContext = new (window.AudioContext || window.webkitAudioContext)();
      audioContextRef.current = audioContext;

      // Create audio source from stream
      const source = audioContext.createMediaStreamSource(stream);
      
      // Create script processor for audio processing
      const processor = audioContext.createScriptProcessor(4096, 1, 1);
      
      processor.onaudioprocess = (e) => {
        if (isRecording && mediaRecorderRef.current?.state === 'recording') {
          const inputData = e.inputBuffer.getChannelData(0);
          // Convert Float32Array to Int16Array for WebSocket
          const pcmData = new Int16Array(inputData.length);
          for (let i = 0; i < inputData.length; i++) {
            pcmData[i] = inputData[i] * 0x7FFF;
          }
          if (wsRef.current?.readyState === WebSocket.OPEN) {
            wsRef.current.send(pcmData.buffer);
          }
        }
      };

      // Connect the nodes
      source.connect(processor);
      processor.connect(audioContext.destination);

      return true;
    } catch (error) {
      console.error('Error initializing audio context:', error);
      return false;
    }
  }, [isRecording]);

  const startRecording = useCallback(async () => {
    try {
      cleanup(); // Clean up any existing connections

      if (!audioContextRef.current) {
        const initialized = await initializeAudioContext();
        if (!initialized) {
          throw new Error('Failed to initialize audio context');
        }
      }

      // Create WebSocket connection
      wsRef.current = new WebSocket('ws://localhost:8000/ws/voice');
      
      wsRef.current.onmessage = (event) => {
        try {
          const response = JSON.parse(event.data);
          console.log('Received WebSocket message:', response); // Debug log
          
          if (response.type === 'transcription' && response.text) {
            console.log('Processing transcription:', response.text); // Debug log
            onTranscription(response.text);
          }
        } catch (error) {
          console.error('Error processing WebSocket message:', error);
        }
      };

      wsRef.current.onerror = (error) => {
        console.error('WebSocket error:', error);
        cleanup();
      };

      wsRef.current.onclose = () => {
        console.log('WebSocket connection closed');
        cleanup();
      };

      // Wait for WebSocket to be ready
      await new Promise((resolve, reject) => {
        if (wsRef.current.readyState === WebSocket.OPEN) {
          resolve();
        } else {
          wsRef.current.onopen = () => {
            console.log('WebSocket connection opened'); // Debug log
            resolve();
          };
          wsRef.current.onerror = reject;
        }
      });

      // Start VAD
      startVAD();
      
      // Start recording
      setIsRecording(true);
      chunksRef.current = [];
      
      const mediaRecorder = new MediaRecorder(streamRef.current);
      mediaRecorderRef.current = mediaRecorder;
      
      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunksRef.current.push(e.data);
        }
      };
      
      mediaRecorder.start(100); // Collect data every 100ms
      
    } catch (error) {
      console.error('Error starting recording:', error);
      cleanup();
      throw error;
    }
  }, [cleanup, initializeAudioContext, onTranscription, startVAD]);

  const stopRecording = useCallback(async () => {
    cleanup();
  }, [cleanup]);

  useEffect(() => {
    return () => {
      cleanup();
    };
  }, [cleanup]);

  return {
    isRecording,
    isProcessing,
    startRecording,
    stopRecording,
    isSpeaking
  };
}; 