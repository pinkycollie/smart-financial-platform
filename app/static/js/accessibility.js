/**
 * Accessibility functionality for April's ASL integration
 */

// Initialize ASL features when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  initASLVideoPlayer();
  initVisualAlerts();
  initAccessibilityPreferences();
});

/**
 * Initialize the ASL video player for page content
 */
function initASLVideoPlayer() {
  const aslContainer = document.getElementById('asl-video-container');
  if (!aslContainer) return;
  
  // Get video ID from data attribute or from the page
  const videoId = aslContainer.dataset.videoId || document.body.dataset.aslVideoId;
  if (!videoId) return;
  
  // Load ASL video
  loadASLVideo(videoId, aslContainer);
  
  // Add controls for ASL video
  initASLVideoControls(aslContainer);
}

/**
 * Load an ASL video into the specified container
 * @param {string} videoId - The Mux video ID
 * @param {HTMLElement} container - The container element
 */
function loadASLVideo(videoId, container) {
  // Fetch video details from API
  fetch(`/accessibility/api/asl-video/${videoId}`)
    .then(response => response.json())
    .then(data => {
      if (data.success && data.video) {
        const video = data.video;
        
        // Create Mux player element
        const player = document.createElement('mux-player');
        player.setAttribute('stream-type', 'on-demand');
        player.setAttribute('playback-id', video.playback_id);
        player.setAttribute('metadata-video-title', video.title || 'ASL Instruction');
        player.setAttribute('metadata-viewer-user-id', document.body.dataset.userId || 'anonymous');
        
        // Get user's preferred playback speed
        const speed = localStorage.getItem('asl-playback-speed') || '1';
        player.setAttribute('default-playback-rate', speed);
        
        // Add player to container
        container.innerHTML = '';
        container.appendChild(player);
        
        // Auto-play if preferences allow
        const autoplay = localStorage.getItem('asl-autoplay') || 'true';
        if (autoplay === 'true') {
          player.play();
        }
      } else {
        showVideoError(container);
      }
    })
    .catch(err => {
      console.error('Error loading ASL video:', err);
      showVideoError(container);
    });
}

/**
 * Show error message when video fails to load
 * @param {HTMLElement} container - The container element
 */
function showVideoError(container) {
  container.innerHTML = `
    <div class="asl-video-error">
      <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-alert-triangle">
        <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
        <line x1="12" y1="9" x2="12" y2="13"></line>
        <line x1="12" y1="17" x2="12.01" y2="17"></line>
      </svg>
      <p>ASL video unavailable. Please try again later.</p>
    </div>
  `;
}

/**
 * Initialize controls for ASL video player
 * @param {HTMLElement} container - The container element
 */
function initASLVideoControls(container) {
  // Create controls container
  const controls = document.createElement('div');
  controls.className = 'asl-video-controls';
  
  // Create speed control
  const speedControl = document.createElement('select');
  speedControl.className = 'form-select form-select-sm asl-speed-control';
  speedControl.innerHTML = `
    <option value="0.75">0.75x Speed</option>
    <option value="1" selected>1x Speed</option>
    <option value="1.25">1.25x Speed</option>
    <option value="1.5">1.5x Speed</option>
  `;
  
  // Set saved speed if available
  const savedSpeed = localStorage.getItem('asl-playback-speed');
  if (savedSpeed) {
    speedControl.value = savedSpeed;
  }
  
  // Add change handler
  speedControl.addEventListener('change', (e) => {
    const speed = e.target.value;
    localStorage.setItem('asl-playback-speed', speed);
    
    // Update player speed
    const player = container.querySelector('mux-player');
    if (player) {
      player.playbackRate = parseFloat(speed);
    }
  });
  
  // Add controls to container
  controls.appendChild(speedControl);
  container.appendChild(controls);
}

/**
 * Initialize visual alerts for important information
 */
