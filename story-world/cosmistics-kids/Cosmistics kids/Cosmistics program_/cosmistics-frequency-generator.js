/**
 * COSMISTICS Frequency Generator Tool
 * 
 * This code implements a web-based frequency generator for the COSMISTICS program
 * that can produce precise frequencies for energy work and consciousness development.
 * 
 * Core features:
 * - Generate Solfeggio frequencies (396Hz, 417Hz, 528Hz, 639Hz, 741Hz, 852Hz, 963Hz)
 * - Create binaural beats for brainwave entrainment
 * - Guided meditation integration
 * - Visual frequency representation
 * - Session timing with gentle transitions
 * - Save custom frequency combinations
 * 
 * This is the frontend implementation using React and Web Audio API
 */

import React, { useState, useEffect, useRef } from 'react';
import './FrequencyGenerator.css';

// Constants for Solfeggio frequencies
const SOLFEGGIO_FREQUENCIES = {
  LIBERATION: 396, // Liberating guilt and fear
  TRANSFORMATION: 417, // Facilitating change
  MIRACLE: 528, // Transformation and miracles (DNA repair)
  RELATIONSHIPS: 639, // Connecting/relationships
  EXPRESSION: 741, // Expression/solutions
  INTUITION: 852, // Returning to spiritual order
  AWAKENING: 963, // Awakening and cosmic consciousness
};

// Constants for brainwave frequencies
const BRAINWAVE_STATES = {
  DELTA: 2, // Deep sleep (0.5-4 Hz)
  THETA: 6, // Meditation, intuition (4-8 Hz)
  ALPHA: 10, // Relaxation, calm (8-13 Hz)
  BETA: 15, // Active thinking, focus (13-30 Hz)
  GAMMA: 40, // Higher consciousness, insight (30-100 Hz)
};

/**
 * Main Frequency Generator Component
 */
