# shadow_core/automation.py
"""
Automation module for Shadow AI Agent - Full computer control capabilities
File system, applications, web browsing, system commands, GUI automation
"""

import logging
import asyncio
import os
import sys
import subprocess
import platform
import psutil
from typing import Dict, List, Optional, Any
from pathlib import Path
import webbrowser
import time
import pyautogui
import pyperclip
from datetime import datetime
import json

# Import optional dependencies with fallbacks
try:
    import pygetwindow as gw
    HAS_PYGETWINDOW = True
except ImportError:
    HAS_PYGETWINDOW = False

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    HAS_SELENIUM = True
except ImportError:
    HAS_SELENIUM = False

logger = logging.getLogger(__name__)

class ComputerControl:
    """Main computer control class with full system automation capabilities"""
    
    def __init__(self):
        self.system = platform.system().lower()
        self.pyautogui_failsafe = True
        pyautogui.FAILSAFE = self.pyautogui_failsafe
        pyautogui.PAUSE = 0.1
        
        # Initialize components
        self.file_manager = FileManager()
        self.app_controller = ApplicationController()
        self.web_automator = WebAutomator()
        self.system_monitor = SystemMonitor()
        self.gui_controller = GUIController()
        
        logger.info(f"Computer Control initialized for {self.system}")
    
    async def execute_command(self, command: str, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute automation command with parameters
        Returns: Dict with success status and results
        """
        try:
            command = command.lower().strip()
            parameters = parameters or {}
            
            # File system commands
            if command in ["open_file", "read_file", "write_file", "list_files", 
                          "create_file", "delete_file", "search_files"]:
                return await self.file_manager.handle_command(command, parameters)
            
            # Application commands
            elif command in ["open_app", "close_app", "list_apps", "kill_app", 
                           "focus_app", "install_app"]:
                return await self.app_controller.handle_command(command, parameters)
            
            # Web automation commands
            elif command in ["open_url", "web_search", "click_element", "fill_form",
                           "screenshot", "scrape_data"]:
                return await self.web_automator.handle_command(command, parameters)
            
            # System commands
            elif command in ["system_info", "shutdown", "restart", "sleep", 
                           "volume", "brightness", "network_info"]:
                return await self._handle_system_command(command, parameters)
            
            # GUI automation commands
            elif command in ["click", "type", "hotkey", "screenshot", "locate",
                           "drag", "scroll", "position"]:
                return await self.gui_controller.handle_command(command, parameters)
            
            # Custom automation sequences
            elif command in ["automate", "sequence", "macro"]:
                return await self._execute_automation_sequence(parameters)
            
            else:
                return {"success": False, "error": f"Unknown command: {command}"}
                
        except Exception as e:
            logger.error(f"Automation command error: {e}")
            return {"success": False, "error": str(e)}
    
    async def _handle_system_command(self, command: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle system-level commands"""
        try:
            if command == "system_info":
                return self.system_monitor.get_system_info()
            
            elif command == "shutdown":
                return await self._shutdown_system(parameters.get("delay", 0))
            
            elif command == "restart":
                return await self._restart_system(parameters.get("delay", 0))
            
            elif command == "sleep":
                return await self._sleep_system()
            
            elif command == "volume":
                return await self._control_volume(parameters.get("level"), parameters.get("action"))
            
            elif command == "brightness":
                return await self._control_brightness(parameters.get("level"))
            
            elif command == "network_info":
                return self.system_monitor.get_network_info()
            
            else:
                return {"success": False, "error": f"Unknown system command: {command}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _shutdown_system(self, delay: int = 0) -> Dict[str, Any]:
        """Shutdown the computer"""
        try:
            if self.system == "windows":
                cmd = f"shutdown /s /t {delay}"
            elif self.system == "darwin":  # macOS
                cmd = f"sudo shutdown -h +{delay//60}" if delay > 0 else "sudo shutdown -h now"
            else:  # linux
                cmd = f"shutdown -h +{delay//60}" if delay > 0 else "shutdown -h now"
            
            subprocess.run(cmd, shell=True)
            return {"success": True, "message": f"System will shutdown in {delay} seconds"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _restart_system(self, delay: int = 0) -> Dict[str, Any]:
        """Restart the computer"""
        try:
            if self.system == "windows":
                cmd = f"shutdown /r /t {delay}"
            elif self.system == "darwin":
                cmd = f"sudo shutdown -r +{delay//60}" if delay > 0 else "sudo shutdown -r now"
            else:
                cmd = f"shutdown -r +{delay//60}" if delay > 0 else "shutdown -r now"
            
            subprocess.run(cmd, shell=True)
            return {"success": True, "message": f"System will restart in {delay} seconds"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _sleep_system(self) -> Dict[str, Any]:
        """Put system to sleep"""
        try:
            if self.system == "windows":
                subprocess.run("rundll32.exe powrprof.dll,SetSuspendState 0,1,0", shell=True)
            elif self.system == "darwin":
                subprocess.run("pmset sleepnow", shell=True)
            else:
                subprocess.run("systemctl suspend", shell=True)
            
            return {"success": True, "message": "System going to sleep"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _control_volume(self, level: int = None, action: str = None) -> Dict[str, Any]:
        """Control system volume"""
        try:
            if level is not None:
                if self.system == "windows":
                    subprocess.run(f"nircmd setsysvolume {level*655}", shell=True)
                elif self.system == "darwin":
                    subprocess.run(f"osascript -e 'set volume output volume {level}'", shell=True)
                else:
                    subprocess.run(f"amixer set Master {level}%", shell=True)
                return {"success": True, "message": f"Volume set to {level}%"}
            
            elif action:
                if action == "mute":
                    if self.system == "windows":
                        subprocess.run("nircmd mutesysvolume 1", shell=True)
                    elif self.system == "darwin":
                        subprocess.run("osascript -e 'set volume output muted true'", shell=True)
                    else:
                        subprocess.run("amixer set Master mute", shell=True)
                    return {"success": True, "message": "Volume muted"}
                elif action == "unmute":
                    if self.system == "windows":
                        subprocess.run("nircmd mutesysvolume 0", shell=True)
                    elif self.system == "darwin":
                        subprocess.run("osascript -e 'set volume output muted false'", shell=True)
                    else:
                        subprocess.run("amixer set Master unmute", shell=True)
                    return {"success": True, "message": "Volume unmuted"}
            
            return {"success": False, "error": "Please specify volume level or action"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _control_brightness(self, level: int = None) -> Dict[str, Any]:
        """Control display brightness"""
        try:
            if level is None:
                return {"success": False, "error": "Please specify brightness level (0-100)"}
            
            if self.system == "windows":
                # Requires additional tools like nircmd or wmi
                subprocess.run(f"nircmd setbrightness {level}", shell=True)
            elif self.system == "darwin":
                subprocess.run(f"brightness {level/100}", shell=True)
            else:
                # Linux - varies by system
                subprocess.run(f"xrandr --output $(xrandr | grep ' connected' | cut -f1 -d' ') --brightness {level/100}", shell=True)
            
            return {"success": True, "message": f"Brightness set to {level}%"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _execute_automation_sequence(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a sequence of automation commands"""
        try:
            steps = parameters.get("steps", [])
            results = []
            
            for step in steps:
                command = step.get("command")
                step_params = step.get("parameters", {})
                
                result = await self.execute_command(command, step_params)
                results.append({
                    "command": command,
                    "success": result.get("success", False),
                    "result": result
                })
                
                # Short delay between steps
                await asyncio.sleep(0.5)
            
            return {
                "success": all(r["success"] for r in results),
                "results": results,
                "message": f"Executed {len(results)} automation steps"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}


class FileManager:
    """File system automation operations"""
    
    def __init__(self):
        self.home_dir = Path.home()
    
    async def handle_command(self, command: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle file system commands"""
        try:
            if command == "open_file":
                return self.open_file(parameters.get("path"))
            elif command == "read_file":
                return self.read_file(parameters.get("path"))
            elif command == "write_file":
                return self.write_file(parameters.get("path"), parameters.get("content"))
            elif command == "list_files":
                return self.list_files(parameters.get("path"), parameters.get("pattern"))
            elif command == "create_file":
                return self.create_file(parameters.get("path"))
            elif command == "delete_file":
                return self.delete_file(parameters.get("path"))
            elif command == "search_files":
                return self.search_files(parameters.get("path"), parameters.get("pattern"))
            else:
                return {"success": False, "error": f"Unknown file command: {command}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def open_file(self, file_path: str) -> Dict[str, Any]:
        """Open a file with default application"""
        try:
            if not file_path:
                return {"success": False, "error": "No file path provided"}
            
            full_path = self._resolve_path(file_path)
            if not full_path.exists():
                return {"success": False, "error": f"File not found: {file_path}"}
            
            os.startfile(full_path) if os.name == 'nt' else subprocess.run(['open', full_path])
            return {"success": True, "message": f"Opened file: {file_path}"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def read_file(self, file_path: str) -> Dict[str, Any]:
        """Read content from a file"""
        try:
            if not file_path:
                return {"success": False, "error": "No file path provided"}
            
            full_path = self._resolve_path(file_path)
            if not full_path.exists():
                return {"success": False, "error": f"File not found: {file_path}"}
            
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return {
                "success": True, 
                "content": content,
                "size": len(content),
                "message": f"Read {len(content)} characters from {file_path}"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def write_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """Write content to a file"""
        try:
            if not file_path:
                return {"success": False, "error": "No file path provided"}
            
            full_path = self._resolve_path(file_path)
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content or "")
            
            return {"success": True, "message": f"Written to file: {file_path}"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def list_files(self, directory: str = None, pattern: str = None) -> Dict[str, Any]:
        """List files in a directory"""
        try:
            dir_path = self._resolve_path(directory or ".")
            if not dir_path.exists():
                return {"success": False, "error": f"Directory not found: {directory}"}
            
            if pattern:
                files = list(dir_path.glob(pattern))
            else:
                files = list(dir_path.iterdir())
            
            file_list = []
            for f in files:
                file_list.append({
                    "name": f.name,
                    "path": str(f),
                    "is_file": f.is_file(),
                    "is_dir": f.is_dir(),
                    "size": f.stat().st_size if f.is_file() else 0,
                    "modified": f.stat().st_mtime
                })
            
            return {
                "success": True,
                "files": file_list,
                "count": len(file_list),
                "directory": str(dir_path)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def create_file(self, file_path: str) -> Dict[str, Any]:
        """Create a new file"""
        try:
            if not file_path:
                return {"success": False, "error": "No file path provided"}
            
            full_path = self._resolve_path(file_path)
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.touch()
            
            return {"success": True, "message": f"Created file: {file_path}"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def delete_file(self, file_path: str) -> Dict[str, Any]:
        """Delete a file or directory"""
        try:
            if not file_path:
                return {"success": False, "error": "No file path provided"}
            
            full_path = self._resolve_path(file_path)
            if not full_path.exists():
                return {"success": False, "error": f"Path not found: {file_path}"}
            
            if full_path.is_file():
                full_path.unlink()
            else:
                import shutil
                shutil.rmtree(full_path)
            
            return {"success": True, "message": f"Deleted: {file_path}"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def search_files(self, directory: str, pattern: str) -> Dict[str, Any]:
        """Search for files matching pattern"""
        try:
            dir_path = self._resolve_path(directory or ".")
            if not dir_path.exists():
                return {"success": False, "error": f"Directory not found: {directory}"}
            
            matches = list(dir_path.rglob(pattern))
            result_files = []
            
            for match in matches:
                result_files.append({
                    "name": match.name,
                    "path": str(match),
                    "is_file": match.is_file(),
                    "size": match.stat().st_size if match.is_file() else 0
                })
            
            return {
                "success": True,
                "files": result_files,
                "count": len(result_files),
                "pattern": pattern
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _resolve_path(self, path: str) -> Path:
        """Resolve a path to absolute path"""
        path_obj = Path(path)
        if not path_obj.is_absolute():
            path_obj = self.home_dir / path_obj
        return path_obj.resolve()


class ApplicationController:
    """Application management and control"""
    
    def __init__(self):
        self.system = platform.system().lower()
    
    async def handle_command(self, command: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle application commands"""
        try:
            if command == "open_app":
                return self.open_application(parameters.get("name"), parameters.get("path"))
            elif command == "close_app":
                return self.close_application(parameters.get("name"))
            elif command == "list_apps":
                return self.list_applications()
            elif command == "kill_app":
                return self.kill_application(parameters.get("name"))
            elif command == "focus_app":
                return self.focus_application(parameters.get("name"))
            elif command == "install_app":
                return await self.install_application(parameters.get("name"))
            else:
                return {"success": False, "error": f"Unknown app command: {command}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def open_application(self, app_name: str, app_path: str = None) -> Dict[str, Any]:
        """Open an application"""
        try:
            if app_path:
                # Open specific application path
                subprocess.Popen(app_path, shell=True)
                return {"success": True, "message": f"Opened application: {app_path}"}
            
            # Try to open by name
            if self.system == "windows":
                subprocess.Popen(f"start {app_name}", shell=True)
            elif self.system == "darwin":
                subprocess.Popen(f"open -a '{app_name}'", shell=True)
            else:
                subprocess.Popen(app_name, shell=True)
            
            return {"success": True, "message": f"Opened application: {app_name}"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def close_application(self, app_name: str) -> Dict[str, Any]:
        """Close an application"""
        try:
            if not app_name:
                return {"success": False, "error": "No application name provided"}
            
            if HAS_PYGETWINDOW:
                # Try to close by window title
                windows = gw.getWindowsWithTitle(app_name)
                for window in windows:
                    window.close()
                
                if windows:
                    return {"success": True, "message": f"Closed {len(windows)} instances of {app_name}"}
            
            # Fallback: kill process by name
            for proc in psutil.process_iter(['name']):
                if app_name.lower() in proc.info['name'].lower():
                    proc.kill()
            
            return {"success": True, "message": f"Attempted to close application: {app_name}"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def list_applications(self) -> Dict[str, Any]:
        """List running applications"""
        try:
            apps = []
            if HAS_PYGETWINDOW:
                windows = gw.getAllTitles()
                apps = [{"name": title, "type": "window"} for title in windows if title]
            else:
                # Fallback: list processes
                for proc in psutil.process_iter(['name', 'pid']):
                    apps.append({"name": proc.info['name'], "pid": proc.info['pid'], "type": "process"})
            
            return {
                "success": True,
                "applications": apps,
                "count": len(apps)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def kill_application(self, app_name: str) -> Dict[str, Any]:
        """Force kill an application"""
        try:
            if not app_name:
                return {"success": False, "error": "No application name provided"}
            
            killed = 0
            for proc in psutil.process_iter(['name', 'pid']):
                if app_name.lower() in proc.info['name'].lower():
                    try:
                        proc.kill()
                        killed += 1
                    except:
                        continue
            
            return {"success": True, "message": f"Killed {killed} processes of {app_name}"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def focus_application(self, app_name: str) -> Dict[str, Any]:
        """Focus/bring an application to front"""
        try:
            if not HAS_PYGETWINDOW:
                return {"success": False, "error": "pygetwindow not available for window management"}
            
            windows = gw.getWindowsWithTitle(app_name)
            if windows:
                windows[0].activate()
                return {"success": True, "message": f"Focused application: {app_name}"}
            else:
                return {"success": False, "error": f"Application not found: {app_name}"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def install_application(self, app_name: str) -> Dict[str, Any]:
        """Install an application (basic package manager support)"""
        try:
            if self.system == "windows":
                # Chocolatey or winget would be needed
                return {"success": False, "error": "Automatic installation requires package manager setup"}
            elif self.system == "darwin":
                # brew support
                result = subprocess.run(f"brew install {app_name}", shell=True, capture_output=True)
            else:
                # apt for Debian/Ubuntu
                result = subprocess.run(f"sudo apt install {app_name}", shell=True, capture_output=True)
            
            if result.returncode == 0:
                return {"success": True, "message": f"Installed application: {app_name}"}
            else:
                return {"success": False, "error": f"Installation failed: {result.stderr.decode()}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}


class WebAutomator:
    """Web browser automation and control"""
    
    def __init__(self):
        self.driver = None
    
    async def handle_command(self, command: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle web automation commands"""
        try:
            if command == "open_url":
                return self.open_url(parameters.get("url"))
            elif command == "web_search":
                return self.web_search(parameters.get("query"))
            elif command == "click_element":
                return await self.click_element(parameters.get("selector"), parameters.get("by"))
            elif command == "fill_form":
                return await self.fill_form(parameters.get("selector"), parameters.get("text"))
            elif command == "screenshot":
                return self.take_screenshot(parameters.get("path"))
            elif command == "scrape_data":
                return await self.scrape_data(parameters.get("selector"))
            else:
                return {"success": False, "error": f"Unknown web command: {command}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def open_url(self, url: str) -> Dict[str, Any]:
        """Open a URL in default browser"""
        try:
            if not url:
                return {"success": False, "error": "No URL provided"}
            
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            webbrowser.open(url)
            return {"success": True, "message": f"Opened URL: {url}"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def web_search(self, query: str) -> Dict[str, Any]:
        """Perform web search in default browser"""
        try:
            if not query:
                return {"success": False, "error": "No search query provided"}
            
            search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            webbrowser.open(search_url)
            return {"success": True, "message": f"Searching for: {query}"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def click_element(self, selector: str, by: str = "css") -> Dict[str, Any]:
        """Click a web element using Selenium"""
        try:
            if not HAS_SELENIUM:
                return {"success": False, "error": "Selenium not available for advanced web automation"}
            
            if not self.driver:
                self._init_driver()
            
            if by == "css":
                element = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                )
            elif by == "xpath":
                element = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
            else:
                return {"success": False, "error": f"Unsupported selector type: {by}"}
            
            element.click()
            return {"success": True, "message": f"Clicked element: {selector}"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def fill_form(self, selector: str, text: str) -> Dict[str, Any]:
        """Fill a form field using Selenium"""
        try:
            if not HAS_SELENIUM:
                return {"success": False, "error": "Selenium not available for advanced web automation"}
            
            if not self.driver:
                self._init_driver()
            
            element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            element.clear()
            element.send_keys(text)
            
            return {"success": True, "message": f"Filled form field: {selector}"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def take_screenshot(self, path: str = None) -> Dict[str, Any]:
        """Take a screenshot of the current page"""
        try:
            if not HAS_SELENIUM:
                # Fallback to pyautogui screenshot
                if not path:
                    path = f"screenshot_{int(time.time())}.png"
                pyautogui.screenshot(path)
                return {"success": True, "message": f"Screenshot saved: {path}"}
            
            if not self.driver:
                self._init_driver()
            
            if not path:
                path = f"web_screenshot_{int(time.time())}.png"
            
            self.driver.save_screenshot(path)
            return {"success": True, "message": f"Web screenshot saved: {path}"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def scrape_data(self, selector: str) -> Dict[str, Any]:
        """Scrape data from web elements"""
        try:
            if not HAS_SELENIUM:
                return {"success": False, "error": "Selenium required for web scraping"}
            
            if not self.driver:
                self._init_driver()
            
            elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
            data = [element.text for element in elements if element.text]
            
            return {
                "success": True,
                "data": data,
                "count": len(data),
                "message": f"Scraped {len(data)} elements"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _init_driver(self):
        """Initialize Selenium WebDriver"""
        if HAS_SELENIUM:
            from selenium.webdriver.chrome.options import Options
            
            options = Options()
            options.add_argument("--headless")  # Run in background
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            
            self.driver = webdriver.Chrome(options=options)
    
    def close_driver(self):
        """Close the WebDriver"""
        if self.driver:
            self.driver.quit()
            self.driver = None


class SystemMonitor:
    """System monitoring and information"""
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get comprehensive system information"""
        try:
            # CPU information
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # Memory information
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Battery information
            try:
                battery = psutil.sensors_battery()
                battery_info = {
                    "percent": battery.percent,
                    "power_plugged": battery.power_plugged,
                    "time_left": battery.secsleft if battery.secsleft != psutil.POWER_TIME_UNLIMITED else "Unlimited"
                }
            except:
                battery_info = None
            
            return {
                "success": True,
                "system": {
                    "platform": platform.platform(),
                    "processor": platform.processor(),
                    "architecture": platform.architecture()[0]
                },
                "cpu": {
                    "usage_percent": cpu_percent,
                    "core_count": cpu_count,
                    "frequency": psutil.cpu_freq().current if psutil.cpu_freq() else None
                },
                "memory": {
                    "total_gb": round(memory.total / (1024**3), 2),
                    "available_gb": round(memory.available / (1024**3), 2),
                    "used_percent": memory.percent
                },
                "disk": {
                    "total_gb": round(disk.total / (1024**3), 2),
                    "used_gb": round(disk.used / (1024**3), 2),
                    "free_gb": round(disk.free / (1024**3), 2),
                    "used_percent": disk.percent
                },
                "battery": battery_info,
                "boot_time": datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_network_info(self) -> Dict[str, Any]:
        """Get network information"""
        try:
            interfaces = psutil.net_if_addrs()
            stats = psutil.net_io_counters()
            
            network_info = {}
            for interface, addrs in interfaces.items():
                network_info[interface] = {
                    "addresses": [str(addr.address) for addr in addrs],
                    "stats": {
                        "bytes_sent": stats.bytes_sent if stats else 0,
                        "bytes_recv": stats.bytes_recv if stats else 0
                    } if stats else {}
                }
            
            return {
                "success": True,
                "interfaces": network_info,
                "message": f"Found {len(network_info)} network interfaces"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}


class GUIController:
    """GUI automation and control"""
    
    def __init__(self):
        self.screen_width, self.screen_height = pyautogui.size()
    
    async def handle_command(self, command: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle GUI automation commands"""
        try:
            if command == "click":
                return self.mouse_click(parameters.get("x"), parameters.get("y"), parameters.get("button"))
            elif command == "type":
                return self.keyboard_type(parameters.get("text"))
            elif command == "hotkey":
                return self.keyboard_hotkey(parameters.get("keys"))
            elif command == "screenshot":
                return self.take_screenshot(parameters.get("path"))
            elif command == "locate":
                return self.locate_on_screen(parameters.get("image"))
            elif command == "drag":
                return self.mouse_drag(parameters.get("start_x"), parameters.get("start_y"), 
                                     parameters.get("end_x"), parameters.get("end_y"))
            elif command == "scroll":
                return self.mouse_scroll(parameters.get("clicks"))
            elif command == "position":
                return self.get_mouse_position()
            else:
                return {"success": False, "error": f"Unknown GUI command: {command}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def mouse_click(self, x: int = None, y: int = None, button: str = "left") -> Dict[str, Any]:
        """Mouse click at specified coordinates"""
        try:
            if x is not None and y is not None:
                pyautogui.click(x, y, button=button)
                return {"success": True, "message": f"Clicked at ({x}, {y}) with {button} button"}
            else:
                pyautogui.click(button=button)
                return {"success": True, "message": f"Clicked at current position with {button} button"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def keyboard_type(self, text: str) -> Dict[str, Any]:
        """Type text using keyboard"""
        try:
            if not text:
                return {"success": False, "error": "No text provided to type"}
            
            pyautogui.write(text, interval=0.05)
            return {"success": True, "message": f"Typed: {text}"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def keyboard_hotkey(self, keys: List[str]) -> Dict[str, Any]:
        """Press keyboard hotkey combination"""
        try:
            if not keys:
                return {"success": False, "error": "No keys provided for hotkey"}
            
            pyautogui.hotkey(*keys)
            return {"success": True, "message": f"Pressed hotkey: {'+'.join(keys)}"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def take_screenshot(self, path: str = None) -> Dict[str, Any]:
        """Take a screenshot"""
        try:
            if not path:
                path = f"screenshot_{int(time.time())}.png"
            
            screenshot = pyautogui.screenshot(path)
            return {"success": True, "message": f"Screenshot saved: {path}"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def locate_on_screen(self, image_path: str) -> Dict[str, Any]:
        """Locate an image on screen"""
        try:
            if not image_path:
                return {"success": False, "error": "No image path provided"}
            
            location = pyautogui.locateOnScreen(image_path, confidence=0.8)
            if location:
                return {
                    "success": True,
                    "found": True,
                    "location": {
                        "left": location.left,
                        "top": location.top,
                        "width": location.width,
                        "height": location.height
                    },
                    "message": f"Image found at {location}"
                }
            else:
                return {"success": True, "found": False, "message": "Image not found on screen"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def mouse_drag(self, start_x: int, start_y: int, end_x: int, end_y: int) -> Dict[str, Any]:
        """Drag mouse from start to end coordinates"""
        try:
            pyautogui.moveTo(start_x, start_y)
            pyautogui.dragTo(end_x, end_y, duration=1)
            return {"success": True, "message": f"Dragged from ({start_x}, {start_y}) to ({end_x}, {end_y})"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def mouse_scroll(self, clicks: int) -> Dict[str, Any]:
        """Scroll mouse wheel"""
        try:
            pyautogui.scroll(clicks or 1)
            return {"success": True, "message": f"Scrolled {clicks} clicks"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_mouse_position(self) -> Dict[str, Any]:
        """Get current mouse position"""
        try:
            x, y = pyautogui.position()
            return {
                "success": True,
                "position": {"x": x, "y": y},
                "message": f"Mouse position: ({x}, {y})"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}


# Automation manager for high-level control
class AutomationManager:
    """High-level automation management with safety controls"""
    
    def __init__(self):
        self.computer = ComputerControl()
        self.safety_enabled = True
        self.confirmation_required = True
        
    async def automate(self, command: str, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute automation command with safety checks"""
        try:
            parameters = parameters or {}
            
            # Safety check for dangerous operations
            if self.safety_enabled:
                safety_result = self._safety_check(command, parameters)
                if not safety_result["allowed"]:
                    return {
                        "success": False, 
                        "error": f"Safety check failed: {safety_result['reason']}",
                        "requires_confirmation": True
                    }
            
            # Execute the command
            result = await self.computer.execute_command(command, parameters)
            return result
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _safety_check(self, command: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Check if automation command is safe to execute"""
        dangerous_commands = ["shutdown", "restart", "kill_app", "delete_file"]
        sensitive_paths = ["/system", "/windows", "/etc", "C:\\Windows"]
        
        if command in dangerous_commands:
            return {
                "allowed": False,
                "reason": f"Command '{command}' requires explicit confirmation"
            }
        
        # Check for sensitive file operations
        if command in ["delete_file", "write_file"]:
            path = parameters.get("path", "").lower()
            for sensitive_path in sensitive_paths:
                if sensitive_path.lower() in path:
                    return {
                        "allowed": False,
                        "reason": f"Operation on sensitive path: {path}"
                    }
        
        return {"allowed": True, "reason": "Safe operation"}
    
    def set_safety_mode(self, enabled: bool):
        """Enable or disable safety mode"""
        self.safety_enabled = enabled
        logger.info(f"Safety mode {'enabled' if enabled else 'disabled'}")
    
    def set_confirmation_required(self, required: bool):
        """Set whether confirmation is required for dangerous operations"""
        self.confirmation_required = required
        logger.info(f"Confirmation {'required' if required else 'not required'}")