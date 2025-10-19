// YouTube API Configuration
const YOUTUBE_API_KEY = 'AIzaSyCsu8HxkeAorYspiyDKsB8WQl1HGc2p5wQ'; // Replace with your API key
const YOUTUBE_API_URL = 'https://www.googleapis.com/youtube/v3/search';
const YOUTUBE_VIDEO_API_URL = 'https://www.googleapis.com/youtube/v3/videos';

let currentQuery = 'personal finance basics';
let currentVideoData = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    // Load default videos
    loadTopicVideos('personal finance basics');
});

// Search videos based on user input
function searchVideos() {
    const searchInput = document.getElementById('videoSearchInput');
    const query = searchInput.value.trim();
    
    if (query) {
        currentQuery = query + ' finance';
        loadVideos(currentQuery);
        
        // Remove active class from all topic buttons
        document.querySelectorAll('.topic-btn').forEach(btn => {
            btn.classList.remove('active');
        });
    }
}

// Load videos for specific topic
function loadTopicVideos(topic) {
    currentQuery = topic;
    document.getElementById('videoSearchInput').value = '';
    
    // Update active button
    document.querySelectorAll('.topic-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
    
    loadVideos(topic);
}

// Fetch and display videos from YouTube API
async function loadVideos(query) {
    const container = document.getElementById('videosContainer');
    
    // Show loading state
    container.innerHTML = `
        <div class="loading-videos">
            <div class="pixel-loader"></div>
            <p style="font-family: var(--font-heading); margin-top: 20px;">Finding best videos...</p>
        </div>
    `;
    
    try {
        const response = await fetch(
            `${YOUTUBE_API_URL}?part=snippet&q=${encodeURIComponent(query)}&type=video&maxResults=12&videoCategoryId=26&relevanceLanguage=en&safeSearch=strict&key=${YOUTUBE_API_KEY}`
        );
        
        if (!response.ok) {
            throw new Error('Failed to fetch videos');
        }
        
        const data = await response.json();
        
        if (data.items && data.items.length > 0) {
            displayVideos(data.items);
        } else {
            container.innerHTML = `
                <div class="no-results">
                    <p>😕 No videos found. Try another search term!</p>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error fetching videos:', error);
        container.innerHTML = `
            <div class="no-results">
                <p>⚠️ Unable to load videos. Please check your API key and try again.</p>
                <p style="font-size: 0.9rem; margin-top: 10px; color: var(--color-text-secondary);">Error: ${error.message}</p>
            </div>
        `;
    }
}

// Display videos in grid
function displayVideos(videos) {
    const container = document.getElementById('videosContainer');
    
    const videosHTML = videos.map(video => {
        const videoId = video.id.videoId;
        const title = video.snippet.title;
        const channel = video.snippet.channelTitle;
        const thumbnail = video.snippet.thumbnails.medium.url;
        const description = video.snippet.description;
        const publishedAt = new Date(video.snippet.publishedAt);
        const timeAgo = getTimeAgo(publishedAt);
        
        return `
            <div class="video-card" onclick='openVideoPlayer("${videoId}", ${JSON.stringify(escapeHtml(title))}, ${JSON.stringify(escapeHtml(channel))}, ${JSON.stringify(escapeHtml(description))})'>
                <img src="${thumbnail}" alt="${escapeHtml(title)}" class="video-thumbnail">
                <div class="video-info">
                    <h3 class="video-title">${escapeHtml(title)}</h3>
                    <p class="video-channel">📺 ${escapeHtml(channel)}</p>
                    <div class="video-meta">
                        <span>${timeAgo}</span>
                        <span class="watch-badge">▶ WATCH</span>
                    </div>
                </div>
            </div>
        `;
    }).join('');
    
    container.innerHTML = `<div class="videos-grid">${videosHTML}</div>`;
}

// Open video player in modal
function openVideoPlayer(videoId, title, channel, description) {
    const modal = document.getElementById('videoModal');
    const player = document.getElementById('videoPlayer');
    const modalTitle = document.getElementById('modalVideoTitle');
    const modalChannel = document.getElementById('modalVideoChannel');
    const modalDescription = document.getElementById('modalVideoDescription');
    
    // Set video details
    modalTitle.textContent = title;
    modalChannel.textContent = '📺 ' + channel;
    modalDescription.textContent = description || 'No description available.';
    
    // Set iframe source with autoplay
    player.src = `https://www.youtube.com/embed/${videoId}?autoplay=1&rel=0`;
    
    // Show modal
    modal.style.display = 'flex';
    document.body.style.overflow = 'hidden';
}

// Close video player
function closeVideoPlayer() {
    const modal = document.getElementById('videoModal');
    const player = document.getElementById('videoPlayer');
    
    // Stop video by clearing src
    player.src = '';
    
    // Hide modal
    modal.style.display = 'none';
    document.body.style.overflow = 'auto';
}

// Close modal when pressing Escape key
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        const modal = document.getElementById('videoModal');
        if (modal && modal.style.display === 'flex') {
            closeVideoPlayer();
        }
    }
});

// Helper function to get time ago
function getTimeAgo(date) {
    const seconds = Math.floor((new Date() - date) / 1000);
    
    let interval = Math.floor(seconds / 31536000);
    if (interval >= 1) return interval + ' year' + (interval > 1 ? 's' : '') + ' ago';
    
    interval = Math.floor(seconds / 2592000);
    if (interval >= 1) return interval + ' month' + (interval > 1 ? 's' : '') + ' ago';
    
    interval = Math.floor(seconds / 86400);
    if (interval >= 1) return interval + ' day' + (interval > 1 ? 's' : '') + ' ago';
    
    interval = Math.floor(seconds / 3600);
    if (interval >= 1) return interval + ' hour' + (interval > 1 ? 's' : '') + ' ago';
    
    interval = Math.floor(seconds / 60);
    if (interval >= 1) return interval + ' minute' + (interval > 1 ? 's' : '') + ' ago';
    
    return 'Just now';
}

// Helper function to escape HTML
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}