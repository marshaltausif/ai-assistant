import os
from dataclasses import dataclass

@dataclass
class Config:
    # LLM Settings
    LLM_MODEL: str = "gemma:4b"  # or "mistral:latest", "llama2:latest"
    LLM_TIMEOUT: int = 30
    
    # Voice Settings
    VOICE_ENABLED: bool = True
    VOICE_OUTPUT: bool = True
    ALWAYS_VOICE: bool = False
    
    # Execution Settings
    STOP_ON_FAILURE: bool = False
    AUTO_SAVE_WEB_CONTENT: bool = True
    MAX_FILE_SIZE_MB: int = 10
    
    # Sandbox Settings
    SANDBOX_PATH: str = "AutoBox"
    ALLOWED_FOLDERS: list = None
    
    # Web Settings
    HEADLESS_BROWSER: bool = True
    WEB_TIMEOUT: int = 30
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/assistant.log"
    
    def __post_init__(self):
        if self.ALLOWED_FOLDERS is None:
            self.ALLOWED_FOLDERS = ["AB1", "AB2", "AB3"]
        
        # Create necessary directories
        os.makedirs(self.SANDBOX_PATH, exist_ok=True)
        for folder in self.ALLOWED_FOLDERS:
            os.makedirs(os.path.join(self.SANDBOX_PATH, folder), exist_ok=True)
        
        os.makedirs("logs", exist_ok=True)