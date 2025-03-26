# Hotkey Automation Tool

A Python-based automation tool that converts AutoHotkey scripts into a modern, user-friendly application with a graphical interface. The application supports global hotkeys and automated mouse clicks with configurable coordinates and actions.

## Features

- Modern GUI with system tray integration
- Global hotkey support (F1-F8, numeric keys, and backtick)
- Configurable mouse click actions (coordinates, button type, repeat count)
- Real-time configuration editing
- Background operation
- Detailed logging
- Error handling and validation

## Requirements

- Python 3.7 or higher
- Required Python packages (installed automatically via pip):
  - pyautogui
  - pynput
  - PyQt5
  - loguru

## Installation

1. Clone or download this repository
2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Starting the Application

Run the application with the GUI:
```bash
python gui.py
```

Run the application in console mode (without GUI):
```bash
python main.py
```

### GUI Features

1. **Main Window**
   - Start/Stop Listener: Toggle the hotkey listener
   - Reload Config: Reload the configuration from file
   - Save Changes: Save current configuration
   - Configuration Table: Edit hotkey actions
   - Log Display: View application status and errors

2. **System Tray**
   - Right-click the tray icon for quick actions
   - Show/Hide window
   - Start/Stop listener
   - Quit application

### Configuration

The configuration is stored in `config.json` and can be edited directly or through the GUI:

```json
{
  "char_settings": {
    "char1": "U8",
    "char2": "wekwok",
    "char3": "Uboring",
    "char4": "U9",
    "char5": ""
  },
  "hotkeys": {
    "f1": [
      {
        "x": 490,
        "y": 711,
        "button": "RIGHT",
        "repeat": 1,
        "char": "char1"
      }
    ]
  }
}
```

### Hotkey Actions

Each hotkey can trigger multiple mouse click actions. Actions are configured with:
- X and Y coordinates
- Mouse button (LEFT or RIGHT)
- Number of clicks (repeat)
- Character reference

## Safety Features

- Mouse failsafe: Move mouse to screen corner to abort
- Configuration validation
- Error logging
- Graceful error handling

## Troubleshooting

1. **Hotkeys not working**
   - Ensure the listener is started (check system tray icon)
   - Verify configuration in the GUI
   - Check app.log for errors

2. **Mouse clicks not accurate**
   - Verify screen coordinates in configuration
   - Ensure target window is in the correct position
   - Check if coordinates need adjustment for your screen resolution

3. **Application not starting**
   - Verify Python installation
   - Check all dependencies are installed
   - Look for errors in app.log

## Logs

Application logs are stored in `app.log` with the following information:
- Timestamp
- Log level (INFO, ERROR, etc.)
- Detailed message
- Automatic rotation (10MB size limit)
- One week retention

## License

This project is licensed under the MIT License - see the LICENSE file for details.