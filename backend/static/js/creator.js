// creator.js - SIMPLE WORKING VERSION
console.log('🎮 Creator\'s Tool loading...');

// Hide loading screen after 3 seconds no matter what
setTimeout(() => {
    const loadingScreen = document.querySelector('.loading-screen');
    if (loadingScreen) {
        loadingScreen.style.opacity = '0';
        setTimeout(() => {
            loadingScreen.style.display = 'none';
            showBasicInterface();
        }, 300);
    } else {
        showBasicInterface();
    }
}, 2000);

// Show basic interface
function showBasicInterface() {
    console.log('Showing basic interface...');
    
    // Simple HTML that definitely works
    document.body.innerHTML = `
        <style>
            body {
                background: #0a0a0f;
                color: white;
                font-family: 'Segoe UI', sans-serif;
                margin: 0;
                padding: 20px;
            }
            .header {
                background: #141420;
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 20px;
                border: 1px solid #ff5e00;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            .header h1 {
                margin: 0;
                color: #ff5e00;
                display: flex;
                align-items: center;
                gap: 10px;
            }
            .content {
                background: #1e1e2e;
                padding: 30px;
                border-radius: 10px;
                border: 1px solid rgba(255,94,0,0.3);
                text-align: center;
            }
            .btn {
                background: #ff5e00;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                cursor: pointer;
                font-size: 16px;
                margin: 10px;
                display: inline-flex;
                align-items: center;
                gap: 8px;
            }
            .btn:hover {
                background: #ff8c00;
            }
            .btn-blue {
                background: #00b4d8;
            }
            .btn-blue:hover {
                background: #0096c7;
            }
            .asset-grid {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
                gap: 20px;
                margin-top: 30px;
            }
            .asset-card {
                background: rgba(255,255,255,0.05);
                border: 1px solid rgba(255,94,0,0.3);
                border-radius: 10px;
                padding: 15px;
                text-align: left;
            }
            .asset-card h4 {
                margin: 0 0 10px 0;
                color: #ff5e00;
            }
        </style>
        
        <div class="header">
            <h1><i class="fas fa-hat-wizard"></i> Creator's Tool</h1>
            <button class="btn" onclick="window.location.href='/'">
                <i class="fas fa-home"></i> Back to Home
            </button>
        </div>
        
        <div class="content">
            <h2><i class="fas fa-robot"></i> Agent Tools</h2>
            <p>Your visual novel creation studio is ready!</p>
            
            <div style="margin: 30px 0;">
                <button class="btn" onclick="showAssetBrowser()">
                    <i class="fas fa-images"></i> Asset Browser
                </button>
                <button class="btn btn-blue" onclick="showStoryAnalysis()">
                    <i class="fas fa-brain"></i> Story Analysis
                </button>
            </div>
            
            <div id="resultsArea">
                <!-- Results will appear here -->
            </div>
        </div>
    `;
    
    // Add Font Awesome if not already loaded
    if (!document.querySelector('link[href*="font-awesome"]')) {
        const faLink = document.createElement('link');
        faLink.rel = 'stylesheet';
        faLink.href = 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css';
        document.head.appendChild(faLink);
    }
}

// Simple Asset Browser
function showAssetBrowser() {
    document.getElementById('resultsArea').innerHTML = `
        <div style="margin-top: 30px;">
            <h3><i class="fas fa-cube"></i> 3D Asset Browser</h3>
            <p>Search for 3D models, characters, and environments</p>
            
            <div style="display: flex; gap: 10px; margin: 20px 0; justify-content: center;">
                <input type="text" id="searchInput" placeholder="Try: genesis 8, fantasy, sci-fi" 
                       style="padding: 10px; width: 300px; background: rgba(255,255,255,0.05); 
                              border: 1px solid #ff5e00; border-radius: 8px; color: white;">
                <button class="btn" onclick="searchAssets()">
                    <i class="fas fa-search"></i> Search
                </button>
            </div>
            
            <div style="margin: 20px 0;">
                <button class="btn" onclick="quickSearch('genesis 8')" style="background: rgba(0,180,216,0.2); color: #00b4d8;">
                    Genesis 8
                </button>
                <button class="btn" onclick="quickSearch('fantasy')" style="background: rgba(46,204,113,0.2); color: #2ecc71;">
                    Fantasy
                </button>
                <button class="btn" onclick="quickSearch('sci-fi')" style="background: rgba(155,89,182,0.2); color: #9b59b6;">
                    Sci-Fi
                </button>
            </div>
            
            <div id="assetResults" style="min-height: 200px; padding: 20px; background: rgba(0,0,0,0.2); border-radius: 10px;">
                <p style="color: #aaa;">Enter a search term to find 3D assets</p>
            </div>
        </div>
    `;
}

