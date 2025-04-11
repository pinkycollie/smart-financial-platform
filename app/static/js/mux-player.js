/**
 * Mux Player integration for April's ASL accessibility
 */

// Initialize Mux Player when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  initMuxPlayers();
});

/**
 * Initialize all Mux Players on the page
 */
function initMuxPlayers() {
  // Add Mux Player script if not already present
  if (!document.getElementById('mux-player-script')) {
    const script = document.createElement('script');
    script.id = 'mux-player-script';
    script.src = 'https://unpkg.com/@mux/mux-player';
    script.type = 'module';
    document.head.appendChild(script);
    
    // Add necessary CSS
    const style = document.createElement('link');
    style.rel = 'stylesheet';
    style.href = 'https://unpkg.com/@mux/mux-player/dist/mux-player.css';
    document.head.appendChild(style);
  }
  
  // When script loads, initialize players
  script.onload = () => {
    initializePlayerElements();
  };
  
  // If the script might already be loaded, try to initialize immediately
  if (customElements.get('mux-player')) {
    initializePlayerElements();
  }
}

/**
 * Initialize all player elements with customizations
 */
function initializePlayerElements() {
  // Get user preferences
  const playbackSpeed = localStorage.getItem('asl-playback-speed') || '1';
  
  // Find all containers that need players
  document.querySelectorAll('[data-asl-video-id]').forEach(container => {
    if (!container.hasAttribute('data-player-initialized')) {
      createMuxPlayer(container, container.dataset.aslVideoId, playbackSpeed);
      container.setAttribute('data-player-initialized', 'true');
    }
  });
  
  // Add global player styles
  addPlayerStyles();
}

/**
 * Create a Mux Player in the specified container
 * @param {HTMLElement} container - The container element
 * @param {string} videoId - The video ID
 * @param {string} playbackSpeed - The playback speed
 */
function createMuxPlayer(container, videoId, playbackSpeed) {
  // First check if the video ID is a full playback ID or needs to be fetched
  if (videoId.startsWith('mux_video_')) {
    // Need to fetch the actual playback ID
    fetchVideoPlaybackId(videoId, playbackId => {
      createPlayerElement(container, playbackId, playbackSpeed);
    });
  } else {
    // Already have playback ID
    createPlayerElement(container, videoId, playbackSpeed);
  }
}

/**
 * Fetch the playback ID for a video key
 * @param {string} videoKey - The video key
 * @param {Function} callback - Callback function with playback ID
 */
function fetchVideoPlaybackId(videoKey, callback) {
  fetch(`/accessibility/api/asl-video/${videoKey}`)
    .then(response => response.json())
    .then(data => {
      if (data.success && data.video && data.video.playback_id) {
        callback(data.video.playback_id);
      } else {
        console.error('Failed to fetch playback ID:', data);
        container.innerHTML = '<div class="asl-error">ASL video unavailable</div>';
      }
    })
    .catch(err => {
      console.error('Error fetching playback ID:', err);
      container.innerHTML = '<div class="asl-error">ASL video unavailable</div>';
    });
}

/**
 * Create a player element with the specified playback ID
 * @param {HTMLElement} container - The container element
 * @param {string} playbackId - The Mux playback ID
 * @param {string} playbackSpeed - The playback speed
 */
function createPlayerElement(container, playbackId, playbackSpeed) {
  // Create Mux player element
  const player = document.createElement('mux-player');
  player.setAttribute('stream-type', 'on-demand');
  player.setAttribute('playback-id', playbackId);
  player.setAttribute('playback-rate', playbackSpeed);
  
  // Add accessibility attributes
  player.setAttribute('title', 'ASL Instruction Video');
  player.setAttribute('aria-label', 'American Sign Language instruction video');
  
  // Add Mux metadata
  player.setAttribute('metadata-video-title', container.dataset.videoTitle || 'ASL Instruction');
  player.setAttribute('metadata-viewer-user-id', document.body.dataset.userId || 'anonymous');
  
  // Set player size
  player.style.width = '100%';
  player.style.height = container.dataset.playerHeight || '225px';
  
  // Clear container and add player
  container.innerHTML = '';
  container.appendChild(player);
  
  // Add custom controls
  addCustomControls(container, player);
  
  // Auto-play if enabled in preferences
  const autoplay = localStorage.getItem('asl-autoplay') !== 'false';
  if (autoplay) {
    // Use a slight delay to avoid browser autoplay restrictions
    setTimeout(() => {
      try {
        player.play().catch(e => {
          console.log('Autoplay prevented:', e);
          // Show play button overlay
          addPlayOverlay(container, player);
        });
      } catch (e) {
        console.log('Autoplay error:', e);
      }
    }, 1000);
  } else {
    // Show play button overlay
    addPlayOverlay(container, player);
  }
}

