/**
 * AgriCare Assistant — Frontend Logic
 * Version: 3.0 (All Fixes Applied)
 */

// DOM Elements
const chatbox = document.getElementById('chatbox');
const userInput = document.getElementById('user-input');
const imageUpload = document.getElementById('image-upload');

// ============================================================
// FIX #5 (SECURITY): HTML sanitizer — strips all tags from
// user input before it ever touches innerHTML.
// ============================================================
function sanitizeHTML(str) {
    const div = document.createElement('div');
    div.appendChild(document.createTextNode(str));
    return div.innerHTML;
}

/**
 * Adds a message bubble to the chat interface.
 * isUser = true  → text is plain (sanitized), displayed as-is
 * isUser = false → HTML is from our own code (trusted), rendered directly
 */
function addMessage(content, isUser = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';

    if (isUser) {
        // FIX #5: sanitize user-supplied text — never use innerHTML for user input
        contentDiv.textContent = content;
    } else {
        // Bot responses come from our own formatting functions — safe to use innerHTML
        contentDiv.innerHTML = content;
    }

    const timeDiv = document.createElement('div');
    timeDiv.className = 'message-time';
    timeDiv.textContent = getCurrentTime();

    messageDiv.appendChild(contentDiv);
    messageDiv.appendChild(timeDiv);
    chatbox.appendChild(messageDiv);
    chatbox.scrollTop = chatbox.scrollHeight;
}

/**
 * FIX #2: Strips residual citation markers [1], [1,3,5] that may
 * still slip through from older DB entries.
 */
function stripCitations(text) {
    if (!text) return '';
    return text.replace(/\[\s*\d+(?:\s*,\s*\d+)*\s*\]/g, '').trim();
}

/**
 * Transforms the JSON response from Flask into a clean diagnosis card.
 */
function formatDiagnosisResponse(response) {
    // Casual chat / clarification
    if (response.is_casual) {
        return `<div class="casual-response">${response.message}</div>`;
    }

    // Server / logic error
    if (response.error) {
        return `<div class="error-msg"><i class="fas fa-exclamation-circle"></i> ${sanitizeHTML(response.error)}</div>`;
    }

    if (!response.disease || response.disease === 'Unknown') {
        return `I couldn't identify a specific disease. Could you describe the symptoms in more detail?`;
    }

    // FIX #2: strip any remaining citations from every field
    const disease    = stripCitations(response.disease);
    const organic    = stripCitations(response.organic);
    const chemical   = stripCitations(response.chemical);
    const prevention = stripCitations(response.prevention);
    const source     = stripCitations(response.source);

    return `
        <div class="diagnosis-card">
            <div class="card-header">
                <i class="fas fa-leaf"></i>
                <strong>DIAGNOSIS: ${disease}</strong>
            </div>
            <div class="card-body">
                <div class="treatment-section">
                    <strong><i class="fas fa-seedling text-success"></i> Organic Treatment</strong>
                    <p>${organic}</p>
                </div>
                <div class="treatment-section">
                    <strong><i class="fas fa-flask text-primary"></i> Chemical Treatment</strong>
                    <p>${chemical}</p>
                </div>
                <div class="treatment-section">
                    <strong><i class="fas fa-shield-alt text-warning"></i> Prevention</strong>
                    <p>${prevention}</p>
                </div>
            </div>
            <div class="card-footer">
                <small><i class="fas fa-database"></i> ${source}</small>
            </div>
        </div>
    `;
}

function getCurrentTime() {
    return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

/** Shows the animated "Typing…" dots */
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

/** Safely removes a typing/loading element from the chat */
function removeElement(el) {
    if (el && el.parentNode) el.parentNode.removeChild(el);
}

// ============================================================
// Text submit
// ============================================================
async function handleSubmit() {
    const text = userInput.value.trim();
    if (!text) return;

    addMessage(text, true);   // user bubble — plain text, sanitized
    userInput.value = '';

    const typingElement = showTyping();

    try {
        const response = await fetch('http://localhost:5000/api/analyze-symptoms', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            // FIX #5: send raw text to backend which sanitizes with markupsafe
            body: JSON.stringify({ symptoms: text }),
        });

        const data = await response.json();
        removeElement(typingElement);

        if (!response.ok) {
            throw new Error(data.error || 'The server returned an error.');
        }

        addMessage(formatDiagnosisResponse(data));

    } catch (error) {
        console.error('Connection Error:', error);
        removeElement(typingElement);
        addMessage(`<div class="error-msg"><i class="fas fa-wifi"></i> I'm having trouble connecting. Please check your Flask server is running.</div>`);
    }
}

