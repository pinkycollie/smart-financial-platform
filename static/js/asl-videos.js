/**
 * ASL Video Handler for the DEAF FIRST Platform
 * Provides functionality for playing ASL videos and handling both Mux videos and SignASL embeds
 */

// Track if the user has ASL videos enabled
let aslVideosEnabled = localStorage.getItem('asl_videos_enabled') !== 'false';

/**
 * Show an ASL video modal for a specific key
 * @param {string} videoKey - The key identifier for the ASL video
 */
function showASLVideo(videoKey) {
    if (!aslVideosEnabled) {
        console.log('ASL videos are disabled by user preference');
        return;
    }

    // Create a modal if it doesn't exist
    let videoModal = document.getElementById('asl-video-modal');
    if (!videoModal) {
        videoModal = createASLVideoModal();
    }

    // Show a loading spinner
    const modalBody = videoModal.querySelector('.modal-body');
    modalBody.innerHTML = '<div class="text-center my-5"><div class="spinner-border text-info" role="status"><span class="visually-hidden">Loading ASL video...</span></div><p class="mt-3">Loading ASL video...</p></div>';

    // Show the modal
    const modalInstance = new bootstrap.Modal(videoModal);
    modalInstance.show();

    // Fetch the video
    fetch(`/insurance/asl-videos/${videoKey}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(video => {
            if (video.is_embed) {
                // This is a SignASL embed - use the embed HTML directly
                modalBody.innerHTML = video.embed_html;
                
                // Update modal title
                const modalTitle = videoModal.querySelector('.modal-title');
                modalTitle.textContent = video.title;
                
                // Add source attribution if available
                if (video.source) {
                    const attribution = document.createElement('p');
                    attribution.className = 'text-muted mt-2 mb-0 text-end';
                    attribution.innerHTML = `Source: <a href="${video.url}" target="_blank">${video.source}</a>`;
                    modalBody.appendChild(attribution);
                }
            } else {
                // This is a Mux video - use the player
                const playerHTML = `
                    <div class="ratio ratio-16x9">
                        <iframe 
                            src="https://stream.mux.com/${video.playback_id}" 
                            allowfullscreen 
                            allow="autoplay; fullscreen">
                        </iframe>
                    </div>
                    <p class="mt-2">${video.description}</p>
                `;
                modalBody.innerHTML = playerHTML;
                
                // Update modal title
                const modalTitle = videoModal.querySelector('.modal-title');
                modalTitle.textContent = video.title;
            }
        })
        .catch(error => {
            console.error('Error fetching ASL video:', error);
            modalBody.innerHTML = `
                <div class="alert alert-warning">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    <div>
                        <h5>ASL Video Unavailable</h5>
                        <p>We're sorry, but this ASL video is currently unavailable. We're working to add more ASL content soon.</p>
                    </div>
                </div>
            `;
        });
}

/**
 * Create the ASL video modal
 * @returns {HTMLElement} The modal element
 */
function createASLVideoModal() {
    const modal = document.createElement('div');
    modal.id = 'asl-video-modal';
    modal.className = 'modal fade';
    modal.tabIndex = '-1';
    modal.setAttribute('aria-labelledby', 'aslVideoModalLabel');
    modal.setAttribute('aria-hidden', 'true');

    modal.innerHTML = `
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" id="aslVideoModalLabel">ASL Video</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <!-- Video will be loaded here -->
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                </div>
            </div>
        </div>
    `;

    document.body.appendChild(modal);
    return modal;
}

/**
 * Toggle ASL video preference setting
 * @param {boolean} enabled - Whether ASL videos should be enabled
 */
function toggleASLVideos(enabled) {
    aslVideosEnabled = enabled;
    localStorage.setItem('asl_videos_enabled', enabled);
    
    // Update any UI that needs to reflect this setting
    const aslToggleButtons = document.querySelectorAll('.asl-toggle');
    if (aslToggleButtons) {
        aslToggleButtons.forEach(button => {
            if (enabled) {
                button.classList.add('active');
                button.setAttribute('aria-pressed', 'true');
            } else {
                button.classList.remove('active');
                button.setAttribute('aria-pressed', 'false');
            }
        });
    }
}

// Initialize event listeners when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Set up event listeners for ASL video buttons
    document.querySelectorAll('[data-asl-video]').forEach(button => {
        button.addEventListener('click', function() {
            const videoKey = this.getAttribute('data-asl-video');
            showASLVideo(videoKey);
        });
    });
    
    // Set up ASL toggle buttons if they exist
    const aslToggleButtons = document.querySelectorAll('.asl-toggle');
    if (aslToggleButtons) {
        aslToggleButtons.forEach(button => {
            button.addEventListener('click', function() {
                toggleASLVideos(!aslVideosEnabled);
            });
            
            // Set initial state
            if (aslVideosEnabled) {
                button.classList.add('active');
                button.setAttribute('aria-pressed', 'true');
            }
        });
    }
});