/**
 * CyberSafe - Renderer Process (Frontend Logic)
 */

let API_URL = 'http://localhost:5000';
let monitoring = false;
let updateInterval;

// Initialize app
async function init() {
    console.log('Initializing CyberSafe...');
    
    // Get API URL from main process
    if (window.electronAPI) {
        API_URL = await window.electronAPI.getApiUrl();
    }
    
    // Check backend connection
    await checkConnection();
    
    // Hide loading, show app
    document.getElementById('loading').style.display = 'none';
    document.getElementById('app').style.display = 'block';
    
    // Setup event listeners
    setupEventListeners();
    
    // Start updating time
    updateTime();
    setInterval(updateTime, 1000);
    
    console.log('App initialized');
}

// Check backend connection
async function checkConnection() {
    try {
        const response = await fetch(`${API_URL}/api/status`);
        const data = await response.json();
        
        document.getElementById('connection-status').textContent = '🟢 Connected';
        return true;
    } catch (error) {
        document.getElementById('connection-status').textContent = '🔴 Disconnected';
        return false;
    }
}

// Setup event listeners
function setupEventListeners() {
    // Navigation
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const view = btn.dataset.view;
            switchView(view);
        });
    });
    
    // Start/Stop buttons
    document.getElementById('startBtn').addEventListener('click', startMonitoring);
    document.getElementById('stopBtn').addEventListener('click', stopMonitoring);
    
    // Listen for IPC events from main process
    if (window.electronAPI) {
        window.electronAPI.onStartMonitoring(() => startMonitoring());
        window.electronAPI.onStopMonitoring(() => stopMonitoring());
    }
}

// Switch view
function switchView(viewName) {
    document.querySelectorAll('.nav-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.view').forEach(view => view.classList.remove('active'));
    
    document.querySelector(`[data-view="${viewName}"]`).classList.add('active');
    document.getElementById(`${viewName}-view`).classList.add('active');
}

// Start monitoring
async function startMonitoring() {
    try {
        const response = await fetch(`${API_URL}/api/start`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        
        if (response.ok) {
            monitoring = true;
            document.getElementById('startBtn').style.display = 'none';
            document.getElementById('stopBtn').style.display = 'inline-block';
            document.getElementById('status').textContent = '🟢 Monitoring Active';
            
            // Start updating data
            updateInterval = setInterval(updateData, 2000);
            
            addActivity('Monitoring started');
        }
    } catch (error) {
        alert('Failed to start monitoring. Make sure backend is running as Administrator.');
    }
}

// Stop monitoring
async function stopMonitoring() {
    try {
        await fetch(`${API_URL}/api/stop`, { method: 'POST' });
        
        monitoring = false;
        document.getElementById('startBtn').style.display = 'inline-block';
        document.getElementById('stopBtn').style.display = 'none';
        document.getElementById('status').textContent = '⚫ Not Monitoring';
        
        clearInterval(updateInterval);
        
        addActivity('Monitoring stopped');
    } catch (error) {
        console.error('Error stopping:', error);
    }
}

// Update all data
async function updateData() {
    try {
        const [stats, packets, threats, ports] = await Promise.all([
            fetch(`${API_URL}/api/stats`).then(r => r.json()),
            fetch(`${API_URL}/api/packets?count=50`).then(r => r.json()),
            fetch(`${API_URL}/api/threats?count=20`).then(r => r.json()),
            fetch(`${API_URL}/api/ports`).then(r => r.json())
        ]);
        
        updateDashboard(stats);
        updatePackets(packets);
        updateThreats(threats);
        updatePorts(ports);
        
    } catch (error) {
        console.error('Update error:', error);
    }
}

// Update dashboard
function updateDashboard(stats) {
    const capture = stats.capture || {};
    const threats = stats.threats || {};
    const ports = stats.ports || {};
    
    document.getElementById('total-packets').textContent = capture.total_packets || 0;
    document.getElementById('total-threats').textContent = threats.total_threats || 0;
    document.getElementById('active-ports').textContent = ports.listening_ports || 0;
    
    const dataRate = ((capture.bytes_per_second || 0) / 1024).toFixed(2);
    document.getElementById('data-rate').textContent = `${dataRate} KB/s`;
    
    document.getElementById('packet-count').textContent = `Packets: ${capture.total_packets || 0}`;
}

// Update packets table
function updatePackets(packets) {
    const tbody = document.getElementById('packets-tbody');
    tbody.innerHTML = '';
    
    packets.slice(0, 100).forEach(packet => {
        const row = tbody.insertRow();
        row.innerHTML = `
            <td>${packet.number}</td>
            <td>${new Date(packet.timestamp).toLocaleTimeString()}</td>
            <td><span class="protocol-badge">${packet.protocol || 'N/A'}</span></td>
            <td>${packet.src_ip || 'N/A'}</td>
            <td>${packet.dst_ip || 'N/A'}</td>
            <td>${packet.length || 0} bytes</td>
        `;
    });
}

// Update threats
function updateThreats(threats) {
    const list = document.getElementById('threats-list');
    list.innerHTML = '';
    
    if (threats.length === 0) {
        list.innerHTML = '<p style="color: #4CAF50; text-align: center; padding: 40px;">No threats detected. Your network is secure! ✓</p>';
        return;
    }
    
    threats.forEach(threat => {
        const card = document.createElement('div');
        card.className = `threat-card ${threat.severity?.toLowerCase() || 'low'}`;
        card.innerHTML = `
            <div class="threat-header">
                <div class="threat-type">${threat.type || 'Unknown'}</div>
                <div class="threat-severity ${threat.severity?.toLowerCase() || 'low'}">${threat.severity || 'LOW'}</div>
            </div>
            <div class="threat-description">${threat.description || 'No description'}</div>
            <div class="threat-meta" style="margin-top: 10px; font-size: 12px; color: #757575;">
                ${threat.source_ip ? `From: ${threat.source_ip}` : ''} 
                ${threat.timestamp ? `• ${new Date(threat.timestamp).toLocaleString()}` : ''}
            </div>
        `;
        list.appendChild(card);
    });
}

// Update ports
function updatePorts(portsData) {
    const list = document.getElementById('ports-list');
    list.innerHTML = '<h3>Listening Ports</h3>';
    
    const listening = portsData.listening || [];
    if (listening.length === 0) {
        list.innerHTML += '<p>No listening ports detected</p>';
        return;
    }
    
    const table = document.createElement('table');
    table.innerHTML = `
        <thead>
            <tr><th>Port</th><th>Process</th><th>PID</th><th>IP</th></tr>
        </thead>
        <tbody>
            ${listening.slice(0, 50).map(port => `
                <tr>
                    <td>${port.port}</td>
                    <td>${port.process || 'Unknown'}</td>
                    <td>${port.pid || 'N/A'}</td>
                    <td>${port.ip || 'N/A'}</td>
                </tr>
            `).join('')}
        </tbody>
    `;
    list.appendChild(table);
}

// Add activity log
function addActivity(message) {
    const log = document.getElementById('activity-log');
    const item = document.createElement('div');
    item.className = 'activity-item';
    item.textContent = `${new Date().toLocaleTimeString()} - ${message}`;
    log.prepend(item);
    
    // Keep only last 20 items
    while (log.children.length > 20) {
        log.removeChild(log.lastChild);
    }
}

// Update time
function updateTime() {
    document.getElementById('time').textContent = new Date().toLocaleTimeString();
}

// Initialize when ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