// ============================================================
// FIX #1 + FIX #3: Image upload with preview & loading spinner
// ============================================================-------------------------
// imageUpload.addEventListener('change', function () {
//     const file = this.files[0];
//     if (!file) return;

//     // Show image preview in chat immediately after selection
//     const reader = new FileReader();
//     reader.onload = function (e) {
//         const previewHTML = `
//             <div class="img-preview-wrapper">
//                 <img src="${e.target.result}" alt="Uploaded crop photo" class="img-preview" />
//                 <span class="img-preview-label"><i class="fas fa-image"></i> ${sanitizeHTML(file.name)}</span>
//             </div>
//         `;
//         addMessage(previewHTML, false);
//     };
//     reader.readAsDataURL(file);

//     // Update upload chip: show filename + ✕ cancel button
//     const uploadLabel = document.getElementById('upload-label');
//     if (uploadLabel) {
//         uploadLabel.innerHTML = `
//             <i class="fas fa-check-circle"></i>
//             <span class="chip-filename">${sanitizeHTML(file.name)}</span>
//             <span class="chip-cancel" id="chip-cancel-btn" title="Remove image">✕</span>
//         `;
//         uploadLabel.classList.add('file-selected');

//         // Cancel button — clears the file selection
//         document.getElementById('chip-cancel-btn').addEventListener('click', function (e) {
//             e.preventDefault();   // don't open the file picker
//             e.stopPropagation();  // don't bubble up to the label
//             clearImageSelection();
//         });
//     }
// });
//---------------------------------------------new image upload handler with async logic and better UX feedback---------------------------
// Inline preview elements
const inlinePreview = document.getElementById('inline-preview');
const inlinePreviewImg = document.getElementById('inline-preview-img');
const inlinePreviewName = document.getElementById('inline-preview-name');
const inlinePreviewRemove = document.getElementById('inline-preview-remove');

// ============================================================
// FIXED: Image upload preview shown near input, NOT in chat
// ============================================================
imageUpload.addEventListener('change', function () {
    const file = this.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = function (e) {
        // Show small preview beside upload button
        inlinePreviewImg.src = e.target.result;
        inlinePreviewName.textContent = file.name;
        inlinePreview.classList.remove('hidden');
    };
    reader.readAsDataURL(file);

    // Keep upload button simple but show selected state
    const uploadLabel = document.getElementById('upload-label');
    if (uploadLabel) {
        uploadLabel.innerHTML = `<i class="fas fa-check-circle"></i> Image Selected`;
        uploadLabel.classList.add('file-selected');
    }
});

// Remove preview + clear file input
if (inlinePreviewRemove) {
    inlinePreviewRemove.addEventListener('click', function (e) {
        e.preventDefault();
        e.stopPropagation();
        clearImageSelection();
    });
}



// ----------------------------------------------------------------------------------------------------------------------------
/** Resets the image input and chip back to the default state */
// function clearImageSelection() {
//     imageUpload.value = '';
//     const uploadLabel = document.getElementById('upload-label');
//     if (uploadLabel) {
//         uploadLabel.innerHTML = `<i class="fas fa-camera"></i> Upload Image`;
//         uploadLabel.classList.remove('file-selected');
//     }
// }
//----------------------------------------------new clear image selection that also hides the inline preview---------------------------

function clearImageSelection() {
    imageUpload.value = '';

    const uploadLabel = document.getElementById('upload-label');
    if (uploadLabel) {
        uploadLabel.innerHTML = `<i class="fas fa-camera"></i> Upload Image`;
        uploadLabel.classList.remove('file-selected');
    }

    // Hide inline preview
    if (inlinePreview) {
        inlinePreview.classList.add('hidden');
    }

    if (inlinePreviewImg) {
        inlinePreviewImg.src = '';
    }

    if (inlinePreviewName) {
        inlinePreviewName.textContent = '';
    }
}


//--------------------------------------------------------------------------------------------------------------