function initVisualAlerts() {
  // Check if visual alerts are enabled
  const visualAlertsEnabled = localStorage.getItem('visual-alerts-enabled') !== 'false';
  if (!visualAlertsEnabled) return;
  
  // Add visual indicators to form fields with errors
  const invalidFields = document.querySelectorAll('.is-invalid');
  invalidFields.forEach(field => {
    // Add pulsing border
    field.classList.add('visual-alert-pulse');
    
    // Add visual indicator icon
    const fieldParent = field.parentElement;
    const alertIcon = document.createElement('div');
    alertIcon.className = 'visual-alert-icon';
    alertIcon.innerHTML = `
      <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-alert-circle">
        <circle cx="12" cy="12" r="10"></circle>
        <line x1="12" y1="8" x2="12" y2="12"></line>
        <line x1="12" y1="16" x2="12.01" y2="16"></line>
      </svg>
    `;
    fieldParent.appendChild(alertIcon);
  });
  
  // Add visual indicators to flash messages
  const flashMessages = document.querySelectorAll('.alert');
  flashMessages.forEach(message => {
    message.classList.add('visual-alert-flash');
  });
}

/**
 * Initialize accessibility preferences
 */
function initAccessibilityPreferences() {
  // Get toggle switch for ASL videos
  const aslToggle = document.getElementById('asl-video-toggle');
  if (aslToggle) {
    // Set initial state
    const aslEnabled = localStorage.getItem('asl-enabled') !== 'false';
    aslToggle.checked = aslEnabled;
    
    // Update DOM based on preference
    if (!aslEnabled) {
      document.querySelectorAll('.asl-video-container').forEach(container => {
        container.style.display = 'none';
      });
    }
    
    // Add change handler
    aslToggle.addEventListener('change', (e) => {
      const enabled = e.target.checked;
      localStorage.setItem('asl-enabled', enabled);
      
      // Show/hide ASL videos
      document.querySelectorAll('.asl-video-container').forEach(container => {
        container.style.display = enabled ? 'block' : 'none';
      });
    });
  }
  
  // Get toggle for autoplay
  const autoplayToggle = document.getElementById('asl-autoplay-toggle');
  if (autoplayToggle) {
    // Set initial state
    const autoplayEnabled = localStorage.getItem('asl-autoplay') !== 'false';
    autoplayToggle.checked = autoplayEnabled;
    
    // Add change handler
    autoplayToggle.addEventListener('change', (e) => {
      localStorage.setItem('asl-autoplay', e.target.checked);
    });
  }
  
  // Get toggle for visual alerts
  const visualAlertsToggle = document.getElementById('visual-alerts-toggle');
  if (visualAlertsToggle) {
    // Set initial state
    const visualAlertsEnabled = localStorage.getItem('visual-alerts-enabled') !== 'false';
    visualAlertsToggle.checked = visualAlertsEnabled;
    
    // Add change handler
    visualAlertsToggle.addEventListener('change', (e) => {
      localStorage.setItem('visual-alerts-enabled', e.target.checked);
    });
  }
}

/**
 * Request live ASL interpretation
 */
function requestLiveASL(context) {
  // Show loading state
  const requestButton = document.getElementById('request-asl-button');
  const originalText = requestButton.textContent;
  requestButton.disabled = true;
  requestButton.innerHTML = `
    <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
    Requesting...
  `;
  
  // Request ASL session
  fetch('/fintech/api/request-asl-session', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ context: context }),
  })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        // Show success message
        const sessionModal = new bootstrap.Modal(document.getElementById('asl-session-modal'));
        document.getElementById('asl-session-link').href = data.join_url;
        document.getElementById('asl-session-link').textContent = data.join_url;
        sessionModal.show();
      } else {
        // Show error
        showError('Failed to create ASL session: ' + (data.error || 'Unknown error'));
      }
    })
    .catch(err => {
      console.error('Error requesting ASL session:', err);
      showError('Failed to create ASL session. Please try again later.');
    })
    .finally(() => {
      // Reset button
      requestButton.disabled = false;
      requestButton.textContent = originalText;
    });
}

/**
 * Display an error message
 * @param {string} message - The error message
 */
function showError(message) {
  const errorDiv = document.createElement('div');
  errorDiv.className = 'alert alert-danger alert-dismissible fade show visual-alert-flash';
  errorDiv.innerHTML = `
    ${message}
    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
  `;
  
  // Add to page
  const alertContainer = document.getElementById('alert-container');
  if (alertContainer) {
    alertContainer.appendChild(errorDiv);
  } else {
    document.querySelector('main').prepend(errorDiv);
  }
  
  // Remove after 5 seconds
  setTimeout(() => {
    errorDiv.remove();
  }, 5000);
}
