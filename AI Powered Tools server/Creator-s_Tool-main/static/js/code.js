// code.js - Simple version
document.addEventListener('DOMContentLoaded', function() {
    console.log('💻 Code Assistant loading...');
    
    // After 2 seconds, show a message and redirect back
    setTimeout(() => {
        const loadingContent = document.querySelector('.loading-content');
        loadingContent.innerHTML = `
            <i class="fas fa-exclamation-triangle"></i>
            <h2>Code Assistant Under Construction</h2>
            <p>This tool is being developed. Coming soon!</p>
            <button onclick="window.location.href='/'" style="margin-top: 20px; padding: 10px 20px; background: #00b4d8; color: white; border: none; border-radius: 8px; cursor: pointer;">
                Back to Home
            </button>
        `;
    }, 2000);
});