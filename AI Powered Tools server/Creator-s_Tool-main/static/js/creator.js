// creator.js - SIMPLE WORKING VERSION
console.log('🎮 Creator\'s Tool loading...');

// Hide loading screen immediately
setTimeout(() => {
    const loadingScreen = document.querySelector('.loading-screen');
    if (loadingScreen) {
        loadingScreen.style.opacity = '0';
        setTimeout(() => {
            loadingScreen.style.display = 'none';
        }, 300);
    }
}, 500);

// Simple app class
class SimpleCreatorTool {
    constructor() {
        console.log('🛠️ Simple Creator Tool created');
        this.projects = [];
        this.init();
    }

    async init() {
        console.log('Initializing...');
        
        // Setup basic UI
        this.setupBasicUI();
        
        // Load projects
        await this.loadProjects();
        
        // Setup event listeners
        this.setupEventListeners();
        
        console.log('✅ Ready!');
    }

    setupBasicUI() {
        // Add agent status to welcome screen
        const welcomeScreen = document.querySelector('.welcome-screen');
        if (welcomeScreen) {
            const agentStatus = document.createElement('div');
            agentStatus.className = 'agent-status-display';
            agentStatus.innerHTML = `
                <p><i class="fas fa-robot"></i> Agents Status:</p>
                <p>🐧 Skipper: <span style="color:#ff5e00;font-weight:bold">READY</span></p>
                <p>🔬 Kowalski: <span style="color:#00b4d8;font-weight:bold">READY</span></p>
            `;
            
            // Insert after welcome subtitle
            const subtitle = welcomeScreen.querySelector('.welcome-subtitle');
            if (subtitle) {
                subtitle.parentNode.insertBefore(agentStatus, subtitle.nextSibling);
            }
        }
    }

    setupEventListeners() {
        console.log('Setting up event listeners...');
        
        // Back button
        const backBtn = document.getElementById('backToLanding');
        if (backBtn) {
            backBtn.onclick = () => window.location.href = '/';
        }
        
        // Create Project button
        const createBtn = document.getElementById('createFirstProject');
        if (createBtn) {
            createBtn.onclick = () => this.showSimpleModal('Create New Project', `
                <p>Project creation coming soon!</p>
                <button onclick="window.simpleCreator.showNotification('Project created!', 'success'); this.parentElement.parentElement.parentElement.style.display='none'" 
                        style="padding:10px 20px; background:#ff5e00; color:white; border:none; border-radius:8px; cursor:pointer">
                    Create Project
                </button>
            `);
        }
        
        // Open Existing Project button
        const openBtn = document.getElementById('openExistingProject');
        if (openBtn) {
            openBtn.onclick = () => this.showProjectsModal();
        }
        
        // Try Agent Tools button
        const agentBtn = document.getElementById('tryAgentTools');
        if (agentBtn) {
            agentBtn.onclick = () => this.showAgentToolsModal();
        }
        
        // Project Open buttons (for existing projects in list)
        setTimeout(() => {
            document.querySelectorAll('.project-item-btn').forEach(btn => {
                btn.onclick = () => this.showNotification('Opening project...', 'info');
            });
        }, 1000);
    }

    async loadProjects() {
        try {
            const response = await fetch('/api/projects');
            const data = await response.json();
            
            if (data.success) {
                this.projects = data.projects;
                console.log(`Loaded ${this.projects.length} projects`);
            }
        } catch (error) {
            console.log('Error loading projects:', error);
        }
    }

    showProjectsModal() {
        let projectsHTML = '';
        
        if (this.projects && this.projects.length > 0) {
            projectsHTML = this.projects.map(project => `
                <div style="background:rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.1); border-radius:10px; padding:15px; margin:10px 0;">
                    <div style="display:flex; align-items:center; gap:15px;">
                        <i class="fas fa-folder" style="color:#ff5e00; font-size:24px;"></i>
                        <div>
                            <h4 style="margin:0; color:white">${project.name}</h4>
                            <div style="display:flex; gap:15px; font-size:12px; color:#aaa;">
                                <span><i class="fas fa-calendar"></i> ${project.created ? new Date(project.created).toLocaleDateString() : 'Unknown'}</span>
                                <span><i class="fas fa-users"></i> ${project.characters || 0} characters</span>
                                <span><i class="fas fa-scroll"></i> ${project.scenes || 0} scenes</span>
                            </div>
                        </div>
                    </div>
                    <button onclick="window.simpleCreator.openProject('${project.id}', '${project.name}')" 
                            style="margin-top:10px; padding:8px 15px; background:rgba(255,94,0,0.1); border:1px solid rgba(255,94,0,0.3); border-radius:6px; color:#ff5e00; cursor:pointer; display:flex; align-items:center; gap:5px;">
                        <i class="fas fa-folder-open"></i> Open
                    </button>
                </div>
            `).join('');
        } else {
            projectsHTML = '<p style="text-align:center; color:#aaa;">No projects found</p>';
        }
        
        this.showSimpleModal('Open Project', projectsHTML);
    }

