$(document).ready(function () {
    var currentStep = 'uploadvideo.html';
    var isVideoSelected = false;
    var selectedVideoPath = '';
    var destinationPath = '';
    $('#proceedButton').prop('disabled', true);

    // Initial content load
    $('#content').load(currentStep, function (response, status, xhr) {
        if (status == "error") {
            console.log("An error occurred while preloading the page: " + xhr.status + " " + xhr.statusText);
        } else {
            initializeVideoPlayer();
            $('.sidenav-links div').removeClass('activelink');
            $('.sidenav-links div:contains("Upload Video")').addClass('activelink');
        }
    });

    // Proceed button click
    $('#proceedButton').click(function () {
        console.log('Proceed button clicked');
        captureAndSendFrame();
        var nextStep = '';
        switch (currentStep) {
            case 'uploadvideo.html':
                nextStep = 'referenceimage.html';
                break;
            case 'referenceimage.html':
                nextStep = 'applygrade.html';
                break;
            case 'applygrade.html':
                $(this).hide();
                return;
        }

        $('#content').load(nextStep, function (response, status, xhr) {
            if (status == "error") {
                console.log("An error occurred while loading the page: " + xhr.status + " " + xhr.statusText);
            } else {
                $('.sidenav-links div').removeClass('activelink');
                switch (nextStep) {
                    case 'uploadvideo.html':
                        $('.sidenav-links div:contains("Upload Video")').addClass('activelink');
                        initializeVideoPlayer();
                        break;
                    case 'referenceimage.html':
                        $('.sidenav-links div:contains("Reference Frame")').addClass('activelink');
                        initializeImageUploader();
                        displayOriginalImage();
                        break;
                    case 'applygrade.html':
                        $('.sidenav-links div:contains("Apply Grade")').addClass('activelink');
                        initializeDestinationPicker();
                        showSelectedVideoPath();
                        break;
                }
            }
        });

        currentStep = nextStep;
    });

    function captureAndSendFrame() {
        const video = document.querySelector('video');
        if (!video) {
            console.log('No video found');
            return;
        }

        const canvas = document.createElement('canvas');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        const frameData = canvas.toDataURL('image/png');

        selectedVideoPath = video.src;
        const imageName = `chosen_frame.png`;

        console.log('Sending frame to main process');
        window.electron.ipcRenderer.send('save-frame', { frameData, imageName });
    }

    function displayOriginalImage() {
        const imagePath = 'file://F:/AI Project/temp screenshots/chosen_frame.png';
        $('#originalImage').attr('src', imagePath);
    }

    function showSelectedVideoPath() {
        $('#selectedVideoPath').text(selectedVideoPath);
    }

    function initializeDestinationPicker() {
        $('#selectDestinationButton').click(function () {
            window.electron.ipcRenderer.invoke('select-destination').then(result => {
                if (result.canceled) {
                    console.log('Destination selection was canceled.');
                } else {
                    destinationPath = result.filePaths[0];
                    $('#destinationPath').text(destinationPath);
                }
            });
        });

        $('#applyGradeButton').click(function () {
            if (!destinationPath) {
                alert('Please select a destination.');
                return;
            }

            $('#progressContainer').show();
            $('#applyGradeButton').prop('disabled', true);

            console.log('Sending apply-grade to main process');
            window.electron.ipcRenderer.send('apply-grade', { videoPath: selectedVideoPath, destinationPath: destinationPath });

            window.electron.ipcRenderer.on('progress-update', (event, progress) => {
                console.log('Progress update:', progress);
                $('#progressBar').val(progress);
                $('#progressText').text(`${progress}%`);
            });

            window.electron.ipcRenderer.on('process-complete', () => {
                console.log('Video processing complete');
                alert('Video processing complete.');
                $('#progressContainer').hide();
                $('#applyGradeButton').prop('disabled', false);
            });
        });
    }

    $(document).on('click', '#processButton', async function() {
        console.log('Process button clicked');
        try {
            const response = await fetch('http://localhost:5000/process-image', {
                method: 'POST'
            });

            const result = await response.json();
            
            if (result.transformed_image) {
                const transformedImageSrc = 'data:image/png;base64,' + result.transformed_image;
                $('#transformedImage').attr('src', transformedImageSrc);
            } else {
                $('#transformedImage').attr('alt', 'Error processing image');
            }
        } catch (error) {
            console.error('Error:', error);
            $('#transformedImage').attr('alt', 'Error: ' + error.message);
        }
    });
});

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
                const filePath = URL.createObjectURL(file);
                videoElement.src = filePath;
                videoElement.controls = true;
                videoPlayer.innerHTML = '';
                videoPlayer.appendChild(videoElement);

                selectedVideoPath = file.path; // Store the actual file path

                console.log('Video loaded:', selectedVideoPath);
                videoElement.addEventListener('loadedmetadata', function() {
                    $('#proceedButton').prop('disabled', false);
                });
            }
        }
    }
}

function initializeImageUploader() {
    const imageInput = document.getElementById('imageInput');
    const imageDropArea = document.getElementById('imageDropArea');
    const selectedImageContainer = document.getElementById('selectedImageContainer');
    const selectedImage = document.getElementById('selectedImage');

    let imageSelected = false;

    function disableInput() {
        imageDropArea.removeEventListener('click', promptFileSelect);
        imageDropArea.removeEventListener('drop', handleImageDrop);
        imageDropArea.style.cursor = 'default';
        imageSelected = true;
    }

    function hideDragAndDrop() {
        $('#imageDropArea').remove();
    }

    function promptFileSelect() {
        if (!imageSelected) {
            imageInput.click();
        }
    }

    function displayImage(file) {
        if (file && file.type.startsWith('image/')) {
            selectedImage.src = URL.createObjectURL(file);
            selectedImageContainer.style.display = 'block';
            const reader = new FileReader();
            reader.onload = function (e) {
                window.electron.ipcRenderer.send('save-image', { imageData: e.target.result, imageName: 'chosen_reference_image.png' });
            };

            reader.readAsDataURL(file);
            hideDragAndDrop();
        }
    }

    function handleImageDrop(e) {
        e.preventDefault();
        if (!imageSelected) {
            const dt = e.dataTransfer;
            const file = dt.files[0];
            displayImage(file);
        }
    }

    if (imageInput && imageDropArea) {
        imageDropArea.addEventListener('click', promptFileSelect);
        imageInput.addEventListener('change', function () {
            displayImage(this.files[0]);
        });

        ['dragenter', 'dragover'].forEach(eventName => {
            imageDropArea.addEventListener(eventName, function (e) {
                e.preventDefault();
                imageDropArea.classList.add('highlight');
            }, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            imageDropArea.addEventListener(eventName, function (e) {
                e.preventDefault();
                imageDropArea.classList.remove('highlight');
            }, false);
        });

        imageDropArea.addEventListener('drop', handleImageDrop, false);
    }
}
