import json
import os
from typing import Dict, Any
from loguru import logger

class ConfigManager:
    def __init__(self, config_path: str = "config.json"):
        self.config_path = config_path
        self.setup_logger()
        
    def setup_logger(self):
        """Initialize logger configuration"""
        logger.remove()  # Remove default handler
        
        # Add file handler for debugging
        log_path = "app.log"
        logger.add(log_path, 
                  rotation="10 MB",
                  retention="1 week",
                  level="DEBUG",
                  format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}")
        
        # Add console handler for info
        logger.add(lambda msg: print(msg), level="INFO", format="{message}")
    
    def load_config(self) -> Dict[str, Any]:
        """
        Load configuration from JSON file
        Returns: Dictionary containing configuration
        """
        try:
            if not os.path.exists(self.config_path):
                logger.error(f"Configuration file not found: {self.config_path}")
                return self._get_default_config()
            
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            
            # Validate configuration
            if not self._validate_config(config):
                logger.warning("Invalid configuration found, using default")
                return self._get_default_config()
            
            logger.info("Configuration loaded successfully")
            return config
            
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON configuration: {e}")
            return self._get_default_config()
        except Exception as e:
            logger.error(f"Unexpected error loading configuration: {e}")
            return self._get_default_config()
    
    def save_config(self, config: Dict[str, Any]) -> bool:
        """
        Save configuration to JSON file
        Args:
            config: Dictionary containing configuration
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self._validate_config(config):
                logger.error("Invalid configuration, not saving")
                return False
            
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            logger.info("Configuration saved successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
            return False
    
    def _validate_config(self, config: Dict[str, Any]) -> bool:
        """
        Validate configuration structure
        Args:
            config: Dictionary containing configuration
        Returns:
            bool: True if valid, False otherwise
        """
        try:
            # Check for required top-level keys
            required_keys = {"char_settings", "hotkeys"}
            if not all(key in config for key in required_keys):
                logger.error("Missing required configuration keys")
                return False
            
            # Validate char_settings
            if not isinstance(config["char_settings"], dict):
                logger.error("char_settings must be a dictionary")
                return False
            
            # Validate hotkeys
            if not isinstance(config["hotkeys"], dict):
                logger.error("hotkeys must be a dictionary")
                return False
            
            # Validate each hotkey action
            for hotkey, actions in config["hotkeys"].items():
                if not isinstance(actions, list):
                    logger.error(f"Actions for hotkey {hotkey} must be a list")
                    return False
                
                for action in actions:
                    required_action_keys = {"x", "y", "button", "repeat", "char"}
                    if not all(key in action for key in required_action_keys):
                        logger.error(f"Missing required keys in action for hotkey {hotkey}")
                        return False
                    
                    # Validate action values
                    if not isinstance(action["x"], (int, float)):
                        logger.error(f"Invalid x coordinate in hotkey {hotkey}")
                        return False
                    if not isinstance(action["y"], (int, float)):
                        logger.error(f"Invalid y coordinate in hotkey {hotkey}")
                        return False
                    if action["button"] != "LEFT":
                        logger.error(f"Invalid button type in hotkey {hotkey}")
                        return False
                    if not isinstance(action["repeat"], int) or action["repeat"] < 1:
                        logger.error(f"Invalid repeat count in hotkey {hotkey}")
                        return False
                    if not isinstance(action["char"], str):
                        logger.error(f"Invalid char reference in hotkey {hotkey}")
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating configuration: {e}")
            return False
    
    def _get_default_config(self) -> Dict[str, Any]:
        """
        Return default configuration
        Returns:
            Dict containing default configuration
        """
        return {
            "char_settings": {
                "char1": "U8",
                "char2": "wekwok",
                "char3": "Uboring",
                "char4": "U9",
                "char5": ""
            },
            "hotkeys": {
                "f1": [
                    {"x": 490, "y": 711, "button": "LEFT", "repeat": 1, "char": "char1"}
                ]
            }
        }

def get_config_manager() -> ConfigManager:
    """
    Get singleton instance of ConfigManager
    Returns:
        ConfigManager instance
    """
    if not hasattr(get_config_manager, "instance"):
        get_config_manager.instance = ConfigManager()
    return get_config_manager.instance