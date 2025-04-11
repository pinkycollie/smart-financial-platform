/**
 * Deaf Support Bot functionality for April's ASL accessibility
 */

// Initialize the deaf support bot when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  initDeafSupportBot();
});

/**
 * Initialize the deaf support bot
 */
function initDeafSupportBot() {
  const botContainer = document.getElementById('deaf-support-bot');
  if (!botContainer) return;
  
  // Set up message form
  const messageForm = document.getElementById('deaf-support-message-form');
  if (messageForm) {
    messageForm.addEventListener('submit', handleMessageSubmit);
  }
  
  // Set up suggestion clicks
  document.addEventListener('click', e => {
    if (e.target.classList.contains('bot-suggestion')) {
      sendMessage(e.target.textContent);
    }
  });
  
  // Initialize bot with welcome message
  if (document.querySelector('.bot-messages').children.length === 0) {
    displayBotMessage({
      text: "Hello! I'm April's ASL support assistant. How can I help you today?",
      asl_video_id: "greeting",
      suggestions: ["Tax filing help", "Financial profile", "Investment advice"]
    });
  }
}

/**
 * Handle message form submission
 * @param {Event} e - Form submit event
 */
function handleMessageSubmit(e) {
  e.preventDefault();
  
  const messageInput = document.getElementById('deaf-support-message');
  const message = messageInput.value.trim();
  
  if (message) {
    // Display user message
    displayUserMessage(message);
    
    // Clear input
    messageInput.value = '';
    
    // Send message to bot
    sendMessage(message);
  }
}

/**
 * Send a message to the deaf support bot
 * @param {string} message - The message text
 */
function sendMessage(message) {
  // Get context if available
  const botContainer = document.getElementById('deaf-support-bot');
  const context = botContainer.dataset.context;
  
  // Show loading indicator
  showBotTyping();
  
  // Send to server
  fetch('/fintech/api/deaf-support', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      message: message,
      context: context
    }),
  })
    .then(response => response.json())
    .then(data => {
      // Hide typing indicator
      hideBotTyping();
      
      // Display bot response
      displayBotMessage(data);
    })
    .catch(err => {
      console.error('Error sending message to bot:', err);
      
      // Hide typing indicator
      hideBotTyping();
      
      // Display error message
      displayBotMessage({
        text: "I'm sorry, I encountered an error. Please try again later.",
        asl_video_id: "error",
        suggestions: ["Start over", "Contact support"]
      });
    });
}

/**
 * Display a user message in the chat
 * @param {string} message - The message text
 */
