document.addEventListener('DOMContentLoaded', (event) => {
    // File upload preview and drag & drop for payload
    setupFileUpload('payload_audio', 'Upload a text or image file', ['.txt', '.png']);
    setupFileUpload('payload_video', 'Upload a text or image file', ['.txt']);
    setupFileUpload('payload_image', 'Upload a text or image file', ['.txt', '.wav']);
    
    // File upload preview and drag & drop for cover object
    setupFileUpload('cover_audio', 'Upload an audio file', ['.mp3', '.wav']);
    setupFileUpload('cover_video', 'Upload a video file', ['.mp4', '.avi']);
    setupFileUpload('cover_image', 'Upload an image file', ['.png', '.bmp', '.gif']);

    // File upload preview and drag & drop for tex decoding
    setupFileUpload('decode_text', 'Upload an audio file', ['.mp3', '.wav', '.mp4', '.avi', '.png', '.bmp']);
    setupFileUpload('decode_image', 'Upload an audio file', ['.mp3', '.wav']);
    setupFileUpload('decode_audio', 'Upload an audio file', ['.png', '.bmp']);

    // Initialize slider value
    const slider = document.getElementById('bit_size');
    if (slider) {
        updateSliderValue(slider.value);
        slider.addEventListener('input', (e) => updateSliderValue(e.target.value));
    }
});

function setupFileUpload(inputId, defaultText, allowedExtensions) {
    const fileInput = document.getElementById(inputId);
    if (!fileInput) return;

    const fileLabel = document.querySelector(`label[for="${inputId}"]`);
    const dropZone = fileInput.closest('.border-dashed');

    if (!dropZone) return;

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