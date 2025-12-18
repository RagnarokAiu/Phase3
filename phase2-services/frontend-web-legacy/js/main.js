const services = [
    { id: 'user-service', url: '/api/users/health', name: 'User Service' },
    { id: 'chat-service', url: '/api/chat/health', name: 'Chat Service' },
    { id: 'doc-service', url: '/api/documents/health', name: 'Document Service' },
    { id: 'quiz-service', url: '/api/quiz/health', name: 'Quiz Service' },
    { id: 'stt-service', url: '/api/stt/health', name: 'STT Service' },
    { id: 'tts-service', url: '/api/tts/health', name: 'TTS Service' }
];

async function checkService(service) {
    const card = document.getElementById(service.id);
    const statusEl = card.querySelector('.status');

    try {
        const response = await fetch(service.url);
        if (response.ok) {
            const data = await response.json();
            statusEl.textContent = 'Running';
            statusEl.style.color = 'green';
            statusEl.style.fontWeight = 'bold';
        } else {
            throw new Error('Service Error');
        }
    } catch (error) {
        console.error(`Error checking ${service.name}:`, error);
        statusEl.textContent = 'Offline';
        statusEl.style.color = 'red';
    }
}

function checkAllServices() {
    services.forEach(checkService);
}

// Check immediately on load
checkAllServices();

// Poll every 10 seconds
setInterval(checkAllServices, 10000);

async function uploadDocument() {
    const fileInput = document.getElementById('doc-upload');
    const statusEl = document.getElementById('upload-status');
    const file = fileInput.files[0];

    if (!file) {
        statusEl.textContent = 'Please select a file first.';
        statusEl.style.color = 'red';
        return;
    }

    const formData = new FormData();
    formData.append('file', file);

    statusEl.textContent = 'Uploading...';
    statusEl.style.color = 'blue';

    try {
        const response = await fetch('/api/documents/upload', {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            const result = await response.json();
            statusEl.textContent = 'Success! ID: ' + result.file_id;
            statusEl.style.color = 'green';
        } else {
            throw new Error('Upload failed');
        }
    } catch (error) {
        console.error('Upload Error:', error);
        statusEl.textContent = 'Error uploading file.';
        statusEl.style.color = 'red';
    }
}
