document.addEventListener('DOMContentLoaded', (event) => {
    // File upload preview and drag & drop for payload
    setupFileUpload('payload_audio', 'Upload a text or image file', ['.txt', '.png']);
    setupFileUpload('payload_video', 'Upload a text', ['.txt']);
    setupFileUpload('payload_image', 'Upload a text or audio file', ['.txt', '.wav']);
    
    // File upload preview and drag & drop for cover object
    setupFileUpload('cover_audio', 'Upload an audio file', ['.mp3', '.wav']);
    setupFileUpload('cover_video', 'Upload a video file', ['.mp4', '.avi', '.mkv']);
    setupFileUpload('cover_image', 'Upload an image file', ['.png', '.bmp', '.gif']);

    // File upload preview and drag & drop for payload decoding
    setupFileUpload('decode_payload_text', 'Upload file', ['.mp3', '.wav', '.mp4', '.avi', '.png', '.bmp', '.mkv']);
    setupFileUpload('decode_payload_image', 'Upload an audio file', ['.mp3', '.wav']);
    setupFileUpload('decode_payload_audio', 'Upload an image file', ['.png', '.bmp']);

    setupVideoEncoding();

    // Initialize slider value
    const slider = document.getElementById('bit_size');
    if (slider) {
        updateSliderValue(slider.value);
        slider.addEventListener('input', (e) => updateSliderValue(e.target.value));
    }
});

function setupVideoEncoding() {
    const uploadForm = document.getElementById('uploadForm');
    const encodeForm = document.getElementById('encodeForm');
    const uploadStatus = document.getElementById('uploadStatus');
    const step2 = document.getElementById('step2');
    const frameNumber = document.getElementById('frameNumber');
    const bitSize = document.getElementById('bit_size');
    const sliderValue = document.getElementById('slider_value');
    const frameDisplay = document.getElementById('frameDisplay');

    if (uploadForm) {
        uploadForm.addEventListener('submit', (e) => {
            // Let the form submit normally, no need to prevent default
            // The server will handle the upload and use flash messages
        });
    }

    if (encodeForm) {
        encodeForm.addEventListener('submit', (e) => {
            // Let the form submit normally for encoding as well
        });
    }

    if (bitSize && sliderValue) {
        bitSize.addEventListener('input', (e) => {
            sliderValue.textContent = e.target.value;
        });
    }

    // Show/hide step2 based on session data
    if (step2) {
        const frameCount = parseInt(frameNumber.getAttribute('max')) + 1;
        if (frameCount > 0) {
            step2.style.display = 'block';
        } else {
            step2.style.display = 'none';
        }
    }
}

function setupFileUpload(inputId, defaultText, allowedExtensions) {
    const fileInput = document.getElementById(inputId);
    if (!fileInput) return;

    const fileLabel = document.querySelector(`label[for="${inputId}"]`);
    const dropZone = fileInput.closest('.border-dashed') || fileInput.parentElement;

    if (!dropZone) return;

    fileInput.addEventListener('change', (e) => {
        handleFileSelection(fileInput, fileLabel, defaultText, allowedExtensions, dropZone);
        if (inputId === 'cover_video' && fileInput.files.length > 0) {
            document.getElementById('uploadForm').submit();
        }
    });

    dropZone.addEventListener('click', () => {
        fileInput.click();
    });

    fileInput.addEventListener('change', (e) => {
        handleFileSelection(fileInput, fileLabel, defaultText, allowedExtensions, dropZone);
    });

    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('border-blue-500', 'border-2');
    });

    dropZone.addEventListener('dragleave', (e) => {
        e.preventDefault();
        dropZone.classList.remove('border-blue-500', 'border-2');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('border-blue-500', 'border-2');
        const files = e.dataTransfer.files;
        if (files.length > 0 && isValidFileType(files[0], allowedExtensions)) {
            fileInput.files = files;
            handleFileSelection(fileInput, fileLabel, defaultText, allowedExtensions, dropZone);
        } else {
            alert(`Please upload a valid file type: ${allowedExtensions.join(', ')}`);
        }
    });
}

function handleFileSelection(fileInput, fileLabel, defaultText, allowedExtensions, dropZone) {
    if (fileInput.files.length > 0) {
        const file = fileInput.files[0];
        if (isValidFileType(file, allowedExtensions)) {
            updateFileName(fileInput, fileLabel);
            dropZone.classList.remove('border-dashed');
            dropZone.classList.add('border-solid');
        } else {
            fileInput.value = ''; // Clear the file input
            alert(`Please upload a valid file type: ${allowedExtensions.join(', ')}`);
            fileLabel.textContent = defaultText;
        }
    } else {
        fileLabel.textContent = defaultText;
    }
}

function isValidFileType(file, allowedExtensions) {
    return allowedExtensions.some(ext => file.name.toLowerCase().endsWith(ext));
}

function updateFileName(fileInput, fileLabel) {
    if (fileInput.files.length > 0) {
        const fileName = fileInput.files[0].name;
        fileLabel.textContent = fileName;
    }
}

function updateSliderValue(val) {
    const sliderValue = document.getElementById('slider_value');
    if (sliderValue) {
        sliderValue.textContent = val;
    }
}

function handleCoverObjectChange(selectElement) {
    const coverObject = selectElement.value;
    
    if (coverObject && window.urls && coverObject in window.urls) {
        window.location.href = window.urls[coverObject];
    }
}