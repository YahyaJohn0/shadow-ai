# create_installer.py
"""
Create Windows installer for Shadow AI using Inno Setup
"""

import os
import subprocess
import sys
from pathlib import Path
import shutil

def create_installer():
    """Create Windows installer package"""
    print("🔧 Creating Shadow AI Installer...")
    
    current_dir = Path(__file__).parent
    dist_dir = current_dir / 'dist'
    build_dir = current_dir / 'build'
    installer_dir = current_dir / 'installer'
    
    # Clean previous builds
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    if build_dir.exists():
        shutil.rmtree(build_dir)
    if installer_dir.exists():
        shutil.rmtree(installer_dir)
    
    installer_dir.mkdir(exist_ok=True)
    
    try:
        # Step 1: Build executable with PyInstaller
        print("📦 Building executable with PyInstaller...")
        result = subprocess.run([
            sys.executable, '-m', 'PyInstaller',
            '--clean',
            '--noconfirm',
            'shadow_ai.spec'
        ], capture_output=True, text=True, cwd=current_dir)
        
        if result.returncode != 0:
            print(f"❌ PyInstaller failed: {result.stderr}")
            return False
        
        print("✅ Executable built successfully!")
        
        # Step 2: Create Inno Setup script
        print("📝 Creating Inno Setup script...")
        create_inno_script(current_dir, installer_dir)
        
        # Step 3: Check if Inno Setup is installed
        inno_path = find_inno_setup()
        if not inno_path:
            print("❌ Inno Setup not found. Please install it from: https://jrsoftware.org/isdl.php")
            return False
        
        # Step 4: Compile installer
        print("🏗️  Compiling installer...")
        iss_file = installer_dir / 'ShadowAI.iss'
        result = subprocess.run([
            inno_path,
            iss_file
        ], capture_output=True, text=True, cwd=installer_dir)
        
        if result.returncode == 0:
            print("🎉 Installer created successfully!")
            print(f"📁 Installer location: {installer_dir}")
            return True
        else:
            print(f"❌ Inno Setup compilation failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Installer creation failed: {e}")
        return False

def find_inno_setup():
    """Find Inno Setup compiler path"""
    possible_paths = [
        r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
        r"C:\Program Files\Inno Setup 6\ISCC.exe",
        r"C:\Program Files (x86)\Inno Setup 5\ISCC.exe",
        r"C:\Program Files\Inno Setup 5\ISCC.exe",
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    return None

def create_inno_script(current_dir, installer_dir):
    """Create Inno Setup script"""
    iss_content = f"""; Shadow AI Installer Script
; Generated automatically

#define MyAppName "Shadow AI"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Shadow AI Team"
#define MyAppURL "https://github.com/your-repo/shadow-ai"
#define MyAppExeName "ShadowAI.exe"

[Setup]
AppId={{{{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}}}}
AppName={{#MyAppName}}
AppVersion={{#MyAppVersion}}
AppVerName={{#MyAppName}} {{#MyAppVersion}}
AppPublisher={{#MyAppPublisher}}
AppPublisherURL={{#MyAppURL}}
AppSupportURL={{#MyAppURL}}
AppUpdatesURL={{#MyAppURL}}
DefaultDirName={{autopf}}\{{#MyAppName}}
DefaultGroupName={{#MyAppName}}
AllowNoIcons=yes
LicenseFile={current_dir}\LICENSE
OutputDir={installer_dir}
OutputBaseFilename=ShadowAI_Setup
SetupIconFile={current_dir}\assets\icon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{{cm:CreateDesktopIcon}}"; GroupDescription: "{{cm:AdditionalIcons}}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{{cm:CreateQuickLaunchIcon}}"; GroupDescription: "{{cm:AdditionalIcons}}"; Flags: unchecked; OnlyBelowVersion: 6.1

[Files]
Source: "{current_dir}\dist\ShadowAI\*"; DestDir: "{{app}}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "{current_dir}\data\*"; DestDir: "{{app}}\data"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "{current_dir}\assets\*"; DestDir: "{{app}}\assets"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{{group}}\{{#MyAppName}}"; Filename: "{{app}}\{{#MyAppExeName}}"
Name: "{{group}}\{{cm:UninstallProgram,{{#MyAppName}}}}"; Filename: "{{uninstallexe}}"
Name: "{{autodesktop}}\{{#MyAppName}}"; Filename: "{{app}}\{{#MyAppExeName}}"; Tasks: desktopicon
Name: "{{userappdata}}\Microsoft\Internet Explorer\Quick Launch\{{#MyAppName}}"; Filename: "{{app}}\{{#MyAppExeName}}"; Tasks: quicklaunchicon

[Run]
Filename: "{{app}}\{{#MyAppExeName}}"; Description: "{{cm:LaunchProgram,{{#StringChange(MyAppName, '&', '&&')}}}}"; Flags: nowait postinstall skipifsilent

[Code]
function InitializeSetup(): Boolean;
begin
  Result := True;
  // Check if .NET Framework is installed (optional)
  // if not IsDotNetInstalled then begin
  //   MsgBox('Shadow AI requires .NET Framework 4.5 or later.', mbError, MB_OK);
  //   Result := False;
  // end;
end;
"""
    
    iss_file = installer_dir / 'ShadowAI.iss'
    with open(iss_file, 'w', encoding='utf-8') as f:
        f.write(iss_content)
    
    print(f"✅ Inno Setup script created: {iss_file}")

if __name__ == "__main__":
    success = create_installer()
    if success:
        print("\n🎊 Installation package ready!")
        print("📦 The installer can be found in the 'installer' folder")
        print("🚀 You can now distribute Shadow AI!")
    else:
        print("\n❌ Failed to create installer")
        sys.exit(1)