/**
 * Add a play button overlay to the player
 * @param {HTMLElement} container - The container element
 * @param {HTMLElement} player - The player element
 */
function addPlayOverlay(container, player) {
  const overlay = document.createElement('div');
  overlay.className = 'mux-player-overlay';
  overlay.innerHTML = `
    <button class="btn btn-primary play-button">
      <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-play">
        <polygon points="5 3 19 12 5 21 5 3"></polygon>
      </svg>
      Play ASL Video
    </button>
  `;
  
  // Add click handler
  overlay.querySelector('.play-button').addEventListener('click', () => {
    player.play();
    overlay.remove();
  });
  
  container.appendChild(overlay);
}

/**
 * Add custom controls to the player
 * @param {HTMLElement} container - The container element
 * @param {HTMLElement} player - The player element
 */
function addCustomControls(container, player) {
  // Create controls container
  const controls = document.createElement('div');
  controls.className = 'asl-custom-controls';
  
  // Create speed selector
  const speedSelector = document.createElement('select');
  speedSelector.className = 'form-select form-select-sm speed-selector';
  speedSelector.innerHTML = `
    <option value="0.75">0.75x</option>
    <option value="1" selected>1x</option>
    <option value="1.25">1.25x</option>
    <option value="1.5">1.5x</option>
  `;
  
  // Set initial value based on preferences
  const savedSpeed = localStorage.getItem('asl-playback-speed');
  if (savedSpeed) {
    speedSelector.value = savedSpeed;
  }
  
  // Add change handler
  speedSelector.addEventListener('change', e => {
    const speed = e.target.value;
    player.playbackRate = parseFloat(speed);
    localStorage.setItem('asl-playback-speed', speed);
  });
  
  // Add replay button
  const replayButton = document.createElement('button');
  replayButton.className = 'btn btn-sm btn-outline-secondary replay-button';
  replayButton.innerHTML = `
    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-repeat">
      <polyline points="17 1 21 5 17 9"></polyline>
      <path d="M3 11V9a4 4 0 0 1 4-4h14"></path>
      <polyline points="7 23 3 19 7 15"></polyline>
      <path d="M21 13v2a4 4 0 0 1-4 4H3"></path>
    </svg>
    Replay
  `;
  
  // Add click handler
  replayButton.addEventListener('click', () => {
    player.currentTime = 0;
    player.play();
  });
  
  // Add elements to controls
  controls.appendChild(replayButton);
  controls.appendChild(speedSelector);
  
  // Add controls to container after player
  container.appendChild(controls);
}

/**
 * Add global player styles
 */
function addPlayerStyles() {
  // Only add styles once
  if (document.getElementById('mux-player-custom-styles')) return;
  
  const style = document.createElement('style');
  style.id = 'mux-player-custom-styles';
  style.textContent = `
    .asl-custom-controls {
      display: flex;
      justify-content: flex-end;
      align-items: center;
      margin-top: 8px;
      gap: 8px;
    }
    
    .speed-selector {
      width: auto;
      max-width: 90px;
    }
    
    .mux-player-overlay {
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(0, 0, 0, 0.4);
      display: flex;
      justify-content: center;
      align-items: center;
      cursor: pointer;
    }
    
    .mux-player-overlay .play-button {
      display: flex;
      align-items: center;
      gap: 8px;
    }
    
    .asl-error {
      padding: 10px;
      background: var(--bs-danger-bg-subtle);
      color: var(--bs-danger);
      border-radius: 4px;
      text-align: center;
      margin: 10px 0;
    }
  `;
  
  document.head.appendChild(style);
}