// Simple search function
function searchAssets() {
    const query = document.getElementById('searchInput').value || 'genesis 8';
    const resultsDiv = document.getElementById('assetResults');
    
    // Sample assets
    const assets = [
        { name: 'Genesis 8 Female', type: 'Character', color: '#00b4d8' },
        { name: 'Genesis 8 Male', type: 'Character', color: '#00b4d8' },
        { name: 'Fantasy Castle', type: 'Environment', color: '#2ecc71' },
        { name: 'Sci-Fi Cyborg', type: 'Character', color: '#9b59b6' },
        { name: 'Magic Forest', type: 'Environment', color: '#2ecc71' },
        { name: 'Space Station', type: 'Environment', color: '#9b59b6' }
    ];
    
    // Filter by query
    const filtered = assets.filter(asset => 
        asset.name.toLowerCase().includes(query.toLowerCase()) || 
        asset.type.toLowerCase().includes(query.toLowerCase())
    );
    
    // Display results
    let html = '<div class="asset-grid">';
    
    filtered.forEach(asset => {
        html += `
            <div class="asset-card">
                <h4>${asset.name}</h4>
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="color: ${asset.color}; font-size: 12px; background: ${asset.color}20; 
                          padding: 4px 8px; border-radius: 10px;">${asset.type}</span>
                    <button onclick="addAsset('${asset.name}')" 
                            style="background: ${asset.color}20; color: ${asset.color}; 
                                   border: 1px solid ${asset.color}40; padding: 6px 12px; 
                                   border-radius: 6px; cursor: pointer;">
                        <i class="fas fa-plus"></i> Add
                    </button>
                </div>
            </div>
        `;
    });
    
    html += '</div>';
    
    if (filtered.length === 0) {
        html = `<p style="color: #aaa;">No assets found for "${query}". Try: genesis 8, fantasy, sci-fi</p>`;
    }
    
    resultsDiv.innerHTML = html;
}

// Quick search
function quickSearch(query) {
    document.getElementById('searchInput').value = query;
    searchAssets();
}

// Add asset
function addAsset(name) {
    alert(`✅ Added "${name}" to your project!`);
    console.log(`Asset added: ${name}`);
}

// Story analysis
function showStoryAnalysis() {
    document.getElementById('resultsArea').innerHTML = `
        <div style="margin-top: 30px; text-align: left;">
            <h3><i class="fas fa-brain"></i> Story Analysis</h3>
            <p>Describe your story for AI analysis:</p>
            <textarea id="storyInput" style="width: 100%; height: 100px; padding: 10px; 
                    background: rgba(255,255,255,0.05); border: 1px solid #00b4d8; 
                    border-radius: 8px; color: white; margin: 10px 0;"></textarea>
            <button class="btn btn-blue" onclick="analyzeStory()">
                <i class="fas fa-magic"></i> Analyze Story
            </button>
            <div id="analysisResult" style="margin-top: 20px;"></div>
        </div>
    `;
}

// Analyze story
function analyzeStory() {
    const story = document.getElementById('storyInput').value || 'A fantasy adventure with dragons';
    const resultDiv = document.getElementById('analysisResult');
    
    resultDiv.innerHTML = `
        <div style="background: rgba(0,180,216,0.1); padding: 20px; border-radius: 10px; border: 1px solid rgba(0,180,216,0.3);">
            <h4 style="color: #00b4d8; margin-top: 0;">🔬 Analysis Results</h4>
            <p><strong>Story:</strong> "${story.substring(0, 50)}..."</p>
            <p><strong>Genre:</strong> FANTASY</p>
            <p><strong>Characters needed:</strong> 3-4</p>
            <p><strong>Suggested assets:</strong> Dragon model, Fantasy castle, Magical forest</p>
            <button class="btn" onclick="showAssetBrowser()" style="margin-top: 15px;">
                <i class="fas fa-search"></i> Search for These Assets
            </button>
        </div>
    `;
}

// Make functions available globally
window.showAssetBrowser = showAssetBrowser;
window.searchAssets = searchAssets;
window.quickSearch = quickSearch;
window.addAsset = addAsset;
window.showStoryAnalysis = showStoryAnalysis;
window.analyzeStory = analyzeStory;

console.log('✅ Creator\'s Tool loaded successfully!');