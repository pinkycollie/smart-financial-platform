"""
Video.js Integration for DEAF FIRST Platform
Enhanced video streaming with accessibility features for ASL content
"""

import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class VideoJSIntegration:
    """Video.js integration with deaf-specific accessibility features"""
    
    def __init__(self):
        self.default_config = {
            'fluid': True,
            'responsive': True,
            'playbackRates': [0.5, 0.75, 1, 1.25, 1.5, 2],
            'controls': True,
            'preload': 'metadata',
            'language': 'en',
            'languages': {
                'en': {
                    'Play': 'Play ASL Video',
                    'Pause': 'Pause ASL Video',
                    'Fullscreen': 'Full Screen ASL View',
                    'Mute': 'Mute Audio Description'
                }
            }
        }
        
        # Deaf-specific accessibility features
        self.accessibility_features = {
            'captions': True,
            'audio_descriptions': True,
            'sign_language_interpretation': True,
            'keyboard_navigation': True,
            'high_contrast_mode': True,
            'custom_playback_speeds': [0.25, 0.5, 0.75, 1, 1.25, 1.5, 2, 3],
            'visual_indicators': True,
            'transcript_overlay': True
        }
    
    def generate_video_config(self, video_data: Dict[str, Any], user_preferences: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate Video.js configuration for ASL content"""
        
        if user_preferences is None:
            user_preferences = {}
        
        config = self.default_config.copy()
        
        # Configure sources
        sources = []
        if 'hls_url' in video_data:
            sources.append({
                'src': video_data['hls_url'],
                'type': 'application/x-mpegURL',
                'label': 'Auto'
            })
        
        if 'mp4_url' in video_data:
            sources.append({
                'src': video_data['mp4_url'],
                'type': 'video/mp4',
                'label': 'MP4'
            })
        
        config['sources'] = sources
        
        # Add poster image
        if 'thumbnail_url' in video_data:
            config['poster'] = video_data['thumbnail_url']
        
        # Configure captions/subtitles
        tracks = []
        if video_data.get('captions'):
            for caption in video_data['captions']:
                tracks.append({
                    'kind': 'captions',
                    'src': caption['url'],
                    'srclang': caption.get('language', 'en'),
                    'label': caption.get('label', 'English Captions'),
                    'default': caption.get('default', False)
                })
        
        # Add ASL interpretation track if available
        if video_data.get('asl_interpretation'):
            tracks.append({
                'kind': 'descriptions',
                'src': video_data['asl_interpretation']['url'],
                'srclang': 'asl',
                'label': 'ASL Interpretation',
                'default': True
            })
        
        config['tracks'] = tracks
        
        # Apply user preferences
        if user_preferences.get('preferred_speed'):
            config['playbackRates'] = [user_preferences['preferred_speed']]
        
        if user_preferences.get('auto_captions', True):
            config['textTracks'] = {'captions': {'default': True}}
        
        # Add deaf-specific plugins
        config['plugins'] = self._get_accessibility_plugins(user_preferences)
        
        return config
    
    def _get_accessibility_plugins(self, user_preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Configure accessibility plugins for deaf users"""
        plugins = {}
        
        # Visual indicators plugin
        plugins['visualIndicators'] = {
            'enabled': user_preferences.get('visual_alerts', True),
            'playPauseIndicator': True,
            'bufferingIndicator': True,
            'volumeIndicator': False  # Not needed for deaf users
        }
        
        # Enhanced keyboard navigation
        plugins['keyboardNavigation'] = {
            'enabled': True,
            'customKeys': {
                'Space': 'togglePlayPause',
                'ArrowLeft': 'seekBackward',
                'ArrowRight': 'seekForward',
                'ArrowUp': 'increaseSpeed',
                'ArrowDown': 'decreaseSpeed',
                'C': 'toggleCaptions',
                'F': 'toggleFullscreen',
                'T': 'toggleTranscript'
            }
        }
        
        # High contrast mode
        if user_preferences.get('high_contrast', False):
            plugins['highContrast'] = {
                'enabled': True,
                'theme': 'dark'
            }
        
        # Transcript overlay
        plugins['transcript'] = {
            'enabled': user_preferences.get('show_transcript', True),
            'position': 'bottom',
            'searchable': True,
            'downloadable': True
        }
        
        # ASL-specific features
        plugins['aslSupport'] = {
            'enabled': True,
            'signerWindow': {
                'resizable': True,
                'moveable': True,
                'defaultSize': '25%'
            },
            'signLanguageControls': True
        }
        
        return plugins
    
    def generate_html_player(self, video_id: str, config: Dict[str, Any], container_class: str = "") -> str:
        """Generate HTML for Video.js player with accessibility features"""
        
        config_json = json.dumps(config, indent=2)
        
        html = f"""
        <div class="video-container {container_class}">
            <video
                id="{video_id}"
                class="video-js vjs-default-skin vjs-deaf-first-theme"
                controls
                preload="auto"
                data-setup='{config_json}'
                aria-label="ASL Video Player">
                
                <!-- Fallback message for unsupported browsers -->
                <p class="vjs-no-js">
                    To view this ASL video, please enable JavaScript or update your browser.
                    <a href="https://videojs.com/html5-video-support/" target="_blank">
                        Learn more about video support
                    </a>
                </p>
            </video>
            
            <!-- ASL Controls Panel -->
            <div class="asl-controls-panel" aria-label="ASL Video Controls">
                <button class="btn-asl-speed" aria-label="Adjust ASL playback speed">
                    <i class="fas fa-tachometer-alt"></i> Speed
                </button>
                <button class="btn-asl-captions" aria-label="Toggle captions">
                    <i class="fas fa-closed-captioning"></i> Captions
                </button>
                <button class="btn-asl-transcript" aria-label="Show transcript">
                    <i class="fas fa-file-text"></i> Transcript
                </button>
                <button class="btn-asl-fullscreen" aria-label="Enter fullscreen">
                    <i class="fas fa-expand"></i> Full Screen
                </button>
            </div>
            
            <!-- Visual Indicators for Deaf Users -->
            <div class="visual-indicators" aria-live="polite">
                <div class="play-indicator" role="status" aria-label="Video playing"></div>
                <div class="pause-indicator" role="status" aria-label="Video paused"></div>
                <div class="buffer-indicator" role="status" aria-label="Video buffering"></div>
            </div>
        </div>
        """
        
        return html
    
    def generate_css_styles(self) -> str:
        """Generate CSS styles for deaf-first video player theme"""
        return """
        /* DEAF FIRST Video.js Theme */
        .vjs-deaf-first-theme {
            font-family: 'Inter', sans-serif;
        }
        
        .vjs-deaf-first-theme .vjs-control-bar {
            background: rgba(0, 0, 0, 0.9);
            height: 60px;
            border-top: 3px solid var(--bs-primary);
        }
        
        .vjs-deaf-first-theme .vjs-big-play-button {
            width: 80px;
            height: 80px;
            border-radius: 50%;
            background: var(--bs-primary);
            border: 4px solid white;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        }
        
        .vjs-deaf-first-theme .vjs-big-play-button:hover {
            background: var(--bs-primary);
            transform: scale(1.1);
            transition: all 0.3s ease;
        }
        
        /* Visual Indicators */
        .visual-indicators {
            position: absolute;
            top: 20px;
            right: 20px;
            z-index: 1000;
        }
        
        .play-indicator, .pause-indicator, .buffer-indicator {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: none;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 18px;
            margin-bottom: 10px;
            animation: pulse 1.5s infinite;
        }
        
        .play-indicator {
            background: var(--bs-success);
        }
        
        .pause-indicator {
            background: var(--bs-warning);
        }
        
        .buffer-indicator {
            background: var(--bs-info);
        }
        
        .play-indicator.active,
        .pause-indicator.active,
        .buffer-indicator.active {
            display: flex;
        }
        
        /* ASL Controls Panel */
        .asl-controls-panel {
            display: flex;
            gap: 10px;
            margin-top: 15px;
            padding: 15px;
            background: var(--bs-dark);
            border-radius: 8px;
            border: 1px solid var(--bs-border-color);
        }
        
        .asl-controls-panel button {
            background: var(--bs-secondary);
            border: none;
            padding: 10px 15px;
            border-radius: 6px;
            color: white;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .asl-controls-panel button:hover {
            background: var(--bs-primary);
            transform: translateY(-2px);
        }
        
        .asl-controls-panel button:focus {
            outline: 3px solid var(--bs-info);
            outline-offset: 2px;
        }
        
        /* High Contrast Mode */
        .vjs-deaf-first-theme.high-contrast {
            filter: contrast(150%) brightness(120%);
        }
        
        .vjs-deaf-first-theme.high-contrast .vjs-control-bar {
            background: black;
            border-top: 5px solid yellow;
        }
        
        .vjs-deaf-first-theme.high-contrast .vjs-big-play-button {
            background: yellow;
            color: black;
            border-color: black;
        }
        
        /* Transcript Overlay */
        .vjs-transcript-overlay {
            position: absolute;
            bottom: 80px;
            left: 20px;
            right: 20px;
            background: rgba(0, 0, 0, 0.9);
            color: white;
            padding: 20px;
            border-radius: 8px;
            max-height: 200px;
            overflow-y: auto;
            font-size: 16px;
            line-height: 1.5;
        }
        
        .vjs-transcript-overlay.hidden {
            display: none;
        }
        
        /* Responsive Design */
        @media (max-width: 768px) {
            .asl-controls-panel {
                flex-wrap: wrap;
            }
            
            .vjs-deaf-first-theme .vjs-control-bar {
                height: 50px;
            }
            
            .visual-indicators {
                top: 10px;
                right: 10px;
            }
        }
        
        /* Keyboard Focus Indicators */
        .vjs-deaf-first-theme .vjs-control:focus {
            outline: 3px solid var(--bs-info);
            outline-offset: 2px;
        }
        
        /* Animation Keyframes */
        @keyframes pulse {
            0% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.7; transform: scale(1.1); }
            100% { opacity: 1; transform: scale(1); }
        }
        """
    
    def generate_javascript_integration(self, video_id: str) -> str:
        """Generate JavaScript for Video.js integration with accessibility features"""
        return f"""
        // Initialize Video.js with DEAF FIRST accessibility features
        document.addEventListener('DOMContentLoaded', function() {{
            const player = videojs('{video_id}', {{
                // Additional initialization options
                experimentalSvgIcons: true,
                enableSourceBuffering: true,
                
                // Accessibility enhancements
                textTrackDisplay: true,
                textTrackSettings: true,
                
                // Performance optimizations
                techOrder: ['html5'],
                html5: {{
                    vhs: {{
                        overrideNative: true,
                        enableLowInitialPlaylist: true
                    }}
                }}
            }});
            
            // Add deaf-specific event handlers
            player.ready(function() {{
                console.log('ASL Video Player ready');
                
                // Visual indicators for play/pause
                player.on('play', function() {{
                    showVisualIndicator('play');
                    announceToScreenReader('Video playing');
                }});
                
                player.on('pause', function() {{
                    showVisualIndicator('pause');
                    announceToScreenReader('Video paused');
                }});
                
                player.on('waiting', function() {{
                    showVisualIndicator('buffer');
                    announceToScreenReader('Video buffering');
                }});
                
                player.on('canplay', function() {{
                    hideVisualIndicators();
                }});
                
                // Enhanced keyboard controls
                player.on('keydown', function(event) {{
                    switch(event.which) {{
                        case 67: // 'C' key for captions
                            player.textTracks().tracks_.forEach(track => {{
                                if (track.kind === 'captions') {{
                                    track.mode = track.mode === 'showing' ? 'hidden' : 'showing';
                                }}
                            }});
                            break;
                        case 84: // 'T' key for transcript
                            toggleTranscript();
                            break;
                        case 38: // Up arrow - increase speed
                            increasePlaybackSpeed();
                            break;
                        case 40: // Down arrow - decrease speed
                            decreasePlaybackSpeed();
                            break;
                    }}
                }});
            }});
            
            // ASL-specific control functions
            function showVisualIndicator(type) {{
                const indicators = document.querySelectorAll('.visual-indicators > div');
                indicators.forEach(indicator => indicator.classList.remove('active'));
                
                const targetIndicator = document.querySelector(`.{type}-indicator`);
                if (targetIndicator) {{
                    targetIndicator.classList.add('active');
                    setTimeout(() => {{
                        targetIndicator.classList.remove('active');
                    }}, 2000);
                }}
            }}
            
            function hideVisualIndicators() {{
                const indicators = document.querySelectorAll('.visual-indicators > div');
                indicators.forEach(indicator => indicator.classList.remove('active'));
            }}
            
            function announceToScreenReader(message) {{
                const announcement = document.createElement('div');
                announcement.setAttribute('aria-live', 'polite');
                announcement.setAttribute('aria-atomic', 'true');
                announcement.className = 'sr-only';
                announcement.textContent = message;
                document.body.appendChild(announcement);
                
                setTimeout(() => {{
                    document.body.removeChild(announcement);
                }}, 1000);
            }}
            
            function toggleTranscript() {{
                const transcript = document.querySelector('.vjs-transcript-overlay');
                if (transcript) {{
                    transcript.classList.toggle('hidden');
                }}
            }}
            
            function increasePlaybackSpeed() {{
                const currentRate = player.playbackRate();
                const rates = player.options().playbackRates || [0.5, 0.75, 1, 1.25, 1.5, 2];
                const currentIndex = rates.indexOf(currentRate);
                if (currentIndex < rates.length - 1) {{
                    player.playbackRate(rates[currentIndex + 1]);
                    announceToScreenReader(`Speed increased to ${{rates[currentIndex + 1]}}x`);
                }}
            }}
            
            function decreasePlaybackSpeed() {{
                const currentRate = player.playbackRate();
                const rates = player.options().playbackRates || [0.5, 0.75, 1, 1.25, 1.5, 2];
                const currentIndex = rates.indexOf(currentRate);
                if (currentIndex > 0) {{
                    player.playbackRate(rates[currentIndex - 1]);
                    announceToScreenReader(`Speed decreased to ${{rates[currentIndex - 1]}}x`);
                }}
            }}
            
            // ASL Controls Panel Event Handlers
            document.querySelector('.btn-asl-speed').addEventListener('click', function() {{
                // Show speed selection modal or cycle through speeds
                const currentRate = player.playbackRate();
                increasePlaybackSpeed();
            }});
            
            document.querySelector('.btn-asl-captions').addEventListener('click', function() {{
                player.textTracks().tracks_.forEach(track => {{
                    if (track.kind === 'captions') {{
                        track.mode = track.mode === 'showing' ? 'hidden' : 'showing';
                    }}
                }});
            }});
            
            document.querySelector('.btn-asl-transcript').addEventListener('click', toggleTranscript);
            
            document.querySelector('.btn-asl-fullscreen').addEventListener('click', function() {{
                if (player.isFullscreen()) {{
                    player.exitFullscreen();
                }} else {{
                    player.requestFullscreen();
                }}
            }});
            
            // Save user preferences
            player.on('ratechange', function() {{
                localStorage.setItem('asl_preferred_speed', player.playbackRate());
            }});
            
            // Load user preferences
            const savedSpeed = localStorage.getItem('asl_preferred_speed');
            if (savedSpeed) {{
                player.ready(() => {{
                    player.playbackRate(parseFloat(savedSpeed));
                }});
            }}
        }});
        """
    
    def create_asl_video_component(self, video_data: Dict[str, Any], user_preferences: Dict[str, Any] = None) -> Dict[str, str]:
        """Create complete ASL video component with Video.js"""
        
        video_id = f"asl-video-{video_data.get('id', 'default')}"
        config = self.generate_video_config(video_data, user_preferences)
        
        return {
            'html': self.generate_html_player(video_id, config, "asl-video-component"),
            'css': self.generate_css_styles(),
            'javascript': self.generate_javascript_integration(video_id),
            'config': config
        }


# Global Video.js integration instance
video_js_integration = VideoJSIntegration()