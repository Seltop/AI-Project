function initializeVideoPlayer() {
    const fileInput = document.getElementById('fileInput');
    const dropArea = document.getElementById('dropArea');
    const videoPlayer = document.getElementById('videoPlayer');

    if (fileInput && dropArea && videoPlayer) {
        dropArea.addEventListener('click', function () {
            fileInput.click();
        });

        fileInput.addEventListener('change', function () {
            loadVideo(this.files[0]);
        });

        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropArea.addEventListener(eventName, preventDefaults, false);
            document.body.addEventListener(eventName, preventDefaults, false);
        });

        ['dragenter', 'dragover'].forEach(eventName => {
            dropArea.addEventListener(eventName, highlight, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropArea.addEventListener(eventName, unhighlight, false);
        });

        dropArea.addEventListener('drop', handleDrop, false);

        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }

        function highlight() {
            dropArea.classList.add('highlight');
        }

        function unhighlight() {
            dropArea.classList.remove('highlight');
        }

        function handleDrop(e) {
            const dt = e.dataTransfer;
            const file = dt.files[0];

            loadVideo(file);
        }

        function loadVideo(file) {
            if (file && file.type.startsWith('video/')) {
                const videoElement = document.createElement('video');
                videoElement.src = URL.createObjectURL(file);
                videoElement.controls = true;
                videoPlayer.innerHTML = '';
                videoPlayer.appendChild(videoElement);
                
                videoElement.addEventListener('loadedmetadata', function() {
                    $('#proceedButton').prop('disabled', false);
                });
            }
        }
    }
}

document.addEventListener('DOMContentLoaded', initializeVideoPlayer);
