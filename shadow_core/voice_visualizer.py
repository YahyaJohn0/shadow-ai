# shadow_gui/voice_visualizer.py
"""
Advanced voice visualization component with real-time audio processing
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pyaudio
import threading
import queue
import customtkinter as ctk

class VoiceVisualizer:
    """
    Real-time voice visualization with audio processing
    """
    
    def __init__(self, parent, width=800, height=200):
        self.parent = parent
        self.width = width
        self.height = height
        
        # Audio processing
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 44100
        
        self.audio_data = np.zeros(self.CHUNK)
        self.is_recording = False
        self.audio_queue = queue.Queue()
        
        # Setup visualization
        self.setup_visualization()
        
    def setup_visualization(self):
        """Setup the visualization canvas"""
        # Create figure
        self.fig, self.ax = plt.subplots(figsize=(self.width/100, self.height/100), facecolor='#1E1E1E')
        self.ax.set_facecolor('#1E1E1E')
        
        # Initialize plot
        x = np.arange(self.CHUNK)
        self.line, = self.ax.plot(x, self.audio_data, color='#00FFAA', linewidth=1.5, alpha=0.8)
        
        # Configure plot appearance
        self.ax.set_ylim(-32768, 32768)
        self.ax.set_xlim(0, self.CHUNK)
        self.ax.axis('off')
        
        # Remove margins
        self.fig.tight_layout(pad=0)
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.fig, self.parent)
        self.canvas.draw()
        
    def get_canvas(self):
        """Get the visualization canvas"""
        return self.canvas.get_tk_widget()
        
    def start_visualization(self):
        """Start voice visualization"""
        self.is_recording = True
        
        # Start audio recording thread
        self.audio_thread = threading.Thread(target=self.record_audio, daemon=True)
        self.audio_thread.start()
        
        # Start animation
        self.animation = FuncAnimation(
            self.fig, self.update_plot, interval=50, blit=False, cache_frame_data=False
        )
        
    def stop_visualization(self):
        """Stop voice visualization"""
        self.is_recording = False
        if hasattr(self, 'animation'):
            self.animation.event_source.stop()
            
    def record_audio(self):
        """Record audio data for visualization"""
        p = pyaudio.PyAudio()
        
        stream = p.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            frames_per_buffer=self.CHUNK
        )
        
        while self.is_recording:
            try:
                data = stream.read(self.CHUNK, exception_on_overflow=False)
                audio_array = np.frombuffer(data, dtype=np.int16)
                self.audio_queue.put(audio_array)
            except Exception as e:
                print(f"Audio recording error: {e}")
                break
                
        stream.stop_stream()
        stream.close()
        p.terminate()
        
    def update_plot(self, frame):
        """Update the visualization plot"""
        try:
            if not self.audio_queue.empty():
                self.audio_data = self.audio_queue.get()
                
            # Update plot data
            self.line.set_ydata(self.audio_data)
            
            # Dynamic y-axis scaling based on audio levels
            max_val = np.max(np.abs(self.audio_data)) if len(self.audio_data) > 0 else 32768
            self.ax.set_ylim(-max_val * 1.1, max_val * 1.1)
            
        except Exception as e:
            print(f"Plot update error: {e}")
            
        return self.line,
        
    def set_visualization_style(self, style='default'):
        """Set visualization style"""
        styles = {
            'default': {'color': '#00FFAA', 'linewidth': 1.5, 'alpha': 0.8},
            'energy': {'color': '#FF6B6B', 'linewidth': 2.0, 'alpha': 0.9},
            'calm': {'color': '#4ECDC4', 'linewidth': 1.2, 'alpha': 0.7},
            'neon': {'color': '#FF00FF', 'linewidth': 1.8, 'alpha': 0.85}
        }
        
        if style in styles:
            config = styles[style]
            self.line.set_color(config['color'])
            self.line.set_linewidth(config['linewidth'])
            self.line.set_alpha(config['alpha'])
            self.canvas.draw_idle()