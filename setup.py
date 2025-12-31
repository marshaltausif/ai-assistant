#!/usr/bin/env python3
"""
Setup script for AI Assistant
"""

import os
import sys
import subprocess
import platform

def run_command(cmd, description):
    """Run a shell command and check result"""
    print(f"\n📦 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("   ✅ Done")
            return True
        else:
            print(f"   ❌ Failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def check_python():
    """Check Python version"""
    print("🐍 Checking Python version...")
    if sys.version_info < (3, 8):
        print(f"   ❌ Python 3.8+ required, found {sys.version}")
        return False
    print(f"   ✅ Python {sys.version}")
    return True

def install_dependencies():
    """Install Python dependencies"""
    print("\n📚 Installing dependencies...")
    
    # Create virtual environment
    if not os.path.exists(".venv"):
        run_command("python -m venv .venv", "Creating virtual environment")
    
    # Determine pip path
    pip_path = ".venv/Scripts/pip" if platform.system() == "Windows" else ".venv/bin/pip"
    
    # Install requirements
    if os.path.exists("requirements.txt"):
        success = run_command(f"{pip_path} install -r requirements.txt", "Installing packages")
        if not success:
            print("   ⚠️ Trying with pip3...")
            run_command("pip3 install -r requirements.txt", "Installing with pip3")
    else:
        print("   ❌ requirements.txt not found")
        return False
    
    return True

def install_ollama():
    """Install Ollama if not present"""
    print("\n🤖 Checking Ollama...")
    
    # Check if Ollama is installed
    try:
        subprocess.run(["ollama", "--version"], capture_output=True, check=True)
        print("   ✅ Ollama already installed")
    except (subprocess.SubprocessError, FileNotFoundError):
        print("   ⚠️ Ollama not found")
        
        system = platform.system()
        
        if system == "Windows":
            print("   Downloading Ollama for Windows...")
            # Download and install Ollama
            ollama_url = "https://ollama.com/download/OllamaSetup.exe"
            run_command(f'powershell -Command "Invoke-WebRequest -Uri {ollama_url} -OutFile OllamaSetup.exe"', "Downloading")
            run_command("OllamaSetup.exe", "Installing (follow prompts)")
            
        elif system == "Darwin":  # macOS
            run_command("/bin/bash -c \"$(curl -fsSL https://ollama.com/install.sh)\"", "Installing Ollama")
            
        else:  # Linux
            run_command("curl -fsSL https://ollama.com/install.sh | sh", "Installing Ollama")
    
    # Pull default model
    print("\n📥 Downloading LLM model...")
    run_command("ollama pull gemma:4b", "Downloading Gemma 4B model")
    
    return True

def install_ffmpeg():
    """Install FFmpeg for voice processing"""
    print("\n🎵 Checking FFmpeg...")
    
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        print("   ✅ FFmpeg already installed")
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        print("   ⚠️ FFmpeg not found")
        
        system = platform.system()
        
        if system == "Windows":
            print("   Installing FFmpeg via Chocolatey...")
            # Install Chocolatey if not present
            try:
                subprocess.run(["choco", "--version"], capture_output=True)
            except FileNotFoundError:
                print("   Installing Chocolatey...")
                run_command(
                    'powershell -Command "Set-ExecutionPolicy Bypass -Scope Process -Force; '
                    '[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; '
                    'iex ((New-Object System.Net.WebClient).DownloadString(\'https://community.chocolatey.org/install.ps1\'))"',
                    "Installing Chocolatey"
                )
            
            run_command("choco install ffmpeg -y", "Installing FFmpeg")
            
        elif system == "Darwin":
            run_command("brew install ffmpeg", "Installing FFmpeg")
            
        else:  # Linux
            run_command("sudo apt-get install ffmpeg -y", "Installing FFmpeg")
        
        return True

def setup_autobox():
    """Create AutoBox directory structure"""
    print("\n📁 Setting up AutoBox sandbox...")
    
    autobox_path = "AutoBox"
    folders = ["AB1", "AB2", "AB3"]
    
    try:
        for folder in folders:
            path = os.path.join(autobox_path, folder)
            os.makedirs(path, exist_ok=True)
            print(f"   ✅ Created: {path}")
        
        # Create sample files
        sample_files = {
            "AB1/readme.txt": "This is AB1 folder for file operations.",
            "AB2/notes.txt": "AB2 folder - use for web content storage.",
            "AB3/temp.txt": "AB3 folder - temporary or experimental files."
        }
        
        for filepath, content in sample_files.items():
            full_path = os.path.join(autobox_path, filepath)
            with open(full_path, 'w') as f:
                f.write(content)
        
        print("   ✅ Created sample files")
        return True
        
    except Exception as e:
        print(f"   ❌ Failed to create AutoBox: {e}")
        return False

def setup_browser_driver():
    """Setup Chrome/Chromium driver for web automation"""
    print("\n🌐 Setting up browser automation...")
    
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        
        # This will automatically download and setup ChromeDriver
        driver_path = ChromeDriverManager().install()
        print(f"   ✅ ChromeDriver installed: {driver_path}")
        
        # Test with headless browser
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        service = Service(driver_path)
        driver = webdriver.Chrome(service=service, options=options)
        driver.quit()
        
        print("   ✅ Browser automation configured")
        return True
        
    except Exception as e:
        print(f"   ⚠️ Browser automation setup failed: {e}")
        print("   Some web features may not work fully")
        return False

def create_config():
    """Create default configuration"""
    print("\n⚙️ Creating configuration...")
    
    config_content = """# AI Assistant Configuration
VOICE_ENABLED = True
LLM_MODEL = "gemma:4b"
SANDBOX_PATH = "AutoBox"
LOG_LEVEL = "INFO"
"""
    
    try:
        with open("config.py", "w") as f:
            f.write(config_content)
        print("   ✅ Configuration created")
        return True
    except Exception as e:
        print(f"   ❌ Failed to create config: {e}")
        return False

def run_quick_test():
    """Run a quick test to verify setup"""
    print("\n🧪 Running quick test...")
    
    try:
        # Test basic imports
        import pyttsx3
        import whisper
        import numpy
        import requests
        import pyperclip
        
        print("   ✅ All dependencies imported successfully")
        
        # Test AutoBox
        if os.path.exists("AutoBox/AB1"):
            print("   ✅ AutoBox structure verified")
        else:
            print("   ❌ AutoBox missing")
            return False
        
        return True
        
    except ImportError as e:
        print(f"   ❌ Missing dependency: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        return False

def main():
    """Main setup function"""
    print("=" * 60)
    print("🤖 ADVANCED AI ASSISTANT SETUP")
    print("=" * 60)
    
    # Check prerequisites
    if not check_python():
        return 1
    
    # Installation steps
    steps = [
        ("Installing Python dependencies", install_dependencies),
        ("Installing Ollama", install_ollama),
        ("Installing FFmpeg", install_ffmpeg),
        ("Setting up AutoBox", setup_autobox),
        ("Setting up browser automation", setup_browser_driver),
        ("Creating configuration", create_config),
    ]
    
    all_success = True
    
    for step_name, step_func in steps:
        if not step_func():
            print(f"\n⚠️ {step_name} failed")
            all_success = False
    
    # Run test
    if all_success:
        print("\n" + "=" * 60)
        print("✅ SETUP COMPLETE")
        print("=" * 60)
        
        if run_quick_test():
            print("\n🎉 Ready to use! Run: python run.py")
            print("\n📚 Quick Start:")
            print("   1. Make sure Ollama is running: ollama serve")
            print("   2. Start the assistant: python run.py")
            print("   3. Try commands like:")
            print("      - 'create a file test.txt in AB1'")
            print("      - 'open google.com'")
            print("      - 'search for AI news'")
        else:
            print("\n⚠️ Setup completed with warnings")
            all_success = False
    else:
        print("\n" + "=" * 60)
        print("❌ SETUP FAILED")
        print("=" * 60)
        print("Some components failed to install.")
        print("Check the messages above and try manual installation.")
    
    return 0 if all_success else 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️ Setup interrupted by user")
        sys.exit(1)