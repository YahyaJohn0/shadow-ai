# fast_build_fixed.py
"""
Fixed fast build system for Shadow AI
"""

import os
import sys
import subprocess
import shutil
import time
from pathlib import Path

class FastBuilder:
    def __init__(self):
        self.current_dir = Path(__file__).parent
        self.start_time = time.time()
        
    def log(self, message):
        """Log with timestamp"""
        elapsed = time.time() - self.start_time
        print(f"[{elapsed:06.2f}s] {message}")
        
    def run_command(self, command, description=""):
        """Run a command with logging"""
        if description:
            self.log(f"🔧 {description}")
            
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                cwd=self.current_dir,
                timeout=600  # 10 minute timeout
            )
            
            if result.returncode == 0:
                self.log(f"✅ {description} completed")
                return True
            else:
                self.log(f"❌ {description} failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            self.log(f"⏰ {description} timed out")
            return False
        except Exception as e:
            self.log(f"❌ {description} error: {e}")
            return False
            
    def build_main_app(self):
        """Build main application with optimizations"""
        self.log("🚀 Building main application...")
        
        # Clean previous builds
        if (self.current_dir / "build").exists():
            shutil.rmtree(self.current_dir / "build")
        if (self.current_dir / "dist").exists():
            shutil.rmtree(self.current_dir / "dist")
            
        # Build main application using optimized spec - FIXED COMMAND
        success = self.run_command([
            sys.executable, '-m', 'PyInstaller',
            '--clean',
            '--noconfirm',
            'shadow_ai_optimized.spec'
        ], "Building main application")
        
        return success
        
    def build_installer(self):
        """Build standalone installer"""
        self.log("📦 Building graphical installer...")
        
        # Build installer as onefile for simplicity
        success = self.run_command([
            sys.executable, '-m', 'PyInstaller',
            '--clean',
            '--noconfirm', 
            '--onefile',
            '--windowed',
            '--name=ShadowAI_Setup',
            '--icon=assets/icon.ico',
            'graphical_installer.py'
        ], "Building installer")
        
        return success
        
    def create_distribution(self):
        """Create final distribution package"""
        self.log("📁 Creating distribution package...")
        
        dist_dir = self.current_dir / "dist"
        package_dir = self.current_dir / "ShadowAI_Quick_Setup"
        
        # Clean previous package
        if package_dir.exists():
            shutil.rmtree(package_dir)
        package_dir.mkdir()
        
        # Copy main application
        app_dir = dist_dir / "ShadowAI"
        if app_dir.exists():
            shutil.copytree(app_dir, package_dir / "ShadowAI")
            self.log("✅ Main application copied")
        else:
            self.log("❌ Main application not found")
            return False
            
        # Copy installer
        installer_src = dist_dir / "ShadowAI_Setup.exe"
        if installer_src.exists():
            shutil.copy2(installer_src, package_dir / "Install_ShadowAI.exe")
            self.log("✅ Installer copied to package")
        else:
            self.log("❌ Installer not found")
            return False
            
        # Create quick setup script
        self.create_setup_script(package_dir)
        
        self.log(f"🎉 Distribution package ready: {package_dir}")
        return True
        
    def create_setup_script(self, package_dir):
        """Create quick setup script"""
        script_content = """@echo off
chcp 65001 >nul
title Shadow AI Quick Setup

echo.
echo 🚀 Shadow AI Quick Setup
echo ========================
echo.
echo This package contains:
echo - ShadowAI_Setup.exe: Graphical installer
echo - ShadowAI folder: Portable version
echo.
echo For full installation, run ShadowAI_Setup.exe as Administrator
echo For portable use, run ShadowAI\\ShadowAI.exe
echo.
echo Press any key to continue...
pause >nul

echo.
echo 🔧 Starting graphical installer...
echo Please follow the installation wizard...
echo.

start "" "Install_ShadowAI.exe"

echo.
echo 📝 If the installer doesn't start automatically:
echo     - Navigate to this folder
echo     - Double-click "Install_ShadowAI.exe"
echo     - Run as Administrator for best results
echo.
pause
"""
        
        script_file = package_dir / "Quick_Setup.bat"
        with open(script_file, "w", encoding="utf-8") as f:
            f.write(script_content)
            
    def build_all(self):
        """Build complete package"""
        self.log("🏗️  Starting fast build process...")
        
        # Build main application
        if not self.build_main_app():
            self.log("⚠️  Main app build failed, trying alternative approach...")
            return self.build_alternative()
            
        # Build installer
        if not self.build_installer():
            self.log("⚠️  Installer build failed, but main app is ready")
            
        # Create distribution
        if not self.create_distribution():
            self.log("⚠️  Distribution creation failed")
            
        total_time = time.time() - self.start_time
        self.log(f"🎊 Build completed in {total_time:.2f} seconds!")
        return True

    def build_alternative(self):
        """Alternative build approach"""
        self.log("🔄 Trying alternative build approach...")
        
        # Build main app with simpler command
        success = self.run_command([
            sys.executable, '-m', 'PyInstaller',
            '--clean',
            '--noconfirm',
            '--windowed',
            '--name=ShadowAI',
            '--icon=assets/icon.ico',
            'run_shadow_gui.py'
        ], "Building main application (alternative)")
        
        if success:
            self.build_installer()
            self.create_distribution()
            return True
        return False

def main():
    """Main build function"""
    print("🚀 Shadow AI Fast Builder (Fixed)")
    print("=" * 50)
    
    builder = FastBuilder()
    success = builder.build_all()
    
    if success:
        print(f"\n🎉 Build successful! Total time: {time.time() - builder.start_time:.2f}s")
        print("📦 Check 'ShadowAI_Quick_Setup' folder for the installer")
        print("💡 Run 'Quick_Setup.bat' for easy installation")
    else:
        print("\n❌ Build failed! Trying manual build...")
        manual_build()

def manual_build():
    """Manual build steps as fallback"""
    print("\n🔧 Manual Build Instructions:")
    print("1. Build main app: python -m PyInstaller --clean --noconfirm --windowed --name=ShadowAI --icon=assets/icon.ico run_shadow_gui.py")
    print("2. Build installer: python -m PyInstaller --clean --noconfirm --onefile --windowed --name=ShadowAI_Setup --icon=assets/icon.ico graphical_installer.py")
    print("3. Check 'dist' folder for outputs")

if __name__ == "__main__":
    main()