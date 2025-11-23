const API_URL = "http://127.0.0.1:8000";
let sessionId = null;
let currentAudio = null;
let recognition = null;
let recognizing = false;
let interviewEnded = false;
let userHasTurnedMicOff = false;
let isAgentSpeaking = false; // Prevents self-transcription loop

// Voice input logic
let voiceTranscript = "";
let silenceTimer = null;
const SILENCE_INTERVAL = 3000; // 5 seconds wait time

// ====== START INTERVIEW ======
async function startInterview() {
    const role = document.getElementById('role-input').value.trim();
    if (!role) {
        alert("Please enter a role!");
        return;
    }
    const startBtn = document.querySelector('#setup-panel button');
    startBtn.innerText = "Starting...";
    startBtn.disabled = true;
    try {
        const response = await fetch(`${API_URL}/start_interview`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ role })
        });
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();
        sessionId = data.session_id;
        document.getElementById('setup-panel').classList.add('hidden');
        document.getElementById('chat-panel').classList.remove('hidden');
        addMessage(data.message, "bot");
        if (data.audio) playAudio(data.audio);
    } catch (err) {
        console.error("Start interview error:", err);
        alert("Error connecting to backend. Is it running?");
    } finally {
        startBtn.innerText = "Start Interview";
        startBtn.disabled = false;
    }
}

// ====== SEND TEXT MESSAGE ======
async function sendMessage() {
    const input = document.getElementById("user-message");
    const message = input.value.trim();
    if (!message) return;
    addMessage(message, "user");
    input.value = "";
    try {
        const response = await fetch(`${API_URL}/chat`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ session_id: sessionId, message })
        });
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();
        addMessage(data.message, "bot");
        if (data.audio) playAudio(data.audio);
    } catch (err) {
        console.error("Chat error:", err);
        addMessage("Error: Could not reach AI.", "bot");
    }
}

// ====== END INTERVIEW (FEEDBACK) ======
async function endInterview() {
    interviewEnded = true;
    userHasTurnedMicOff = true;
    if (recognition && recognizing) {
        recognition.stop();
    }
    clearTimer();
    if (!confirm("Are you sure you want to end the interview and get feedback?")) return;
    addMessage("Generating feedback...", "bot");
    try {
        const response = await fetch(`${API_URL}/end_interview`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ session_id: sessionId })
        });
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();
        addMessage("INTERVIEW FEEDBACK:\n" + data.feedback, "bot");
        document.querySelector(".input-area").style.display = "none";
    } catch (err) {
        console.error("End interview error:", err);
        addMessage("Error generating feedback.", "bot");
    }
}

// ====== UI HELPER ======
function addMessage(text, sender) {
    const chatBox = document.getElementById("chat-box");
    const div = document.createElement("div");
    div.className = `message ${sender === "bot" ? "bot-msg" : "user-msg"}`;
    
    // FIX: Use innerHTML for bot to render HTML feedback properly
    if (sender === "bot") {
        div.innerHTML = text;
    } else {
        div.innerText = text; 
    }

    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function handleEnter(event) {
    if (event.key === "Enter") sendMessage();
}

// ====== AUDIO PLAYBACK (TTS OUTPUT) ======
function playAudio(base64Audio) {
    if (!base64Audio) return;
    
    // 1. Flag Agent as Speaking to block mic input
    isAgentSpeaking = true;

    // 2. Stop listening to prevent self-transcription feedback loop
    if (recognition && recognizing) {
        recognition.stop();
    }

    // 3. Manage current audio
    if (currentAudio && !currentAudio.paused) {
        currentAudio.pause();
        currentAudio.currentTime = 0;
    }
    currentAudio = new Audio("data:audio/mp3;base64," + base64Audio);
    
    // FIX: Play faster (1.15x speed)
    currentAudio.playbackRate = 1.35; 

    currentAudio.onended = () => {
        // 4. Resume listening immediately after agent finishes
        isAgentSpeaking = false;
        if (!interviewEnded && !userHasTurnedMicOff) {
            try { recognition.start(); } catch(e) { /* Throttle safe */ }
        }
    };
    
    currentAudio.play().catch(err => console.error("Audio play error:", err));
}

// ====== CONTINUOUS VOICE MODE ======
function toggleVoiceMode() {
    if (!window.SpeechRecognition && !window.webkitSpeechRecognition) {
        alert("Voice mode only works on Chrome and Edge browsers.");
        return;
    }
    if (!recognition) {
        window.SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognition = new SpeechRecognition();
        recognition.lang = 'en-US';
        recognition.continuous = true;
        recognition.interimResults = true;
        recognition.maxAlternatives = 1;

        recognition.onstart = () => {
            recognizing = true;
            userHasTurnedMicOff = false;
            interviewEnded = false;
            voiceTranscript = "";
            document.getElementById('mic-btn').classList.add('recording');
            document.getElementById('mic-btn').textContent = "Mic ON";
        };

        recognition.onresult = function(event) {
            // FIX: If agent is speaking, interrupt it immediately when you speak
            if (currentAudio && !currentAudio.paused && !currentAudio.ended) {
                 currentAudio.pause();
                 currentAudio.currentTime = 0;
                 isAgentSpeaking = false; // Reset flag so we can listen to user
            }

            // Prevent recording agent's own voice if flag is somehow still true
            if (isAgentSpeaking) return;

            for (let i = event.resultIndex; i < event.results.length; ++i) {
                if (event.results[i].isFinal) {
                    voiceTranscript += event.results[i][0].transcript + " ";
                }
            }
            resetSilenceTimer();
        };

        recognition.onerror = function(event) {
            console.error('Speech recognition error:', event.error);
        };

        recognition.onend = () => {
            recognizing = false;
            document.getElementById('mic-btn').classList.remove('recording');
            document.getElementById('mic-btn').textContent = "Mic OFF";
            
            // FIX: Auto-restart unless manually turned off, interview ended, or agent is speaking
            if (sessionId && !interviewEnded && !userHasTurnedMicOff && !isAgentSpeaking) {
                setTimeout(() => {
                    try { recognition.start(); } catch(e) {}
                }, 300); 
            }
        };
    }
    
    // Manual Toggle Logic
    if (!recognizing) {
        userHasTurnedMicOff = false;
        recognition.start();
    } else {
        userHasTurnedMicOff = true;
        recognition.stop();
        clearTimer();
    }
}

// ====== SILENCE TIMER/TRANSCRIPT LOGIC ======
function resetSilenceTimer() {
    clearTimer();
    // Wait 5 seconds silence before sending
    silenceTimer = setTimeout(() => {
        submitTranscriptIfNeeded();
    }, SILENCE_INTERVAL);
}
function clearTimer() {
    if (silenceTimer) {
        clearTimeout(silenceTimer);
        silenceTimer = null;
    }
}
async function submitTranscriptIfNeeded() {
    clearTimer();
    // Ignore very short noise/fragments
    if (voiceTranscript.trim().length < 2) return; 
    
    const txt = voiceTranscript.trim();
    voiceTranscript = ""; // Clear buffer
    
    addMessage(txt, "user");
    await sendVoiceTranscript(txt);
}

async function sendVoiceTranscript(transcript) {
    if (!sessionId || interviewEnded) return;
    try {
        const response = await fetch(`${API_URL}/chat`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ session_id: sessionId, message: transcript })
        });
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();
        addMessage(data.message, "bot");
        if (data.audio) playAudio(data.audio);
    } catch (err) {
        console.error("Voice message error:", err);
    }
}
