$(document).ready(function() {
    var currentStep = 'uploadvideo.html';

    // Initial content load
    $('#content').load(currentStep, function(response, status, xhr) {
        if (status == "error") {
            console.log("An error occurred while preloading the page: " + xhr.status + " " + xhr.statusText);
        } else {
            initializeVideoPlayer();
            // Since the links are not <a> tags, update the selector
            $('.sidenav-links div').removeClass('activelink');
            $('.sidenav-links div:contains("Upload Video")').addClass('activelink');
        }
    });

    // Proceed button click
    $('#proceedButton').click(function() {
        captureAndSendFrame();
        var nextStep = '';
        switch(currentStep) {
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

        $('#content').load(nextStep, function(response, status, xhr) {
            if (status == "error") {
                console.log("An error occurred while loading the page: " + xhr.status + " " + xhr.statusText);
            } else {
                $('.sidenav-links div').removeClass('activelink');
                switch(nextStep) {
                    case 'uploadvideo.html':
                        $('.sidenav-links div:contains("Upload Video")').addClass('activelink');
                        break;
                    case 'referenceimage.html':
                        $('.sidenav-links div:contains("Reference Frame")').addClass('activelink');
                        break;
                    case 'applygrade.html':
                        $('.sidenav-links div:contains("Apply Grade")').addClass('activelink');
                        break;
                }

                if (nextStep === 'uploadvideo.html' || nextStep === 'referenceimage.html') {
                    initializeVideoPlayer();
                }
            }
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
        
            // Extract the video file name from the video element's src attribute
            // You might need to adjust this depending on how the video src is set
            const videoSrc = video.src || '';
            const fileNameMatch = videoSrc.match(/([^\/]+)(?=\.\w+$)/); // Regex to extract file name without extension
            const fileName = fileNameMatch ? fileNameMatch[0] : 'captured_frame';
            const imageName = `${fileName}_chosen_frame.png`;
        
            // Use ipcRenderer to send the frame data and image name to the main process
            window.electron.ipcRenderer.send('save-frame', { frameData, imageName });
        }
        
        currentStep = nextStep;
    });
});
