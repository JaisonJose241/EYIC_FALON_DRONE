/*
*
* Project Name: 	FALON drone - stranded people detection using UAV
* Author List: 		Sarang Chouguley
* Filename: 	main.js
* Functions: 		create_window()
* Global Variables:	None
*
*/

const { app, BrowserWindow } = require('electron')
const path = require('path')

/*
*
* Function Name: 	create_window
* Input: 		None
* Output: 	None
* Logic: 		This function creates the initial window of the software
            and also spawns python files for backend communication
* Example Call:		create_window()
*
*/
function create_window() {
  const win = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      nodeIntegration: true
    }
  })

  app.setAccessibilitySupportEnabled(true)

  win.loadFile('index.html')

  // start python telemetry server
  const telemeetryProcess = require('child_process').spawn('python3', [path.join(__dirname, '/python/telemetry.py')]);
  telemeetryProcess.stdout.on('data', function (data) {
    console.log("Telemetry server response: ", data.toString('utf8'));
  });
  telemeetryProcess.stderr.on('data', (data) => {
    console.error(`stderr: ${data}`);
  });
  telemetryProcess.on('close', (code) => {
    console.log(`child process exited with code ${code}`);
  });

  // // start python serial server
  const serialProcess = require('child_process').spawn('python3', [path.join(__dirname, '/python/serial.py')]);
  serialProcess.stdout.on('data', function (data) {
    console.log("Serial Python server response: ", data.toString('utf8'));
  });
  serialProcess.stderr.on('data', (data) => {
    console.error(`stderr: ${data}`);
  });
  serialProcess.on('close', (code) => {
    console.log(`child process exited with code ${code}`);
  });
}

// on ready create window
app.whenReady().then(create_window)

// on stop quit app
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

// on start create window
app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    create_window()
  }
})

const env = process.env.NODE_ENV || 'development';

// If development environment, start hot reloading
if (env === 'development') {
  try {
    require('electron-reloader')(module, {
      debug: true,
      watchRenderer: true
    });
  } catch (_) { console.log('Error'); }
}

