/**
 * AgriCare Assistant - Frontend Logic
 * Version: 2.0 (High Precision)
 */

// DOM Elements
const chatbox = document.getElementById('chatbox');
const userInput = document.getElementById('user-input');
const imageUpload = document.getElementById('image-upload');


/**
 * Adds a message bubble to the chat interface.
 */
function addMessage(content, isUser = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.innerHTML = content;
    
    const timeDiv = document.createElement('div');
    timeDiv.className = 'message-time';
    timeDiv.textContent = getCurrentTime();
    
    messageDiv.appendChild(contentDiv);
    messageDiv.appendChild(timeDiv);
    chatbox.appendChild(messageDiv);
    
    // Auto-scroll to the newest message
    chatbox.scrollTop = chatbox.scrollHeight;
}

/**
 * Transforms the raw JSON response from Flask into a clean, 
 * readable diagnostic report for the farmer.
 */
function formatDiagnosisResponse(response) {
    // 1. Handle casual chat or plant-clarification requests
    if (response.is_casual) {
        return `<div class="casual-response">${response.message}</div>`;
    }
    
    // 2. Handle server or logic errors
    if (response.error) {
        return `<div class="error-msg"><i class="fas fa-exclamation-circle"></i> Error: ${response.error}</div>`;
    }
    
    // 3. Handle data gaps
    if (!response.disease || response.disease === "Unknown") {
        return `I couldn't identify a specific disease from that description. Could you please provide more details like the color of the spots or if the leaves are wilting?`;
    }
    
    // 4. Return the Professional Diagnosis Card
    return `
        <div class="diagnosis-card">
            <div class="card-header">
                <i class="fas fa-leaf"></i>
                <strong>DIAGNOSIS: ${response.disease}</strong>
            </div>
            <div class="card-body">
                <div class="treatment-section">
                    <strong><i class="fas fa-seedling text-success"></i> Organic Treatment</strong>
                    <p>${response.organic}</p>
                </div>
                <div class="treatment-section">
                    <strong><i class="fas fa-flask text-primary"></i> Chemical Treatment</strong>
                    <p>${response.chemical}</p>
                </div>
                <div class="treatment-section">
                    <strong><i class="fas fa-shield-alt text-warning"></i> Prevention</strong>
                    <p>${response.prevention}</p>
                </div>
            </div>
            <div class="card-footer">
                <small>${response.source}</small>
            </div>
        </div>
    `;
}

/**
 * Utility: Gets current time for message timestamps
 */
function getCurrentTime() {
    const now = new Date();
    return now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

/**
 * UI: Shows the "Typing..." dots while waiting for the server
 */
function showTyping() {
    const typingDiv = document.createElement('div');
    typingDiv.className = 'message bot-message';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content typing-indicator';
    contentDiv.innerHTML = `
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
    `;
    
    typingDiv.appendChild(contentDiv);
    chatbox.appendChild(typingDiv);
    chatbox.scrollTop = chatbox.scrollHeight;
    
    return typingDiv;
}

/**
 * Main Logic: Sends user text to the Python backend
 */
async function handleSubmit() {
    const text = userInput.value.trim();
    if (!text) return;
    
    // Display user's message and clear input
    addMessage(text, true);
    userInput.value = '';
    
    const typingElement = showTyping();
    
    try {
        const response = await fetch('http://localhost:5000/api/analyze-symptoms',{
        // const response = await fetch('/api/analyze-symptoms', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ symptoms: text }),
        });
        
        const data = await response.json();
        
        // Remove typing indicator once data arrives
        if (typingElement.parentNode) {
            chatbox.removeChild(typingElement);
        }
        
        if (!response.ok) {
            throw new Error(data.error || 'The server is not responding.');
        }
        
        // Format and show the final response
        const messageContent = formatDiagnosisResponse(data);
        addMessage(messageContent);

    } catch (error) {
        console.error("Connection Error:", error);
        if (typingElement.parentNode) {
            chatbox.removeChild(typingElement);
        }
        addMessage(`<div class="error-msg">I'm having trouble connecting to the server. Please check if your Flask app is running.</div>`);
    }
}

/**
 * Future: Handle Image Uploads
 */
function handleImageUpload() {
    const file = imageUpload.files[0];
    if (!file) {
        alert('Please select an image first');
        return;
    }
    
    addMessage(`<i class="fas fa-image"></i> Analyzing photo: <strong>${file.name}</strong>`, true);
    const typingElement = showTyping();
    
    setTimeout(() => {
        chatbox.removeChild(typingElement);
        addMessage("Visual diagnosis is being optimized. For now, please describe the symptoms (e.g., 'Rice with brown spots').");
    }, 2000);
}

// Event Listeners
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') handleSubmit();
});



