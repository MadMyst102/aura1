import os
import json
import shutil
from typing import Dict, Any, List, Optional
from loguru import logger

class ProfileManager:
    """Manages configuration profiles for different games/applications"""
    
    def __init__(self, profiles_dir: str = "profiles"):
        """Initialize the profile manager
        
        Args:
            profiles_dir: Directory to store profile configurations
        """
        self.profiles_dir = profiles_dir
        self.default_config_path = "config.json"
        self.current_profile = "default"
        
        # Ensure profiles directory exists
        if not os.path.exists(self.profiles_dir):
            os.makedirs(self.profiles_dir)
            logger.info(f"Created profiles directory: {self.profiles_dir}")
        
        # Create default profile if it doesn't exist
        self._ensure_default_profile()
    
    def _ensure_default_profile(self):
        """Ensure the default profile exists"""
        default_profile_path = os.path.join(self.profiles_dir, "default.json")
        
        if not os.path.exists(default_profile_path):
            # Copy current config to default profile if it exists
            if os.path.exists(self.default_config_path):
                shutil.copy2(self.default_config_path, default_profile_path)
                logger.info("Created default profile from existing configuration")
            else:
                # Create empty default profile
                with open(default_profile_path, 'w') as f:
                    json.dump({
                        "char_settings": {},
                        "hotkeys": {}
                    }, f, indent=2)
                logger.info("Created empty default profile")
    
    def get_profiles(self) -> List[str]:
        """Get list of available profiles
        
        Returns:
            List of profile names (without .json extension)
        """
        profiles = []
        for filename in os.listdir(self.profiles_dir):
            if filename.endswith(".json"):
                profiles.append(filename[:-5])  # Remove .json extension
        return sorted(profiles)
    
    def load_profile(self, profile_name: str) -> Dict[str, Any]:
        """Load a profile configuration
        
        Args:
            profile_name: Name of the profile to load
            
        Returns:
            Dictionary containing profile configuration
        """
        profile_path = os.path.join(self.profiles_dir, f"{profile_name}.json")
        
        if not os.path.exists(profile_path):
            logger.error(f"Profile not found: {profile_name}")
            return {}
        
        try:
            with open(profile_path, 'r') as f:
                config = json.load(f)
            
            # Update current profile
            self.current_profile = profile_name
            
            # Also update main config file
            with open(self.default_config_path, 'w') as f:
                json.dump(config, f, indent=2)
                
            logger.info(f"Loaded profile: {profile_name}")
            return config
            
        except Exception as e:
            logger.error(f"Error loading profile {profile_name}: {e}")
            return {}
    
    def save_profile(self, profile_name: str, config: Dict[str, Any]) -> bool:
        """Save configuration as a profile
        
        Args:
            profile_name: Name to save the profile as
            config: Configuration dictionary to save
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            profile_path = os.path.join(self.profiles_dir, f"{profile_name}.json")
            
            with open(profile_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            # Update current profile
            self.current_profile = profile_name
            
            logger.info(f"Saved profile: {profile_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving profile {profile_name}: {e}")
            return False
    
    def delete_profile(self, profile_name: str) -> bool:
        """Delete a profile
        
        Args:
            profile_name: Name of the profile to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        if profile_name == "default":
            logger.error("Cannot delete the default profile")
            return False
            
        try:
            profile_path = os.path.join(self.profiles_dir, f"{profile_name}.json")
            
            if not os.path.exists(profile_path):
                logger.error(f"Profile not found: {profile_name}")
                return False
            
            os.remove(profile_path)
            logger.info(f"Deleted profile: {profile_name}")
            
            # If current profile was deleted, switch to default
            if self.current_profile == profile_name:
                self.current_profile = "default"
                self.load_profile("default")
                
            return True
            
        except Exception as e:
            logger.error(f"Error deleting profile {profile_name}: {e}")
            return False
    
    def rename_profile(self, old_name: str, new_name: str) -> bool:
        """Rename a profile
        
        Args:
            old_name: Current profile name
            new_name: New profile name
            
        Returns:
            bool: True if successful, False otherwise
        """
        if old_name == "default":
            logger.error("Cannot rename the default profile")
            return False
            
        try:
            old_path = os.path.join(self.profiles_dir, f"{old_name}.json")
            new_path = os.path.join(self.profiles_dir, f"{new_name}.json")
            
            if not os.path.exists(old_path):
                logger.error(f"Profile not found: {old_name}")
                return False
                
            if os.path.exists(new_path):
                logger.error(f"Profile already exists: {new_name}")
                return False
            
            shutil.move(old_path, new_path)
            
            # Update current profile if needed
            if self.current_profile == old_name:
                self.current_profile = new_name
                
            logger.info(f"Renamed profile from {old_name} to {new_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error renaming profile {old_name} to {new_name}: {e}")
            return False
    
    def get_current_profile(self) -> str:
        """Get the name of the currently active profile
        
        Returns:
            Current profile name
        """
        return self.current_profile

# Singleton instance
_profile_manager = None

def get_profile_manager() -> ProfileManager:
    """Get the singleton profile manager instance
    
    Returns:
        ProfileManager instance
    """
    global _profile_manager
    if _profile_manager is None:
        _profile_manager = ProfileManager()
    return _profile_manager