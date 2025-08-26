const API_BASE = 'http://localhost:8000';

let providers = [];
let lastResponse = null;

// Initialize page
document.addEventListener('DOMContentLoaded', () => {
    checkHealth();
    loadProviders();
    
    document.getElementById('generateForm').addEventListener('submit', handleGenerate);
    document.getElementById('healthCheckBtn').addEventListener('click', checkHealth);
});

async function handleGenerate(e) {
    e.preventDefault();
    
    const prompt = document.getElementById('prompt').value;
    const maxTokens = parseInt(document.getElementById('maxTokens').value);
    const temperature = parseFloat(document.getElementById('temperature').value);
    
    if (!prompt.trim()) {
        alert('Please enter a prompt');
        return;
    }

    setLoading(true);
    
    try {
        const response = await fetch(`${API_BASE}/api/generate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                prompt: prompt.trim(),
                options: {
                    max_tokens: maxTokens,
                    temperature: temperature
                }
            })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail?.error || `HTTP ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();
        displayResponse(data);
        checkHealth(); // Refresh provider status
        
    } catch (error) {
        displayError(error.message);
    } finally {
        setLoading(false);
    }
}

async function checkHealth() {
    try {
        const response = await fetch(`${API_BASE}/health`);
        const data = await response.json();
        
        updateSystemStatus(data.status === 'healthy');
        updateProviderStatus(data.providers || []);
        
    } catch (error) {
        updateSystemStatus(false);
        console.error('Health check failed:', error);
    }
}

async function loadProviders() {
    try {
        const response = await fetch(`${API_BASE}/api/providers`);
        const data = await response.json();
        providers = data.providers || [];
    } catch (error) {
        console.error('Failed to load providers:', error);
    }
}

function displayResponse(data) {
    lastResponse = data;
    
    document.getElementById('response').textContent = data.content;
    
    const metadata = document.getElementById('metadata');
    metadata.style.display = 'grid';
    metadata.innerHTML = `
        <div class="metadata-item">
            <div class="metadata-label">Provider</div>
            <div class="metadata-value">${data.provider}</div>
        </div>
        <div class="metadata-item">
            <div class="metadata-label">Model</div>
            <div class="metadata-value">${data.model}</div>
        </div>
        <div class="metadata-item">
            <div class="metadata-label">Tokens Used</div>
            <div class="metadata-value">${data.tokens_used}</div>
        </div>
        <div class="metadata-item">
            <div class="metadata-label">Response Time</div>
            <div class="metadata-value">${data.response_time}ms</div>
        </div>
    `;
}

function displayError(message) {
    document.getElementById('response').textContent = `Error: ${message}`;
    document.getElementById('metadata').style.display = 'none';
}

function updateSystemStatus(isHealthy) {
    const statusElement = document.getElementById('systemStatus');
    statusElement.textContent = isHealthy ? 'System Online' : 'System Issues';
    statusElement.className = `status-badge ${isHealthy ? 'status-healthy' : 'status-error'}`;
}

function updateProviderStatus(providerHealthData) {
    const statusContainer = document.getElementById('providerStatus');
    
    if (!providerHealthData.length) {
        statusContainer.innerHTML = '<div class="provider-card"><div class="provider-name">No providers available</div></div>';
        return;
    }

    statusContainer.innerHTML = providerHealthData.map(provider => `
        <div class="provider-card">
            <div class="provider-name">
                ${provider.provider.charAt(0).toUpperCase() + provider.provider.slice(1)}
                <span class="status-badge ${provider.is_healthy ? 'status-healthy' : 'status-error'}" style="float: right; font-size: 0.8rem;">
                    ${provider.is_healthy ? 'Healthy' : 'Unhealthy'}
                </span>
            </div>
            <div class="provider-details">
                Last checked: ${new Date(provider.last_checked * 1000).toLocaleTimeString()}<br>
                ${provider.response_time ? `Response time: ${provider.response_time}ms<br>` : ''}
                Error count: ${provider.error_count}
            </div>
        </div>
    `).join('');
}

function setLoading(loading) {
    const loadingElement = document.getElementById('loading');
    const generateBtn = document.getElementById('generateBtn');
    
    loadingElement.style.display = loading ? 'block' : 'none';
    generateBtn.disabled = loading;
    generateBtn.textContent = loading ? 'Generating...' : 'Generate Text';
}
