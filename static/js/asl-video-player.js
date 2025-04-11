/**
 * ASL Video Player
 * Handles fetching and displaying ASL videos for deaf and hard of hearing users
 */

// Global variables
let currentVideoPlayer = null;
let currentPlaybackRate = 1.0;

/**
 * Show an ASL video in the modal
 * @param {string} videoKey - The key identifier for the ASL video
 */
function showASLVideo(videoKey) {
    // Check if ASL videos are enabled in user preferences
    const aslVideosEnabled = localStorage.getItem('asl_videos_enabled') !== 'false';
    if (!aslVideosEnabled) {
        console.log('ASL videos are disabled in user preferences');
        return;
    }

    // Get modal elements
    const modal = new bootstrap.Modal(document.getElementById('asl-video-modal'));
    const videoTitle = document.getElementById('asl-video-title');
    const videoContainer = document.getElementById('asl-video-player');
    
    // Show loading state
    videoTitle.textContent = 'Loading ASL Video...';
    videoContainer.innerHTML = `
        <div class="d-flex justify-content-center align-items-center h-100">
            <div class="spinner-border text-info" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
        </div>
    `;
    
    // Show the modal
    modal.show();
    
    // Fetch the video from the API
    fetch(`/asl-video/${videoKey}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Video not found');
            }
            return response.json();
        })
        .then(data => {
            // Update modal title
            videoTitle.textContent = data.title || 'ASL Video';
            
            // Create video player
            createVideoPlayer(videoContainer, data.playback_url, data.poster_url);
            
            // Apply saved playback rate
            applyPlaybackRate();
        })
        .catch(error => {
            console.error('Error fetching ASL video:', error);
            videoContainer.innerHTML = `
                <div class="alert alert-danger m-3">
                    <h5><i class="fas fa-exclamation-triangle"></i> Video Not Available</h5>
                    <p>Sorry, the requested ASL video is not available at this time.</p>
                    <p>Please contact support for assistance.</p>
                </div>
            `;
        });
}

/**
 * Create a video player in the container
 * @param {HTMLElement} container - The HTML element to place the video player in
 * @param {string} videoUrl - The URL of the video
 * @param {string} posterUrl - The URL of the poster image (optional)
 */
function createVideoPlayer(container, videoUrl, posterUrl = '') {
    // Create video element
    const videoElement = document.createElement('video');
    videoElement.className = 'asl-video w-100 h-100';
    videoElement.controls = true;
    videoElement.autoplay = true;
    videoElement.playsInline = true;
    
    // Set poster if available
    if (posterUrl) {
        videoElement.poster = posterUrl;
    }
    
    // Create source element
    const sourceElement = document.createElement('source');
    sourceElement.src = videoUrl;
    sourceElement.type = 'video/mp4';
    
    // Add fallback text
    videoElement.innerHTML = 'Your browser does not support the video tag.';
    
    // Append source to video element
    videoElement.appendChild(sourceElement);
    
    // Clear container and append video
    container.innerHTML = '';
    container.appendChild(videoElement);
    
    // Store reference to the player
    currentVideoPlayer = videoElement;
    
    // Listen for playback rate changes
    document.getElementById('video-speed').addEventListener('change', function() {
        currentPlaybackRate = parseFloat(this.value);
        applyPlaybackRate();
        
        // Save preference
        localStorage.setItem('preferred_video_speed', currentPlaybackRate);
    });
}

/**
 * Apply the current playback rate to the video
 */
function applyPlaybackRate() {
    if (currentVideoPlayer) {
        currentVideoPlayer.playbackRate = currentPlaybackRate;
    }
}

/**
 * Initialize ASL video player functionality
 */
document.addEventListener('DOMContentLoaded', function() {
    // Load saved playback rate preference
    const savedRate = localStorage.getItem('preferred_video_speed');
    if (savedRate) {
        currentPlaybackRate = parseFloat(savedRate);
        const speedSelector = document.getElementById('video-speed');
        if (speedSelector) {
            speedSelector.value = savedRate;
        }
    }
    
    // Check for any data-auto-asl elements to show on page load
    const autoAslElements = document.querySelectorAll('[data-auto-asl]');
    if (autoAslElements.length > 0) {
        setTimeout(() => {
            const element = autoAslElements[0];
            const videoKey = element.getAttribute('data-auto-asl');
            showASLVideo(videoKey);
        }, 1000); // Small delay to ensure page is fully loaded
    }
});