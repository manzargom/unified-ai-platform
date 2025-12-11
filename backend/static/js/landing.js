// landing.js - Simple version
document.addEventListener('DOMContentLoaded', function() {
    console.log('🎮 Landing page loaded');
    
    // Set some default stats
    document.getElementById('projectCount').textContent = '3';
    document.getElementById('characterCount').textContent = '12';
    document.getElementById('sceneCount').textContent = '24';
    
    // Add click effects to buttons
    document.querySelectorAll('.launch-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Launching...';
            this.disabled = true;
            
            setTimeout(() => {
                this.innerHTML = '<i class="fas fa-rocket"></i> Launching...';
                this.disabled = false;
            }, 2000);
        });
    });
});