    showAgentToolsModal() {
        const modalHTML = `
            <div style="text-align:center;">
                <div style="margin:20px 0;">
                    <div style="display:flex; justify-content:center; gap:20px; margin-bottom:30px;">
                        <div style="background:rgba(0,180,216,0.1); padding:15px; border-radius:10px; border:1px solid rgba(0,180,216,0.3);">
                            <div style="font-size:24px;">🐧</div>
                            <h4 style="margin:10px 0; color:#00b4d8">Skipper</h4>
                            <div style="padding:4px 10px; background:rgba(46,204,113,0.2); color:#2ecc71; border-radius:20px; font-size:12px; font-weight:bold;">
                                READY
                            </div>
                        </div>
                        <div style="background:rgba(255,94,0,0.1); padding:15px; border-radius:10px; border:1px solid rgba(255,94,0,0.3);">
                            <div style="font-size:24px;">🔬</div>
                            <h4 style="margin:10px 0; color:#ff5e00">Kowalski</h4>
                            <div style="padding:4px 10px; background:rgba(46,204,113,0.2); color:#2ecc71; border-radius:20px; font-size:12px; font-weight:bold;">
                                READY
                            </div>
                        </div>
                    </div>
                    
                    <div style="display:grid; grid-template-columns:1fr; gap:15px; margin:20px 0;">
                        <button onclick="window.simpleCreator.startStoryAnalysis()" 
                                style="padding:15px; background:rgba(255,94,0,0.1); border:1px solid rgba(255,94,0,0.3); border-radius:10px; color:#ff5e00; cursor:pointer; text-align:left;">
                            <div style="display:flex; align-items:center; gap:10px;">
                                <i class="fas fa-brain" style="font-size:20px;"></i>
                                <div>
                                    <h4 style="margin:0;">Story Analysis</h4>
                                    <p style="margin:5px 0 0 0; font-size:14px; color:#aaa;">Analyze your story with Kowalski</p>
                                </div>
                            </div>
                        </button>
                        
                        <button onclick="window.simpleCreator.startAssetSearch()" 
                                style="padding:15px; background:rgba(255,94,0,0.1); border:1px solid rgba(255,94,0,0.3); border-radius:10px; color:#ff5e00; cursor:pointer; text-align:left;">
                            <div style="display:flex; align-items:center; gap:10px;">
                                <i class="fas fa-search" style="font-size:20px;"></i>
                                <div>
                                    <h4 style="margin:0;">Asset Search</h4>
                                    <p style="margin:5px 0 0 0; font-size:14px; color:#aaa;">Search for assets with Skipper</p>
                                </div>
                            </div>
                        </button>
                        
                        <div style="padding:15px; background:rgba(255,94,0,0.05); border:1px solid rgba(255,94,0,0.2); border-radius:10px;">
                            <h4 style="margin:0 0 10px 0; color:#ff5e00;">Quick Assets</h4>
                            <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:10px;">
                                <button onclick="window.simpleCreator.quickSearch('fantasy forest')" 
                                        style="padding:10px; background:rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.1); border-radius:6px; color:#aaa; cursor:pointer;">
                                    🌳 Fantasy
                                </button>
                                <button onclick="window.simpleCreator.quickSearch('sci-fi city')" 
                                        style="padding:10px; background:rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.1); border-radius:6px; color:#aaa; cursor:pointer;">
                                    🚀 Sci-Fi
                                </button>
                                <button onclick="window.simpleCreator.quickSearch('romantic sunset')" 
                                        style="padding:10px; background:rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.1); border-radius:6px; color:#aaa; cursor:pointer;">
                                    💖 Romance
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        this.showSimpleModal('🤖 Agent Tools', modalHTML);
    }

    showSimpleModal(title, content) {
        // Remove any existing modal
        this.hideModal();
        
        // Create modal
        const modalHTML = `
            <div id="simpleModal" style="position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.8); display:flex; align-items:center; justify-content:center; z-index:1000;">
                <div style="background:#1e1e2e; border:1px solid #ff5e00; border-radius:20px; width:90%; max-width:500px; max-height:80vh; overflow-y:auto;">
                    <div style="padding:20px; border-bottom:1px solid rgba(255,94,0,0.3); display:flex; justify-content:space-between; align-items:center;">
                        <h3 style="margin:0; color:#ff5e00;"><i class="fas fa-robot"></i> ${title}</h3>
                        <button onclick="window.simpleCreator.hideModal()" style="background:none; border:none; color:#aaa; font-size:24px; cursor:pointer;">&times;</button>
                    </div>
                    <div style="padding:20px;">
                        ${content}
                    </div>
                </div>
            </div>
        `;
        
        const modalDiv = document.createElement('div');
        modalDiv.innerHTML = modalHTML;
        document.body.appendChild(modalDiv);
    }

    hideModal() {
        const modal = document.getElementById('simpleModal');
        if (modal) modal.remove();
    }

    // Agent functions
    startStoryAnalysis() {
        this.showNotification('Starting story analysis with Kowalski...', 'info');
        
        // Simple prompt for story
        setTimeout(() => {
            const story = prompt('Describe your story for analysis:\n\nExample: "A fantasy adventure with dragons and magic"', 'A young wizard discovers a magical forest');
            
            if (story) {
                this.showNotification(`🔬 Analyzing: "${story.substring(0, 50)}..."`, 'info');
                
                // Try to call the API
                fetch('/api/agents/analyze', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({prompt: story})
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        this.showNotification('✅ Analysis complete! Check console for details.', 'success');
                        console.log('Analysis results:', data);
                    } else {
                        this.showNotification('⚠️ Analysis failed - using demo mode', 'warning');
                        this.showDemoAnalysis(story);
                    }
                })
                .catch(error => {
                    console.error('API error:', error);
                    this.showNotification('⚠️ Using demo analysis mode', 'warning');
                    this.showDemoAnalysis(story);
                });
            }
        }, 500);
    }

    showDemoAnalysis(story) {
        const analysis = {
            genre: 'FANTASY',
            tone: 'ADVENTUROUS',
            character_count: 3,
            location_count: 2,
            complexity_score: 6.5,
            required_assets: [
                {type: 'background', query: 'magical forest', priority: 'HIGH'},
                {type: 'character', query: 'young wizard', priority: 'HIGH'},
                {type: 'background', query: 'ancient castle', priority: 'MEDIUM'}
            ]
        };
        
        const modalHTML = `
            <div style="background:rgba(0,180,216,0.1); padding:15px; border-radius:10px; margin-bottom:20px;">
                <h4 style="color:#00b4d8; margin-top:0;">🔬 Analysis Results</h4>
                <p><strong>Story:</strong> "${story.substring(0, 100)}..."</p>
                <p><strong>Genre:</strong> ${analysis.genre}</p>
                <p><strong>Tone:</strong> ${analysis.tone}</p>
                <p><strong>Characters:</strong> ${analysis.character_count} estimated</p>
                <p><strong>Locations:</strong> ${analysis.location_count} needed</p>
                <div style="margin-top:15px; padding-top:15px; border-top:1px solid rgba(255,255,255,0.1)">
                    <h5>📦 Required Assets:</h5>
                    <ul style="margin:10px 0; padding-left:20px;">
                        ${analysis.required_assets.map(asset => 
                            `<li><span style="color:#ff5e00">${asset.type}:</span> ${asset.query} (${asset.priority})</li>`
                        ).join('')}
                    </ul>
                </div>
            </div>
            <button onclick="window.simpleCreator.startAssetSearch()" 
                    style="width:100%; padding:12px; background:#ff5e00; color:white; border:none; border-radius:8px; cursor:pointer; font-weight:bold;">
                <i class="fas fa-search"></i> Search for These Assets
            </button>
        `;
        
        this.showSimpleModal('Analysis Results', modalHTML);
    }

    startAssetSearch() {
        this.showNotification('Starting asset search with Skipper...', 'info');
        
        setTimeout(() => {
            const query = prompt('What assets are you looking for?\n\nExamples: fantasy castle, sci-fi character', 'fantasy forest');
            
            if (query) {
                const category = prompt('Category? (backgrounds, characters, ui)', 'backgrounds') || 'backgrounds';
                
                this.showNotification(`🔍 Searching for ${category}: ${query}`, 'info');
                
                // Try API
                fetch('/api/agents/search', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        query: query,
                        category: category,
                        limit: 3
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        const count = data.results?.length || 0;
                        this.showNotification(`✅ Found ${count} assets!`, 'success');
                        this.showAssetResults(data.results || [], query);
                    } else {
                        this.showNotification('⚠️ Search failed - showing demo results', 'warning');
                        this.showDemoAssets(query, category);
                    }
                })
                .catch(error => {
                    console.error('API error:', error);
                    this.showNotification('⚠️ Using demo search mode', 'warning');
                    this.showDemoAssets(query, category);
                });
            }
        }, 500);
    }

    showDemoAssets(query, category) {
        const demoAssets = [
            {
                id: 'demo_1',
                query: query,
                category: category,
                description: `A beautiful ${query} ${category} for your visual novel`,
                filename: 'demo_asset_1.png'
            },
            {
                id: 'demo_2', 
                query: query,
                category: category,
                description: `Another ${query} asset perfect for ${category}`,
                filename: 'demo_asset_2.png'
            }
        ];
        
        this.showAssetResults(demoAssets, query);
    }

    showAssetResults(assets, query) {
        let assetsHTML = `
            <div style="margin-bottom:20px;">
                <p>🐧 Skipper found ${assets.length} assets for: <strong>${query}</strong></p>
            </div>
        `;
        
        assets.forEach((asset, index) => {
            assetsHTML += `
                <div style="background:rgba(255,255,255,0.05); border:1px solid rgba(255,94,0,0.3); border-radius:10px; padding:15px; margin-bottom:10px;">
                    <div style="display:flex; align-items:center; gap:10px; margin-bottom:10px;">
                        <div style="width:60px; height:60px; background:rgba(255,94,0,0.1); border-radius:8px; display:flex; align-items:center; justify-content:center;">
                            <i class="fas fa-image" style="color:#ff5e00; font-size:24px;"></i>
                        </div>
                        <div>
                            <h4 style="margin:0; color:#ff5e00">${asset.query || 'Asset'}</h4>
                            <div style="display:flex; gap:10px; font-size:12px; color:#aaa;">
                                <span>${asset.category || 'asset'}</span>
                                <span>#${index + 1}</span>
                            </div>
                        </div>
                    </div>
                    <p style="font-size:14px; color:#ccc; margin:10px 0;">${asset.description || 'Visual novel asset'}</p>
                    <button onclick="window.simpleCreator.useAsset(${index})" 
                            style="padding:8px 15px; background:rgba(255,94,0,0.1); border:1px solid rgba(255,94,0,0.3); border-radius:6px; color:#ff5e00; cursor:pointer;">
                        <i class="fas fa-plus"></i> Use in Project
                    </button>
                </div>
            `;
        });
        
        assetsHTML += `
            <div style="margin-top:20px;">
                <button onclick="window.simpleCreator.startAssetSearch()" 
                        style="width:100%; padding:12px; background:rgba(255,94,0,0.1); border:1px solid rgba(255,94,0,0.3); border-radius:8px; color:#ff5e00; cursor:pointer;">
                    <i class="fas fa-search"></i> Search Again
                </button>
            </div>
        `;
        
        this.showSimpleModal('Found Assets', assetsHTML);
    }

    quickSearch(query) {
        this.showNotification(`Quick search: ${query}`, 'info');
        this.startAssetSearch(query);
    }

    useAsset(index) {
        this.showNotification(`✅ Asset #${index + 1} added to project!`, 'success');
        this.hideModal();
    }

