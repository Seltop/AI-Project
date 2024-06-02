console.log("running");

const electron = require("electron");
const { app, BrowserWindow, ipcMain, dialog } = electron;
const fs = require('fs');
const path = require("path");
const url = require("url");
const { exec } = require('child_process');

let win;

function createWindow() {
    win = new BrowserWindow({
        autoHideMenuBar: true,
        width: 1280,
        height: 720,
        webPreferences: {
            preload: path.join(__dirname, 'preload.js'),
            contextIsolation: true,
            enableRemoteModule: false,
        },
    });
    win.loadURL(url.format({
        pathname: path.join(__dirname, 'index.html'),
        protocol: 'file:',
        slashes: true
    }));

    win.on('closed', () => {
        console.log("quitting");
        win = null;
    });
}

ipcMain.on('save-frame', (event, { frameData, imageName }) => {
    const customPath = 'F:\\AI Project\\temp screenshots';
    const imagePath = path.join(customPath, imageName);

    fs.mkdirSync(customPath, { recursive: true });
    fs.writeFile(imagePath, frameData.replace(/^data:image\/png;base64,/, ""), 'base64', err => {
        if (err) {
            console.error('Failed to save the frame:', err);
        } else {
            console.log('Frame saved as:', imagePath);
        }
    });
});

ipcMain.on('save-image', (event, { imageData, imageName }) => {
    const customPath = 'F:\\AI Project\\temp screenshots';
    const imagePath = path.join(customPath, imageName);
    fs.mkdirSync(customPath, { recursive: true });
    fs.writeFile(imagePath, imageData.replace(/^data:image\/\w+;base64,/, ""), 'base64', function(err) {
        if (err) {
            console.error('Error saving the image:', err);
        } else {
            console.log('Reference image saved as', imagePath);
        }
    });
});

ipcMain.handle('select-destination', async (event) => {
    const result = await dialog.showOpenDialog(win, {
        properties: ['openDirectory']
    });
    return result;
});

ipcMain.on('apply-grade', (event, { videoPath, destinationPath }) => {
    const tempFramesDir = path.join(destinationPath, 'temp_frames');
    const outputVideoPath = path.join(destinationPath, 'output_video.mp4');

    // Ensure the tempFramesDir exists
    fs.mkdirSync(tempFramesDir, { recursive: true });

    // Define the full path to the FFmpeg executable
    const ffmpegPath = 'C:\\Users\\selto\\OneDrive\\Documents\\ffmpeg\\ffmpeg-2024-05-29-git-fa3b153cb1-essentials_build\\bin\\ffmpeg.exe';

    // Log paths to ensure they are correct
    console.log(`FFmpeg path: ${ffmpegPath}`);
    console.log(`Video path: ${videoPath}`);
    console.log(`Temp frames directory: ${tempFramesDir}`);
    console.log(`Output video path: ${outputVideoPath}`);

    // Step 1: Extract frames from the video
    exec(`"${ffmpegPath}" -i "${videoPath}" "${tempFramesDir}\\frame_%04d.png"`, (err, stdout, stderr) => {
        if (err) {
            console.error('Error extracting frames:', err);
            console.error(stderr);
            return;
        }
        console.log('Frames extracted successfully.');

        // Step 2: Process each frame
        fs.readdir(tempFramesDir, (err, files) => {
            if (err) {
                console.error('Error reading frames:', err);
                return;
            }

            const totalFrames = files.length;
            let processedFrames = 0;

            files.forEach((file, index) => {
                const framePath = path.join(tempFramesDir, file);
                applyModelToFrame(framePath, framePath, () => {
                    processedFrames++;
                    const progress = Math.floor((processedFrames / totalFrames) * 100);
                    win.webContents.send('progress-update', progress);

                    if (processedFrames === totalFrames) {
                        // Step 3: Reassemble the frames into a video
                        exec(`"${ffmpegPath}" -framerate 30 -i "${tempFramesDir}\\frame_%04d.png" -c:v libx264 -pix_fmt yuv420p "${outputVideoPath}"`, (err, stdout, stderr) => {
                            if (err) {
                                console.error('Error assembling video:', err);
                                console.error(stderr);
                                return;
                            }
                            console.log('Video assembled successfully.');
                            win.webContents.send('process-complete');
                        });
                    }
                });
            });
        });
    });
});



function applyModelToFrame(inputPath, outputPath, callback) {
    console.log(`Applying model to frame: ${inputPath}`);
    // Call your model's prediction function here and save the output to outputPath
    const { spawn } = require('child_process');
    const pythonProcess = spawn('python', ['process_frame.py', inputPath, outputPath]);

    pythonProcess.stdout.on('data', (data) => {
        console.log(`stdout: ${data}`);
    });

    pythonProcess.stderr.on('data', (data) => {
        console.error(`stderr: ${data}`);
    });

    pythonProcess.on('close', (code) => {
        console.log(`child process exited with code ${code}`);
        if (callback) callback();
    });
}

app.on('ready', createWindow);