const FrequencyGenerator = ({ user, userLevel, onSessionComplete }) => {
  // State management
  const [primaryFrequency, setPrimaryFrequency] = useState(SOLFEGGIO_FREQUENCIES.LIBERATION);
  const [secondaryFrequency, setSecondaryFrequency] = useState(null);
  const [binauralBeat, setBinauralBeat] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [volume, setVolume] = useState(0.5);
  const [sessionDuration, setSessionDuration] = useState(10); // minutes
  const [timeRemaining, setTimeRemaining] = useState(0);
  const [visualizationType, setVisualizationType] = useState('wave'); // 'wave', 'circle', 'mandala'
  const [savedPresets, setSavedPresets] = useState([]);
  const [showAdvancedOptions, setShowAdvancedOptions] = useState(false);
  
  // References to audio nodes
  const audioContextRef = useRef(null);
  const oscillatorRef = useRef(null);
  const oscillator2Ref = useRef(null);
  const gainNodeRef = useRef(null);
  const analyserRef = useRef(null);
  const timerRef = useRef(null);
  const canvasRef = useRef(null);
  
  // Initialize audio context
  useEffect(() => {
    // Create audio context
    const AudioContext = window.AudioContext || window.webkitAudioContext;
    audioContextRef.current = new AudioContext();
    
    // Create analyzer for visualizations
    analyserRef.current = audioContextRef.current.createAnalyser();
    analyserRef.current.fftSize = 2048;
    
    // Clean up on unmount
    return () => {
      if (oscillatorRef.current) {
        oscillatorRef.current.stop();
        oscillatorRef.current.disconnect();
      }
      if (oscillator2Ref.current) {
        oscillator2Ref.current.stop();
        oscillator2Ref.current.disconnect();
      }
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
      if (audioContextRef.current.state !== 'closed') {
        audioContextRef.current.close();
      }
    };
  }, []);
  
  // Load user presets
  useEffect(() => {
    if (user && user.id) {
      // In a real app, this would be an API call to load user presets
      // For this example, we'll use mock data
      const mockUserPresets = [
        { 
          id: 1, 
          name: 'Morning Activation', 
          primary: SOLFEGGIO_FREQUENCIES.LIBERATION, 
          secondary: SOLFEGGIO_FREQUENCIES.MIRACLE,
          binaural: BRAINWAVE_STATES.ALPHA,
          duration: 15
        },
        { 
          id: 2, 
          name: 'Deep Meditation', 
          primary: SOLFEGGIO_FREQUENCIES.INTUITION, 
          secondary: null,
          binaural: BRAINWAVE_STATES.THETA,
          duration: 20
        }
      ];
      
      setSavedPresets(mockUserPresets);
    }
  }, [user]);
  
  // Effect for visualization rendering
  useEffect(() => {
    if (isPlaying && canvasRef.current && analyserRef.current) {
      renderVisualization();
    }
  }, [isPlaying, visualizationType]);
  
  /**
   * Starts the frequency generator with current settings
   */
  const startGenerator = () => {
    // If audio context is suspended (browser policy), resume it
    if (audioContextRef.current.state === 'suspended') {
      audioContextRef.current.resume();
    }
    
    // Stop any existing oscillators
    if (oscillatorRef.current) {
      oscillatorRef.current.stop();
      oscillatorRef.current.disconnect();
    }
    if (oscillator2Ref.current) {
      oscillator2Ref.current.stop();
      oscillator2Ref.current.disconnect();
    }
    
    // Create gain node for volume control
    gainNodeRef.current = audioContextRef.current.createGain();
    gainNodeRef.current.gain.value = volume;
    gainNodeRef.current.connect(analyserRef.current);
    analyserRef.current.connect(audioContextRef.current.destination);
    
    // Create primary oscillator
    oscillatorRef.current = audioContextRef.current.createOscillator();
    oscillatorRef.current.type = 'sine';
    oscillatorRef.current.frequency.setValueAtTime(primaryFrequency, audioContextRef.current.currentTime);
    oscillatorRef.current.connect(gainNodeRef.current);
    oscillatorRef.current.start();
    
    // Create secondary oscillator if needed
    if (secondaryFrequency) {
      oscillator2Ref.current = audioContextRef.current.createOscillator();
      oscillator2Ref.current.type = 'sine';
      oscillator2Ref.current.frequency.setValueAtTime(secondaryFrequency, audioContextRef.current.currentTime);
      oscillator2Ref.current.connect(gainNodeRef.current);
      oscillator2Ref.current.start();
    }
    
    // Set up binaural beat if selected
    if (binauralBeat && !secondaryFrequency) {
      // For binaural beats, we need two oscillators with slightly different frequencies
      // The difference between frequencies creates the beat frequency perceived by the brain
      // For example, if left ear hears 200Hz and right ear hears 210Hz, a 10Hz beat is perceived
      
      // We can't create true binaural beats without stereo panning, so this is a simplified version
      const leftFreq = primaryFrequency;
      const rightFreq = primaryFrequency + binauralBeat;
      
      // Create stereo panner for left ear
      const pannerLeft = audioContextRef.current.createStereoPanner();
      pannerLeft.pan.value = -1; // Full left
      
      // Create stereo panner for right ear
      const pannerRight = audioContextRef.current.createStereoPanner();
      pannerRight.pan.value = 1; // Full right
      
      // Set up left oscillator
      oscillatorRef.current.disconnect();
      oscillatorRef.current.connect(pannerLeft);
      pannerLeft.connect(gainNodeRef.current);
      
      // Set up right oscillator
      oscillator2Ref.current = audioContextRef.current.createOscillator();
      oscillator2Ref.current.type = 'sine';
      oscillator2Ref.current.frequency.setValueAtTime(rightFreq, audioContextRef.current.currentTime);
      oscillator2Ref.current.connect(pannerRight);
      pannerRight.connect(gainNodeRef.current);
      oscillator2Ref.current.start();
    }
    
    // Set up session timer
    const durationMs = sessionDuration * 60 * 1000;
    setTimeRemaining(durationMs);
    
    // Clear any existing timer
    if (timerRef.current) {
      clearInterval(timerRef.current);
    }
    
    // Create new timer that updates every second
    const startTime = Date.now();
    timerRef.current = setInterval(() => {
      const elapsed = Date.now() - startTime;
      const remaining = durationMs - elapsed;
      
      if (remaining <= 0) {
        // Session complete
        stopGenerator();
        if (onSessionComplete) {
          onSessionComplete({
            duration: sessionDuration,
            primaryFrequency,
            secondaryFrequency,
            binauralBeat
          });
        }
      } else {
        setTimeRemaining(remaining);
        
        // Fade out volume in the last 10 seconds
        if (remaining < 10000) {
          const newVolume = (remaining / 10000) * volume;
          gainNodeRef.current.gain.value = Math.max(0.001, newVolume);
        }
      }
    }, 1000);
    
    setIsPlaying(true);
  };
  
  /**
   * Stops the frequency generator
   */
  const stopGenerator = () => {
    // Stop oscillators with a slight fade out to avoid clicks
    if (gainNodeRef.current) {
      // Exponential ramp would be better but can't go to 0
      gainNodeRef.current.gain.linearRampToValueAtTime(
        0.001, 
        audioContextRef.current.currentTime + 0.5
      );
    }
    
    setTimeout(() => {
      if (oscillatorRef.current) {
        oscillatorRef.current.stop();
        oscillatorRef.current.disconnect();
        oscillatorRef.current = null;
      }
      
      if (oscillator2Ref.current) {
        oscillator2Ref.current.stop();
        oscillator2Ref.current.disconnect();
        oscillator2Ref.current = null;
      }
    }, 500);
    
    // Clear timer
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
    
    setIsPlaying(false);
  };
  
  /**
   * Saves current settings as a user preset
   */
  const savePreset = (presetName) => {
    const newPreset = {
      id: Date.now(), // simple ID generation for example
      name: presetName,
      primary: primaryFrequency,
      secondary: secondaryFrequency,
      binaural: binauralBeat,
      duration: sessionDuration
    };
    
    setSavedPresets([...savedPresets, newPreset]);
    
    // In a real app, save to backend
    // saveUserPreset(user.id, newPreset);
  };
  
  /**
   * Loads a preset
   */
  const loadPreset = (preset) => {
    if (isPlaying) {
      stopGenerator();
    }
    
    setPrimaryFrequency(preset.primary);
    setSecondaryFrequency(preset.secondary);
    setBinauralBeat(preset.binaural);
    setSessionDuration(preset.duration);
  };
  
  /**
   * Renders visualization based on current audio data
   */
  const renderVisualization = () => {
    if (!canvasRef.current || !analyserRef.current) return;
    
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;
    
    // Get frequency data
    const bufferLength = analyserRef.current.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);
    
    function draw() {
      if (!isPlaying) return;
      
      requestAnimationFrame(draw);
      
      analyserRef.current.getByteTimeDomainData(dataArray);
      
      // Clear canvas
      ctx.fillStyle = 'rgb(20, 20, 40)';
      ctx.fillRect(0, 0, width, height);
      
      if (visualizationType === 'wave') {
        // Draw waveform
        ctx.lineWidth = 2;
        ctx.strokeStyle = 'rgb(100, 200, 255)';
        ctx.beginPath();
        
        const sliceWidth = width / bufferLength;
        let x = 0;
        
        for (let i = 0; i < bufferLength; i++) {
          const v = dataArray[i] / 128.0;
          const y = v * height / 2;
          
          if (i === 0) {
            ctx.moveTo(x, y);
          } else {
            ctx.lineTo(x, y);
          }
          
          x += sliceWidth;
        }
        
        ctx.lineTo(width, height / 2);
        ctx.stroke();
      } else if (visualizationType === 'circle') {
        // Draw circular visualization
        const centerX = width / 2;
        const centerY = height / 2;
        const radius = Math.min(width, height) / 3;
        
        ctx.beginPath();
        ctx.arc(centerX, centerY, radius, 0, 2 * Math.PI);
        ctx.strokeStyle = 'rgba(100, 200, 255, 0.5)';
        ctx.lineWidth = 2;
        ctx.stroke();
        
        // Draw data points around circle
        for (let i = 0; i < bufferLength; i += 8) {
          const v = dataArray[i] / 128.0;
          const angle = (i / bufferLength) * 2 * Math.PI;
          
          const x = centerX + Math.cos(angle) * radius * v;
          const y = centerY + Math.sin(angle) * radius * v;
          
          ctx.beginPath();
          ctx.arc(x, y, 2, 0, 2 * Math.PI);
          ctx.fillStyle = `hsl(${i / bufferLength * 360}, 100%, 50%)`;
          ctx.fill();
        }
      } else if (visualizationType === 'mandala') {
        // Draw mandala-style visualization
        const centerX = width / 2;
        const centerY = height / 2;
        
        // Calculate average amplitude for sizing
        let sum = 0;
        for (let i = 0; i < bufferLength; i++) {
          sum += Math.abs(dataArray[i] - 128) / 128.0;
        }
        const avgAmpl