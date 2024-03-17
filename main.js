console.log("running");

const electron = require("electron");
const { app, BrowserWindow, ipcMain } = electron;
const fs = require('fs');
const path = require("path");
const url = require("url");

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
    // Update this path to your desired location
    const customPath = 'F:\\AI Project\\temp screenshots';
    const imagePath = path.join(customPath, imageName);

    // Ensure the directory exists
    fs.mkdirSync(customPath, { recursive: true });

    fs.writeFile(imagePath, frameData.replace(/^data:image\/png;base64,/, ""), 'base64', err => {
        if (err) {
            console.error('Failed to save the frame:', err);
        } else {
            console.log('Frame saved as:', imagePath);
        }
    });
});

app.on('ready', createWindow);
