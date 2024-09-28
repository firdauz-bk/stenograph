document.addEventListener('DOMContentLoaded', (event) => {
    // File upload preview and drag & drop for payload
    setupFileUpload('payload', 'Upload a .txt file', ['.txt']);
    
    // File upload preview and drag & drop for cover object
    setupFileUpload('cover', 'Upload an audio file', ['.mp3', '.wav']);

    // Initialize slider value
    updateSliderValue(document.getElementById('bit_size').value);
});

function setupFileUpload(inputId, defaultText, allowedExtensions) {
    const fileInput = document.getElementById(inputId);
    const fileLabel = document.querySelector(`label[for="${inputId}"]`);
    const dropZone = fileInput.closest('.border-dashed');

    fileInput.addEventListener('change', (e) => {
        handleFileSelection(fileInput, fileLabel, defaultText, allowedExtensions);
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
            handleFileSelection(fileInput, fileLabel, defaultText, allowedExtensions);
        } else {
            alert(`Please upload a valid file type: ${allowedExtensions.join(', ')}`);
        }
    });
}

function handleFileSelection(fileInput, fileLabel, defaultText, allowedExtensions) {
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
    document.getElementById('slider_value').textContent = val;
}

function handleCoverObjectChange(selectElement) {
    const coverObject = selectElement.value;
    
    if (coverObject && coverObject in urls) {
        window.location.href = urls[coverObject];
    }
}