// ============================================================
// Toast notification — slides in from the right, auto-dismisses
// Use this for transient errors/warnings instead of chat bubbles
// ============================================================
function showToast(message, type = 'error') {
    // Remove any existing toast first
    const existing = document.getElementById('agri-toast');
    if (existing) existing.remove();

    const icons = {
        error:   'fa-exclamation-circle',
        warning: 'fa-exclamation-triangle',
        info:    'fa-info-circle',
        success: 'fa-check-circle'
    };

    const toast = document.createElement('div');
    toast.id = 'agri-toast';
    toast.className = `agri-toast agri-toast--${type}`;
    toast.innerHTML = `
        <i class="fas ${icons[type] || icons.error}"></i>
        <span>${message}</span>
        <button class="toast-close" onclick="this.parentElement.remove()">✕</button>
    `;
    document.body.appendChild(toast);

    // Trigger slide-in animation on next frame
    requestAnimationFrame(() => toast.classList.add('agri-toast--visible'));

    // Auto-dismiss after 4 seconds
    setTimeout(() => {
        toast.classList.remove('agri-toast--visible');
        setTimeout(() => toast.remove(), 350);
    }, 4000);
}

async function handleImageUpload() {
    const file = imageUpload.files[0];
    if (!file) {
        // Toast instead of in-chat error bubble
        showToast('Please select an image first using the Upload button.', 'warning');
        return;
    }

    // FIX #3: Richer loading spinner with descriptive status steps
    const loadingId = 'loading-' + Date.now();
    const loadingHTML = `
        <div class="loading-card" id="${loadingId}">
            <div class="loading-spinner">
                <div class="spinner-ring"></div>
            </div>
            <div class="loading-steps">
                <div class="loading-step active" id="${loadingId}-step1">
                    <i class="fas fa-upload"></i> Uploading image…
                </div>
                <div class="loading-step" id="${loadingId}-step2">
                    <i class="fas fa-search"></i> Identifying plant species…
                </div>
                <div class="loading-step" id="${loadingId}-step3">
                    <i class="fas fa-microscope"></i> Analysing for diseases…
                </div>
                <div class="loading-step" id="${loadingId}-step4">
                    <i class="fas fa-book-medical"></i> Looking up treatments…
                </div>
            </div>
        </div>
    `;

    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'message bot-message';
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.innerHTML = loadingHTML;
    loadingDiv.appendChild(contentDiv);
    chatbox.appendChild(loadingDiv);
    chatbox.scrollTop = chatbox.scrollHeight;

    // Animate through steps
    const stepTimings = [800, 1800, 3000];
    stepTimings.forEach((delay, i) => {
        setTimeout(() => {
            const prev = document.getElementById(`${loadingId}-step${i + 1}`);
            const next = document.getElementById(`${loadingId}-step${i + 2}`);
            if (prev) prev.classList.remove('active');
            if (next) next.classList.add('active');
        }, delay);
    });

    const formData = new FormData();
    formData.append('image', file);

    try {
        const response = await fetch('http://localhost:5000/api/analyze-image', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();
        removeElement(loadingDiv);

        if (data.error) {
            // Non-plant or API error → toast, not chat bubble
            showToast(data.error, 'error');
        } else {
            addMessage(formatDiagnosisResponse(data));
        }

        // Reset chip back to default
        clearImageSelection();

    } catch (error) {
        removeElement(loadingDiv);
        showToast("Couldn't connect to the analysis server. Please check Flask is running.", 'error');
        console.error(error);
    }
}

// ============================================================
// Event Listeners
// ============================================================
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') handleSubmit();
});

// Hide welcome banner on first real message
document.addEventListener('DOMContentLoaded', function () {
    const chatWelcome = document.querySelector('.chat-welcome');
    const chatMessages = document.querySelector('.chat-messages');
    let hasMessages = false;

    function hideWelcomeOnFirstMessage() {
        const messageCount = chatMessages.querySelectorAll('.message').length;
        if (messageCount > 0 && !hasMessages) {
            hasMessages = true;
            chatWelcome.style.display = 'none';
        }
    }

    const observer = new MutationObserver(function (mutations) {
        let hasNew = false;
        mutations.forEach(function (mutation) {
            if (mutation.type === 'childList') {
                mutation.addedNodes.forEach(function (node) {
                    if (node.nodeType === 1 && (node.classList?.contains('message') || node.querySelector?.('.message'))) {
                        hasNew = true;
                    }
                });
            }
        });
        if (hasNew) hideWelcomeOnFirstMessage();
    });

    observer.observe(chatMessages, { childList: true, subtree: true });

    const sendBtn = document.querySelector('.send-btn');
    if (sendBtn) sendBtn.addEventListener('click', hideWelcomeOnFirstMessage);
});
