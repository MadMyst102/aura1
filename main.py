import sys
import threading
from license_manager import check_license_and_activate
import time
import os
from typing import Dict, Any, Optional, List
import pyautogui
import keyboard
from pynput import keyboard as pynput_keyboard
from loguru import logger
import json
from datetime import datetime
import win32gui
import win32con
import win32api
import win32process
import ctypes
from ctypes import wintypes

from utils import get_config_manager, ConfigManager

class HotkeyManager:
    def __init__(self):
        self.config_manager = get_config_manager()
        self.config = self.config_manager.load_config()
        self.listener: Optional[pynput_keyboard.GlobalHotKeys] = None
        self.running = False
        self.last_execution = {}  # Track last execution time for each hotkey
        self.execution_count = {}  # Track execution count for analytics
        self.cooldown = 0.01  # Reduced cooldown period between executions (seconds)
        self.key_delay = 0.0005  # Reduced delay between sending actions to multiple clients
        self.paused = False  # Pause state for multiclient actions
        self.start_time = datetime.now()
        
        # Initialize window selection
        self.selected_windows = []
        self.captured_windows = []
        
        # Initialize analytics data
        self.analytics = {
            'total_executions': 0,
            'hotkey_usage': {},
            'errors': [],
            'session_start': self.start_time.isoformat()
        }
        
        # Initialize PyAutoGUI settings
        pyautogui.FAILSAFE = True  # Move mouse to corner to abort
        pyautogui.PAUSE = 0.1  # Add small delay between actions
    
    def _setup_keyboard_listeners(self):
        """Set up both pynput and keyboard listeners for better hotkey coverage"""
        # Set up keyboard library for function keys
        for hotkey in self.config["hotkeys"].keys():
            if hotkey.lower().startswith('f') and hotkey[1:].isdigit():
                keyboard.on_press_key(hotkey.lower(), lambda e, k=hotkey: self._execute_actions(k))
    
    def _get_hotkey_mapping(self) -> Dict[str, Any]:
        """
        Create mapping of hotkeys to their handler functions (for non-function keys)
        Returns:
            Dictionary mapping hotkey strings to handler functions
        """
        mapping = {}
        
        for hotkey in self.config["hotkeys"].keys():
            # Skip function keys as they're handled by keyboard library
            if not (hotkey.lower().startswith('f') and hotkey[1:].isdigit()):
                mapping[hotkey] = lambda k=hotkey: self._execute_actions(k)
        
        return mapping
    
    def _execute_actions(self, hotkey: str):
        """
        Execute the actions associated with a hotkey with improved handling
        Args:
            hotkey: The hotkey that was pressed
        """
        # Check if actions are paused
        if self.paused:
            logger.debug(f"Skipping {hotkey} - actions are paused")
            return
            
        # Check cooldown
        current_time = time.time()
        if hotkey in self.last_execution:
            if current_time - self.last_execution[hotkey] < self.cooldown:
                logger.debug(f"Skipping {hotkey} - cooldown active")
                return
                
        self.last_execution[hotkey] = current_time
        
        # Update analytics
        self.analytics['total_executions'] += 1
        self.analytics['hotkey_usage'][hotkey] = self.analytics['hotkey_usage'].get(hotkey, 0) + 1
        
        try:
            actions = self.config["hotkeys"].get(hotkey, [])
            char_settings = self.config["char_settings"]
            
            logger.info(f"Executing actions for hotkey: {hotkey}")
            
            # Check if we have selected windows (either running or captured)
            if self.selected_windows:
                # First, check if this is a function key (F1-F12) hotkey
                # If so, send the key directly to all selected windows
                if hotkey.lower().startswith('f') and hotkey[1:].isdigit() and 1 <= int(hotkey[1:]) <= 12:
                    logger.info(f"Sending function key {hotkey} to all selected windows")
                    for i, window in enumerate(self.selected_windows):
                        try:
                            hwnd = window["hwnd"]
                            # Ensure window is still valid - use more robust validation
                            try:
                                # First check if window exists
                                if win32gui.IsWindow(hwnd):
                                    # Additional validation - check if window is visible
                                    if win32gui.IsWindowVisible(hwnd):
                                        # Send the function key directly to the window without changing focus
                                        self._send_key_to_window(hwnd, hotkey.lower())
                                        logger.debug(f"Sent {hotkey} key to window {window['title']}")
                                    else:
                                        # Window exists but might be minimized - try anyway
                                        logger.debug(f"Window {window['title']} is not visible, but trying to send key anyway")
                                        self._send_key_to_window(hwnd, hotkey.lower())
                                        logger.debug(f"Attempted to send {hotkey} key to non-visible window {window['title']}")
                                else:
                                    logger.warning(f"Window {window['title']} is no longer valid")
                            except Exception as e:
                                logger.error(f"Error validating window {window['title']}: {e}")
                                
                            # Add delay between windows to prevent race conditions
                            # but don't delay after the last window
                            if i < len(self.selected_windows) - 1:
                                time.sleep(self.key_delay)
                        except Exception as window_e:
                            logger.error(f"Error sending key to window {window['title']}: {window_e}")
                            self.analytics['errors'].append({
                                'time': datetime.now().isoformat(),
                                'hotkey': hotkey,
                                'error': str(window_e)
                            })
                    
                    # No need to update analytics here as errors are caught in the try/except block
                else:
                    # Execute actions on selected windows without moving mouse
                    for action in actions:
                        try:
                            # Get the character value for this action
                            char_value = char_settings.get(action["char"], "")
                            if not char_value:  # Skip if no character value
                                continue
                            
                            # Send input to each selected window with delay between windows
                            for i, window in enumerate(self.selected_windows):
                                try:
                                    hwnd = window["hwnd"]
                                    # Ensure window is still valid
                                    if win32gui.IsWindow(hwnd):
                                        # Send click to window at specified coordinates
                                        self._send_click_to_window(
                                            hwnd,
                                            action["x"],
                                            action["y"],
                                            action["button"],
                                            action["repeat"]
                                        )
                                        logger.debug(f"Sent click to window {window['title']} at ({action['x']}, {action['y']}) with {action['button']} button")
                                    else:
                                        logger.warning(f"Window {window['title']} is no longer valid")
                                        
                                    # Add delay between windows to prevent race conditions
                                    # but don't delay after the last window
                                    if i < len(self.selected_windows) - 1:
                                        time.sleep(self.key_delay)
                                except Exception as window_e:
                                    logger.error(f"Error sending input to window {window['title']}: {window_e}")
                                    self.analytics['errors'].append({
                                        'time': datetime.now().isoformat(),
                                        'hotkey': hotkey,
                                        'error': str(window_e)
                                    })
                        except Exception as e:
                            logger.error(f"Error processing action for hotkey {hotkey}: {e}")
                            self.analytics['errors'].append({
                                'time': datetime.now().isoformat(),
                                'hotkey': hotkey,
                                'error': str(e)
                            })
            else:
                # No windows selected, log a warning
                logger.warning(f"No windows selected for hotkey {hotkey}")
        except Exception as e:
            logger.error(f"Unhandled error in _execute_actions for hotkey {hotkey}: {e}")
            self.analytics['errors'].append({
                'time': datetime.now().isoformat(),
                'hotkey': hotkey,
                'error': str(e)
            })
    
    def start(self):
        """Start the hotkey listeners"""
        if self.running:
            logger.warning("Hotkey listener is already running")
            return
        
        try:
            # Set up function key listeners
            self._setup_keyboard_listeners()
            
            # Create pynput listener for other keys
            mapping = self._get_hotkey_mapping()
            if mapping:  # Only create if we have non-function key hotkeys
                self.listener = pynput_keyboard.GlobalHotKeys(mapping)
                self.listener.start()
            
            self.running = True
            self.start_time = datetime.now()
            
            logger.info("Hotkey listeners started successfully")
            
        except Exception as e:
            logger.error(f"Error starting hotkey listeners: {e}")
            self.running = False
    
    def stop(self):
        """Stop the hotkey listeners"""
        if not self.running:
            logger.warning("Hotkey listener is not running")
            return
        
        try:
            # Stop pynput listener
            if self.listener:
                self.listener.stop()
                self.listener = None
            
            # Remove keyboard library hotkeys
            keyboard.unhook_all()
            
            self.running = False
            logger.info("Hotkey listeners stopped successfully")
            
        except Exception as e:
            logger.error(f"Error stopping hotkey listeners: {e}")
    
    def reload_config(self):
        """Reload configuration from file with validation"""
        try:
            # Save analytics before reload
            self.save_analytics()
            
            was_running = self.running
            if was_running:
                self.stop()
            
            self.config = self.config_manager.load_config()
            
            # Validate all coordinates are within screen bounds
            screen_width, screen_height = pyautogui.size()
            for hotkey, actions in self.config["hotkeys"].items():
                for action in actions:
                    if not (0 <= action["x"] <= screen_width and 0 <= action["y"] <= screen_height):
                        logger.warning(f"Coordinates ({action['x']}, {action['y']}) for hotkey {hotkey} are outside screen bounds")
            
            if was_running:
                self.start()
                
            logger.info("Configuration reloaded and validated successfully")
            
        except Exception as e:
            logger.error(f"Error reloading configuration: {e}")
            self.analytics['errors'].append({
                'time': datetime.now().isoformat(),
                'error': f"Config reload error: {str(e)}"
            })

    def _send_click_to_window(self, hwnd, x, y, button, repeat):
        """
        Send a click to a specific window at the given coordinates without moving the mouse
        or changing window focus, using both PostMessage and SendInput for better reliability
        Args:
            hwnd: Window handle
            x: X coordinate relative to the window
            y: Y coordinate relative to the window
            button: Mouse button (LEFT or RIGHT)
            repeat: Number of clicks
        """
        try:
            # Get window position and size
            left, top, right, bottom = win32gui.GetWindowRect(hwnd)
            
            # Calculate absolute screen coordinates
            screen_x = left + x
            screen_y = top + y
            
            # Send the click message to the window
            if button.upper() == "LEFT":
                button_down = win32con.WM_LBUTTONDOWN
                button_up = win32con.WM_LBUTTONUP
            else:  # RIGHT
                button_down = win32con.WM_RBUTTONDOWN
                button_up = win32con.WM_RBUTTONUP
            
            # Convert to client coordinates
            client_x, client_y = win32gui.ScreenToClient(hwnd, (screen_x, screen_y))
            
            # Create lParam for position
            lParam = win32api.MAKELONG(client_x, client_y)
            
            # First, try to attach to the window's thread
            current_thread = win32api.GetCurrentThreadId()
            target_thread = win32process.GetWindowThreadProcessId(hwnd)[0]
            attached = False
            
            try:
                # Attach to the window's thread input queue
                if current_thread != target_thread:
                    attached = win32process.AttachThreadInput(current_thread, target_thread, True)
                
                # Send clicks directly to the window without changing focus
                # Using PostMessage which doesn't require the window to be in foreground
                for _ in range(repeat):
                    win32gui.PostMessage(hwnd, button_down, 0, lParam)
                    win32gui.PostMessage(hwnd, button_up, 0, lParam)
                    time.sleep(0.05)  # Small delay between clicks
                
                # For game clients, also try SendInput as a backup method
                # This requires setting the window as foreground temporarily
                if attached:
                    # Only try SendInput if we successfully attached
                    prev_foreground = win32gui.GetForegroundWindow()
                    try:
                        # Set the window as foreground temporarily
                        win32gui.SetForegroundWindow(hwnd)
                        
                        # Calculate relative position for SendInput (0-65535 range)
                        normalized_x = int(65535 * (screen_x / win32api.GetSystemMetrics(0)))
                        normalized_y = int(65535 * (screen_y / win32api.GetSystemMetrics(1)))
                        
                        # Define input structure for SendInput
                        MOUSEEVENTF_ABSOLUTE = 0x8000
                        MOUSEEVENTF_MOVE = 0x0001
                        MOUSEEVENTF_LEFTDOWN = 0x0002
                        MOUSEEVENTF_LEFTUP = 0x0004
                        MOUSEEVENTF_RIGHTDOWN = 0x0008
                        MOUSEEVENTF_RIGHTUP = 0x0010
                        
                        # Create mouse input structure
                        class MOUSEINPUT(ctypes.Structure):
                            _fields_ = (
                                ("dx", wintypes.LONG),
                                ("dy", wintypes.LONG),
                                ("mouseData", wintypes.DWORD),
                                ("dwFlags", wintypes.DWORD),
                                ("time", wintypes.DWORD),
                                ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))
                            )
                        
                        class KEYBDINPUT(ctypes.Structure):
                            _fields_ = (
                                ("wVk", wintypes.WORD),
                                ("wScan", wintypes.WORD),
                                ("dwFlags", wintypes.DWORD),
                                ("time", wintypes.DWORD),
                                ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))
                            )
                        
                        class HARDWAREINPUT(ctypes.Structure):
                            _fields_ = (
                                ("uMsg", wintypes.DWORD),
                                ("wParamL", wintypes.WORD),
                                ("wParamH", wintypes.WORD)
                            )
                        
                        class INPUT_union(ctypes.Union):
                            _fields_ = (
                                ("mi", MOUSEINPUT),
                                ("ki", KEYBDINPUT),
                                ("hi", HARDWAREINPUT)
                            )
                        
                        class INPUT(ctypes.Structure):
                            _fields_ = (
                                ("type", wintypes.DWORD),
                                ("union", INPUT_union)
                            )
                        
                        # For each repeat, send mouse input
                        for _ in range(repeat):
                            # Move mouse to position
                            move_input = INPUT(type=0)  # INPUT_MOUSE
                            move_input.union.mi.dx = normalized_x
                            move_input.union.mi.dy = normalized_y
                            move_input.union.mi.mouseData = 0
                            move_input.union.mi.dwFlags = MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE
                            move_input.union.mi.time = 0
                            move_input.union.mi.dwExtraInfo = ctypes.pointer(ctypes.c_ulong(0))
                            
                            # Mouse down input
                            down_input = INPUT(type=0)  # INPUT_MOUSE
                            down_input.union.mi.dx = normalized_x
                            down_input.union.mi.dy = normalized_y
                            down_input.union.mi.mouseData = 0
                            down_input.union.mi.dwFlags = (MOUSEEVENTF_LEFTDOWN if button.upper() == "LEFT" else MOUSEEVENTF_RIGHTDOWN) | MOUSEEVENTF_ABSOLUTE
                            down_input.union.mi.time = 0
                            down_input.union.mi.dwExtraInfo = ctypes.pointer(ctypes.c_ulong(0))
                            
                            # Mouse up input
                            up_input = INPUT(type=0)  # INPUT_MOUSE
                            up_input.union.mi.dx = normalized_x
                            up_input.union.mi.dy = normalized_y
                            up_input.union.mi.mouseData = 0
                            up_input.union.mi.dwFlags = (MOUSEEVENTF_LEFTUP if button.upper() == "LEFT" else MOUSEEVENTF_RIGHTUP) | MOUSEEVENTF_ABSOLUTE
                            up_input.union.mi.time = 0
                            up_input.union.mi.dwExtraInfo = ctypes.pointer(ctypes.c_ulong(0))
                            
                            # Send inputs
                            ctypes.windll.user32.SendInput(1, ctypes.byref(move_input), ctypes.sizeof(INPUT))
                            time.sleep(0.01)
                            ctypes.windll.user32.SendInput(1, ctypes.byref(down_input), ctypes.sizeof(INPUT))
                            time.sleep(0.01)
                            ctypes.windll.user32.SendInput(1, ctypes.byref(up_input), ctypes.sizeof(INPUT))
                            time.sleep(0.03)  # Small delay between clicks
                        
                        # Restore previous foreground window
                        win32gui.SetForegroundWindow(prev_foreground)
                    except Exception as e:
                        logger.warning(f"SendInput fallback failed: {e}")
                        # Continue execution even if this fails
            finally:
                # Detach thread input if we attached
                if attached:
                    win32process.AttachThreadInput(current_thread, target_thread, False)
                    
            logger.debug(f"Sent click to window at ({x}, {y}) using enhanced input methods")
                
        except Exception as e:
            logger.error(f"Error sending click to window: {e}")
            raise
                
        except Exception as e:
            logger.error(f"Error sending key to window: {e}")
            raise
            
    def _send_key_to_window(self, hwnd, key):
        """
        Send a keyboard key to a specific window without changing focus using both PostMessage
        and SendInput for better reliability with game clients
        Args:
            hwnd: Window handle
            key: Key to send (e.g., 'f1', 'a', etc.)
        """
        try:
            # Map function keys to virtual key codes
            vk_map = {
                'f1': win32con.VK_F1,
                'f2': win32con.VK_F2,
                'f3': win32con.VK_F3,
                'f4': win32con.VK_F4,
                'f5': win32con.VK_F5,
                'f6': win32con.VK_F6,
                'f7': win32con.VK_F7,
                'f8': win32con.VK_F8,
                'f9': win32con.VK_F9,
                'f10': win32con.VK_F10,
                'f11': win32con.VK_F11,
                'f12': win32con.VK_F12,
            }
            
            # Get the virtual key code for the key
            vk_code = vk_map.get(key.lower())
            if not vk_code:
                logger.error(f"Unsupported key: {key}")
                return
            
            # Define Windows message constants
            WM_KEYDOWN = 0x0100
            WM_KEYUP = 0x0101
            
            # Get the scan code for the virtual key
            scan_code = win32api.MapVirtualKey(vk_code, 0)
            
            # Create proper lParam for the key message
            # Bits 0-15: Repeat count (always 1)
            # Bits 16-23: Scan code
            # Bit 24: Extended key flag (1 for function keys)
            # Bit 25-28: Reserved
            # Bit 29: Context code (0)
            # Bit 30: Previous key state (0 for keydown, 1 for keyup)
            # Bit 31: Transition state (0 for keydown, 1 for keyup)
            
            # For function keys, set the extended key flag (bit 24)
            extended_key = 1 if key.lower().startswith('f') else 0
            
            # Create lParam for key down (bit 30 and 31 are 0)
            lParam_down = 1 | (scan_code << 16) | (extended_key << 24)
            
            # Create lParam for key up (bit 30 and 31 are 1)
            lParam_up = 1 | (scan_code << 16) | (extended_key << 24) | (1 << 30) | (1 << 31)
            
            # First, try to attach to the window's thread
            current_thread = win32api.GetCurrentThreadId()
            target_thread = win32process.GetWindowThreadProcessId(hwnd)[0]
            attached = False
            
            try:
                # Attach to the window's thread input queue
                if current_thread != target_thread:
                    attached = win32process.AttachThreadInput(current_thread, target_thread, True)
                
                # Send key down and key up messages directly to the window
                # Using PostMessage which doesn't require the window to be in foreground
                win32gui.PostMessage(hwnd, WM_KEYDOWN, vk_code, lParam_down)
                time.sleep(0.01)  # Reduced delay between key down and key up
                win32gui.PostMessage(hwnd, WM_KEYUP, vk_code, lParam_up)
                
                # For game clients, also try SendInput as a backup method
                # Define input structure for SendInput
                KEYEVENTF_EXTENDEDKEY = 0x0001
                KEYEVENTF_KEYUP = 0x0002
                
                # Create input structures for key down and key up
                # Use ctypes for SendInput
                import ctypes
                from ctypes import wintypes
                
                # Define input structure
                class KEYBDINPUT(ctypes.Structure):
                    _fields_ = (
                        ("wVk", wintypes.WORD),
                        ("wScan", wintypes.WORD),
                        ("dwFlags", wintypes.DWORD),
                        ("time", wintypes.DWORD),
                        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))
                    )
                
                class MOUSEINPUT(ctypes.Structure):
                    _fields_ = (
                        ("dx", wintypes.LONG),
                        ("dy", wintypes.LONG),
                        ("mouseData", wintypes.DWORD),
                        ("dwFlags", wintypes.DWORD),
                        ("time", wintypes.DWORD),
                        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))
                    )
                
                class HARDWAREINPUT(ctypes.Structure):
                    _fields_ = (
                        ("uMsg", wintypes.DWORD),
                        ("wParamL", wintypes.WORD),
                        ("wParamH", wintypes.WORD)
                    )
                
                class INPUT_union(ctypes.Union):
                    _fields_ = (
                        ("ki", KEYBDINPUT),
                        ("mi", MOUSEINPUT),
                        ("hi", HARDWAREINPUT)
                    )
                
                class INPUT(ctypes.Structure):
                    _fields_ = (
                        ("type", wintypes.DWORD),
                        ("union", INPUT_union)
                    )
                
                # Set foreground window temporarily
                if attached:
                    # Only set foreground if we successfully attached
                    prev_foreground = win32gui.GetForegroundWindow()
                    try:
                        win32gui.SetForegroundWindow(hwnd)
                        
                        # Prepare key down input
                        x = INPUT(type=1)  # INPUT_KEYBOARD
                        x.union.ki.wVk = vk_code
                        x.union.ki.wScan = scan_code
                        x.union.ki.dwFlags = KEYEVENTF_EXTENDEDKEY if extended_key else 0
                        x.union.ki.time = 0
                        x.union.ki.dwExtraInfo = ctypes.pointer(ctypes.c_ulong(0))
                        
                        # Prepare key up input
                        y = INPUT(type=1)  # INPUT_KEYBOARD
                        y.union.ki.wVk = vk_code
                        y.union.ki.wScan = scan_code
                        y.union.ki.dwFlags = KEYEVENTF_KEYUP | (KEYEVENTF_EXTENDEDKEY if extended_key else 0)
                        y.union.ki.time = 0
                        y.union.ki.dwExtraInfo = ctypes.pointer(ctypes.c_ulong(0))
                        
                        # Send inputs with reduced delay
                        ctypes.windll.user32.SendInput(1, ctypes.byref(x), ctypes.sizeof(INPUT))
                        time.sleep(0.01)
                        ctypes.windll.user32.SendInput(1, ctypes.byref(y), ctypes.sizeof(INPUT))
                        
                        # Restore previous foreground window
                        win32gui.SetForegroundWindow(prev_foreground)
                    except Exception as e:
                        logger.warning(f"SendInput fallback failed: {e}")
                        # Continue execution even if this fails
            finally:
                # Detach thread input if we attached
                if attached:
                    win32process.AttachThreadInput(current_thread, target_thread, False)
            
            logger.debug(f"Sent key {key} to window using enhanced input methods")
                
        except Exception as e:
            logger.error(f"Error sending key to window: {e}")
            raise
    
    def set_selected_windows(self, windows):
        """
        Set the list of selected windows
        Args:
            windows: List of window dictionaries with hwnd and title
        """
        self.selected_windows = windows
        logger.info(f"Set {len(windows)} selected windows for hotkey targeting")
        
    def set_key_delay(self, delay):
        """
        Set the delay between sending actions to multiple clients
        Args:
            delay: Delay in seconds
        """
        self.key_delay = delay
        logger.info(f"Set key delay to {delay} seconds")
        
    def set_pause_state(self, paused):
        """
        Set the pause state for multiclient actions
        Args:
            paused: True to pause actions, False to resume
        """
        self.paused = paused
        logger.info(f"{'Paused' if paused else 'Resumed'} client actions")
    
    def save_analytics(self):
        """Save analytics data to file"""
        try:
            analytics_file = "analytics.json"
            
            # Load existing analytics if file exists
            existing_analytics = []
            if os.path.exists(analytics_file):
                with open(analytics_file, 'r') as f:
                    existing_analytics = json.load(f)
            
            # Add current session analytics
            existing_analytics.append(self.analytics)
            
            # Save updated analytics
            with open(analytics_file, 'w') as f:
                json.dump(existing_analytics, f, indent=2)
                
            logger.debug("Analytics saved successfully")
            
        except Exception as e:
            logger.error(f"Error saving analytics: {e}")