    openProject(projectId, projectName) {
        this.showNotification(`📂 Opening project: ${projectName}`, 'info');
        
        // Create simple dashboard
        const dashboardHTML = `
            <div style="text-align:center; padding:40px 20px;">
                <h2 style="color:#ff5e00;"><i class="fas fa-folder-open"></i> ${projectName}</h2>
                <p>Project dashboard for: <strong>${projectName}</strong></p>
                
                <div style="display:flex; justify-content:center; gap:20px; margin:30px 0;">
                    <div style="background:rgba(0,180,216,0.1); padding:20px; border-radius:10px; min-width:120px;">
                        <div style="font-size:32px; color:#00b4d8;">0</div>
                        <div style="color:#aaa; font-size:14px;">Characters</div>
                    </div>
                    <div style="background:rgba(255,94,0,0.1); padding:20px; border-radius:10px; min-width:120px;">
                        <div style="font-size:32px; color:#ff5e00;">0</div>
                        <div style="color:#aaa; font-size:14px;">Scenes</div>
                    </div>
                    <div style="background:rgba(46,204,113,0.1); padding:20px; border-radius:10px; min-width:120px;">
                        <div style="font-size:32px; color:#2ecc71;">2</div>
                        <div style="color:#aaa; font-size:14px;">Agents</div>
                    </div>
                </div>
                
                <div style="margin:30px 0;">
                    <button onclick="window.simpleCreator.showAgentToolsModal()" 
                            style="padding:15px 30px; background:#ff5e00; color:white; border:none; border-radius:10px; font-size:16px; font-weight:bold; cursor:pointer;">
                        <i class="fas fa-robot"></i> Open Agent Tools
                    </button>
                </div>
                
                <div style="background:rgba(255,255,255,0.05); border-radius:10px; padding:20px; margin-top:30px;">
                    <h3 style="color:#ff5e00; margin-top:0;">Project Dashboard</h3>
                    <p>Welcome to your project! From here you can:</p>
                    <ul style="text-align:left; margin:15px 0; padding-left:20px;">
                        <li>Use Agent Tools for story analysis</li>
                        <li>Search for assets with Skipper</li>
                        <li>Create characters and scenes</li>
                        <li>Export your visual novel</li>
                    </ul>
                </div>
            </div>
        `;
        
        this.showSimpleModal(`Project: ${projectName}`, dashboardHTML);
    }