function displayUserMessage(message) {
  const messagesContainer = document.querySelector('.bot-messages');
  
  const messageElement = document.createElement('div');
  messageElement.className = 'message user-message';
  messageElement.innerHTML = `
    <div class="message-content">
      <p>${escapeHtml(message)}</p>
    </div>
    <div class="message-avatar">
      <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-user">
        <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
        <circle cx="12" cy="7" r="4"></circle>
      </svg>
    </div>
  `;
  
  messagesContainer.appendChild(messageElement);
  
  // Scroll to bottom
  messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

/**
 * Display a bot message in the chat
 * @param {Object} data - The bot response data
 */
function displayBotMessage(data) {
  const messagesContainer = document.querySelector('.bot-messages');
  
  const messageElement = document.createElement('div');
  messageElement.className = 'message bot-message';
  
  // Create message content with ASL video
  let messageContent = `
    <div class="message-avatar">
      <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-activity">
        <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
      </svg>
    </div>
    <div class="message-content">
      <p>${escapeHtml(data.text)}</p>
  `;
  
  // Add ASL video if available
  if (data.asl_video_id) {
    messageContent += `
      <div class="asl-video-container" data-asl-video-id="${data.asl_video_id}"></div>
    `;
  }
  
  // Add suggestions if available
  if (data.suggestions && data.suggestions.length > 0) {
    messageContent += '<div class="bot-suggestions">';
    data.suggestions.forEach(suggestion => {
      messageContent += `<button class="btn btn-sm btn-outline-primary bot-suggestion">${escapeHtml(suggestion)}</button>`;
    });
    messageContent += '</div>';
  }
  
  messageContent += '</div>';
  messageElement.innerHTML = messageContent;
  
  messagesContainer.appendChild(messageElement);
  
  // Initialize ASL video if present
  if (data.asl_video_id) {
    const videoContainer = messageElement.querySelector('.asl-video-container');
    initASLVideoForBot(data.asl_video_id, videoContainer);
  }
  
  // Scroll to bottom
  messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

/**
 * Initialize ASL video for the bot message
 * @param {string} videoId - The video ID
 * @param {HTMLElement} container - The container element
 */
function initASLVideoForBot(videoId, container) {
  // First make sure Mux Player is available
  if (!customElements.get('mux-player')) {
    const script = document.createElement('script');
    script.src = 'https://unpkg.com/@mux/mux-player';
    script.type = 'module';
    document.head.appendChild(script);
    
    script.onload = () => {
      createMuxPlayer(container, videoId);
    };
    
    return;
  }
  
  createMuxPlayer(container, videoId);
}

/**
 * Create a Mux Player for the bot
 * @param {HTMLElement} container - The container element
 * @param {string} videoId - The video ID
 */
function createMuxPlayer(container, videoId) {
  // Fetch video details if needed
  if (videoId.startsWith('mux_video_') || !videoId.includes('_')) {
    // Need to fetch the actual playback ID
    fetch(`/accessibility/api/asl-video/${videoId}`)
      .then(response => response.json())
      .then(data => {
        if (data.success && data.video && data.video.playback_id) {
          createPlayerElement(container, data.video.playback_id);
        } else {
          console.error('Failed to fetch playback ID:', data);
          container.innerHTML = '<div class="asl-error">ASL video unavailable</div>';
        }
      })
      .catch(err => {
        console.error('Error fetching playback ID:', err);
        container.innerHTML = '<div class="asl-error">ASL video unavailable</div>';
      });
  } else {
    // Already have playback ID
    createPlayerElement(container, videoId);
  }
}

/**
 * Create a player element for the bot
 * @param {HTMLElement} container - The container element
 * @param {string} playbackId - The Mux playback ID
 */
function createPlayerElement(container, playbackId) {
  // Get user preferences
  const playbackSpeed = localStorage.getItem('asl-playback-speed') || '1';
  
  // Create Mux player element
  const player = document.createElement('mux-player');
  player.setAttribute('stream-type', 'on-demand');
  player.setAttribute('playback-id', playbackId);
  player.setAttribute('playback-rate', playbackSpeed);
  
  // Set player size - smaller for bot
  player.style.width = '100%';
  player.style.height = '150px';
  
  // Clear container and add player
  container.innerHTML = '';
  container.appendChild(player);
  
  // Auto-play if enabled in preferences
  const autoplay = localStorage.getItem('asl-autoplay') !== 'false';
  if (autoplay) {
    setTimeout(() => player.play().catch(e => console.log('Autoplay prevented:', e)), 500);
  } else {
    // Add simple play button
    const playButton = document.createElement('button');
    playButton.className = 'btn btn-sm btn-primary play-button';
    playButton.innerHTML = 'Play ASL';
    playButton.style.position = 'absolute';
    playButton.style.top = '50%';
    playButton.style.left = '50%';
    playButton.style.transform = 'translate(-50%, -50%)';
    
    playButton.addEventListener('click', () => {
      player.play();
      playButton.remove();
    });
    
    container.appendChild(playButton);
  }
}

/**
 * Show the bot typing indicator
 */
function showBotTyping() {
  const messagesContainer = document.querySelector('.bot-messages');
  
  // Check if typing indicator already exists
  if (document.querySelector('.bot-typing')) return;
  
  const typingElement = document.createElement('div');
  typingElement.className = 'message bot-message bot-typing';
  typingElement.innerHTML = `
    <div class="message-avatar">
      <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-activity">
        <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
      </svg>
    </div>
    <div class="message-content">
      <div class="typing-indicator">
        <span></span>
        <span></span>
        <span></span>
      </div>
    </div>
  `;
  
  messagesContainer.appendChild(typingElement);
  
  // Scroll to bottom
  messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

/**
 * Hide the bot typing indicator
 */
function hideBotTyping() {
  const typingIndicator = document.querySelector('.bot-typing');
  if (typingIndicator) {
    typingIndicator.remove();
  }
}

/**
 * Clear the bot conversation history
 */
function clearBotHistory() {
  // Confirm with user
  if (!confirm('Are you sure you want to clear the conversation history?')) {
    return;
  }
  
  // Send request to clear history
  fetch('/accessibility/api/clear-bot-history', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    }
  })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        // Clear messages in UI
        const messagesContainer = document.querySelector('.bot-messages');
        messagesContainer.innerHTML = '';
        
        // Restart with welcome message
        displayBotMessage({
          text: "Hello! I'm April's ASL support assistant. How can I help you today?",
          asl_video_id: "greeting",
          suggestions: ["Tax filing help", "Financial profile", "Investment advice"]
        });
      } else {
        console.error('Failed to clear history:', data);
      }
    })
    .catch(err => {
      console.error('Error clearing bot history:', err);
    });
}

/**
 * Request live ASL support from the bot
 */
function requestLiveASLSupport() {
  // Get context if available
  const botContainer = document.getElementById('deaf-support-bot');
  const context = botContainer.dataset.context;
  
  // Show loading state
  const requestButton = document.getElementById('request-live-asl-button');
  if (requestButton) {
    const originalText = requestButton.textContent;
    requestButton.disabled = true;
    requestButton.innerHTML = `
      <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
      Requesting...
    `;
  }
  
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
        // Display session information
        displayBotMessage({
          text: `I've created a live ASL session for you. Click the link to join: ${data.join_url}`,
          asl_video_id: "live_asl_session",
          suggestions: ["Thank you"]
        });
      } else {
        displayBotMessage({
          text: "I'm sorry, I couldn't create an ASL session. Please try again later.",
          asl_video_id: "error",
          suggestions: ["Try again later", "Contact support"]
        });
      }
    })
    .catch(err => {
      console.error('Error requesting ASL session:', err);
      displayBotMessage({
        text: "I'm sorry, I encountered an error creating an ASL session. Please try again later.",
        asl_video_id: "error",
        suggestions: ["Try again later", "Contact support"]
      });
    })
    .finally(() => {
      // Reset button
      if (requestButton) {
        requestButton.disabled = false;
        requestButton.textContent = originalText;
      }
    });
}

/**
 * Escape HTML special characters to prevent XSS
 * @param {string} unsafe - Unsafe string
 * @returns {string} Escaped string
 */
function escapeHtml(unsafe) {
  return unsafe
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