def emergency_stop(manager):
    """Emergency stop function"""
    logger.warning("Emergency stop triggered!")
    if hasattr(manager, 'stop'):
        manager.stop()
        manager.save_analytics()
    sys.exit(0)

def launch_gui():
    """Launch the GUI application"""
    try:
        # Import GUI components here to avoid circular imports
        logger.info("Starting application in GUI mode")
        # Use subprocess to launch gui.py to avoid import issues
        import subprocess
        subprocess.Popen([sys.executable, 'gui.py'])
        # Exit this process as the GUI will run in its own process
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error launching GUI: {e}")
        logger.info("Falling back to console mode")
        launch_console()

def launch_console():
    """Launch the application in console mode"""
    try:
        # Check license first
        license_manager = check_license_and_activate()
        if not license_manager.is_licensed:
            logger.error("Valid license required to run in console mode")
            sys.exit(1)
            
        # Set up emergency stop hotkey
        keyboard.add_hotkey('ctrl+shift+x', lambda: emergency_stop(manager))
        
        # Create and start hotkey manager
        manager = HotkeyManager()
        manager.start()
        
        # Keep the main thread running with status updates
        logger.info("Application running in console mode. Press Ctrl+Shift+X to exit.")
        logger.info("To use the GUI version, run 'python gui.py' instead.")
        while True:
            try:
                time.sleep(60)  # Check status every minute
                # Log periodic status update
                uptime = datetime.now() - manager.start_time
                logger.info(f"Status: Running for {uptime}, Total executions: {manager.analytics['total_executions']}")
            except KeyboardInterrupt:
                break
    except Exception as e:
        logger.error(f"Unexpected error in console mode: {e}")
        sys.exit(1)

def main():
    """Enhanced main entry point with better error handling"""
    try:
        # Check for command line arguments
        if len(sys.argv) > 1 and sys.argv[1].lower() in ['-c', '--console']:
            # Run in console mode if specified
            launch_console()
        else:
            # Default to GUI mode
            launch_gui()
            
    except Exception as e:
        logger.error(f"Unexpected error in main: {e}")
    finally:
        try:
            # Cleanup only needed for console mode
            # GUI mode handles its own cleanup
            if 'manager' in locals() and hasattr(manager, 'stop'):
                manager.stop()
                manager.save_analytics()
                logger.info("Application stopped gracefully")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

if __name__ == "__main__":
    main()