    showNotification(message, type = 'info') {
        // Create notification element
        let notification = document.getElementById('simpleNotification');
        if (!notification) {
            notification = document.createElement('div');
            notification.id = 'simpleNotification';
            notification.style.cssText = `
                position: fixed;
                bottom: 20px;
                right: 20px;
                padding: 15px 20px;
                background: #1e1e2e;
                border: 1px solid #ff5e00;
                border-radius: 10px;
                display: flex;
                align-items: center;
                gap: 10px;
                z-index: 1000;
                transform: translateX(100px);
                opacity: 0;
                transition: all 0.3s ease;
            `;
            document.body.appendChild(notification);
        }
        
        // Set color based on type
        let borderColor = '#ff5e00';
        let icon = 'fas fa-info-circle';
        
        switch(type) {
            case 'success':
                borderColor = '#2ecc71';
                icon = 'fas fa-check-circle';
                break;
            case 'error':
                borderColor = '#e74c3c';
                icon = 'fas fa-exclamation-circle';
                break;
            case 'warning':
                borderColor = '#f39c12';
                icon = 'fas fa-exclamation-triangle';
                break;
        }
        
        notification.style.borderColor = borderColor;
        notification.innerHTML = `
            <i class="${icon}" style="color:${borderColor};"></i>
            <span>${message}</span>
        `;
        
        // Show
        notification.style.transform = 'translateX(0)';
        notification.style.opacity = '1';
        
        // Auto-hide
        setTimeout(() => {
            notification.style.transform = 'translateX(100px)';
            notification.style.opacity = '0';
        }, 3000);
    }
}

// Initialize when page loads
window.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Starting Simple Creator Tool...');
    window.simpleCreator = new SimpleCreatorTool();
});

// Make sure loading screen hides even if JS has issues
setTimeout(() => {
    const loadingScreen = document.querySelector('.loading-screen');
    if (loadingScreen && loadingScreen.style.display !== 'none') {
        loadingScreen.style.opacity = '0';
        setTimeout(() => {
            loadingScreen.style.display = 'none';
        }, 300);
        console.log('⏱️ Forced loading screen hide');
    }
}, 3000);