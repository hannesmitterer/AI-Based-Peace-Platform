// euystacio.js

const apiUrl = "https://musk-vs-trump.onrender.com";

// ---- Kernel State ----
async function getKernelState() {
    const trustSpan = document.getElementById('trust');
    const harmonySpan = document.getElementById('harmony');
    const refreshBtn = document.getElementById('refresh-btn');
    if (refreshBtn) refreshBtn.disabled = true;
    try {
        const response = await fetch(`${apiUrl}/api/sacred/status`);
        if (!response.ok) throw new Error(`Status: ${response.status}`);
        const data = await response.json();
        trustSpan.textContent = data.sacred_metrics?.active_vessels ?? '--';
        harmonySpan.textContent = data.sacred_metrics?.harmony_index ?? '--';
    } catch (error) {
        trustSpan.textContent = '--';
        harmonySpan.textContent = '--';
        showStatus('Failed to fetch kernel state.', 'error');
    } finally {
        if (refreshBtn) refreshBtn.disabled = false;
    }
}

// Show status message in a fixed bar or fallback to alert
function showStatus(msg, type = 'info') {
    let bar = document.getElementById('euystacio-status-bar');
    if (!bar) {
        bar = document.createElement('div');
        bar.id = 'euystacio-status-bar';
        bar.style.position = 'fixed';
        bar.style.bottom = '0';
        bar.style.left = '0';
        bar.style.width = '100%';
        bar.style.zIndex = '100';
        bar.style.textAlign = 'center';
        bar.style.fontWeight = 'bold';
        bar.style.padding = '0.7em';
        bar.style.transition = 'opacity 0.3s';
        document.body.appendChild(bar);
    }
    bar.style.background = type === 'error' ? '#ffcccc' : '#e3eafc';
    bar.style.color = type === 'error' ? '#a94442' : '#355c7d';
    bar.textContent = msg;
    bar.style.opacity = '1';
    setTimeout(() => { bar.style.opacity = '0'; }, 3500);
}

// ---- Pulse ----
const pulseForm = document.getElementById('pulse-form');
if (pulseForm) {
    pulseForm.addEventListener('submit', async function (e) {
        e.preventDefault();
        const emotion = document.getElementById('emotion').value;
        const context = document.getElementById('context').value;
        const feedback = document.getElementById('pulse-feedback');
        const btn = pulseForm.querySelector('button[type="submit"]');
        feedback.textContent = 'Sending...';
        btn.disabled = true;
        try {
            const response = await fetch(`${apiUrl}/api/bridge/pulse`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ pulse: { emotion, context } })
            });
            if (!response.ok) throw new Error('Failed to send pulse.');
            feedback.textContent = 'Pulse sent successfully!';
            getKernelState();
        } catch (err) {
            feedback.textContent = 'Failed to send pulse.';
            showStatus('Pulse sending failed.', 'error');
        } finally {
            btn.disabled = false;
            setTimeout(() => { feedback.textContent = ''; }, 2000);
        }
    });
}

// ---- Chat ----
const chatLog = document.getElementById('chat-log');
const chatForm = document.getElementById('chat-form');
const chatInput = document.getElementById('chat-input');

function appendChatMessage(text, sender = 'user') {
    const msg = document.createElement('div');
    msg.className = 'chat-msg ' + sender;
    msg.textContent = text;
    chatLog.appendChild(msg);
    chatLog.scrollTop = chatLog.scrollHeight;
}

if (chatForm) {
    chatForm.addEventListener('submit', async function (e) {
        e.preventDefault();
        const msg = chatInput.value.trim();
        if (!msg) return;
        appendChatMessage(msg, 'user');
        chatInput.value = '';
        chatInput.disabled = true;
        chatForm.querySelector('button[type="submit"]').disabled = true;
        try {
            const response = await fetch(`${apiUrl}/api/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: msg })
            });
            if (!response.ok) throw new Error('No response');
            const data = await response.json();
            appendChatMessage(data.reply || '[AI did not reply]', 'ai');
        } catch (err) {
            appendChatMessage('[AI unavailable]', 'ai');
            showStatus('AI chat unavailable.', 'error');
        } finally {
            chatInput.disabled = false;
            chatForm.querySelector('button[type="submit"]').disabled = false;
        }
    });
}

// ---- Initialization ----
document.addEventListener('DOMContentLoaded', function () {
    getKernelState();
    document.getElementById('refresh-btn')?.addEventListener('click', (e) => {
        e.preventDefault();
        getKernelState();
    });
    // Poll kernel state every 10 seconds
    setInterval(getKernelState, 10000);
});