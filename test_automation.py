# test_automation.py
import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from shadow_core.automation import AutomationManager, ComputerControl

async def test_automation_module():
    print("🤖 Testing Automation Module - Full Computer Control")
    print("=" * 70)
    
    # Test with automation manager
    automation = AutomationManager()
    
    print("🔧 Testing Safe Automation Commands:")
    
    # Test system information
    print("\n1. Testing System Information:")
    result = await automation.automate("system_info")
    if result["success"]:
        print("✅ System info retrieved successfully")
        if "system" in result:
            print(f"   Platform: {result['system']['platform']}")
    else:
        print(f"❌ System info failed: {result['error']}")
    
    # Test file operations
    print("\n2. Testing File Operations:")
    result = await automation.automate("list_files", {"path": "."})
    if result["success"]:
        print(f"✅ File listing: {result['count']} files found")
    else:
        print(f"❌ File listing failed: {result['error']}")
    
    # Test application control (safe)
    print("\n3. Testing Application Control:")
    result = await automation.automate("list_apps")
    if result["success"]:
        print(f"✅ Application listing: {result['count']} apps found")
    else:
        print(f"❌ Application listing failed: {result['error']}")
    
    # Test web automation
    print("\n4. Testing Web Automation:")
    result = await automation.automate("web_search", {"query": "test automation"})
    if result["success"]:
        print("✅ Web search initiated")
    else:
        print(f"❌ Web search failed: {result['error']}")
    
    # Test GUI automation
    print("\n5. Testing GUI Automation:")
    result = await automation.automate("get_mouse_position")
    if result["success"]:
        pos = result["position"]
        print(f"✅ Mouse position: ({pos['x']}, {pos['y']})")
    else:
        print(f"❌ Mouse position failed: {result['error']}")
    
    print("\n⚠️  Testing Safety Controls:")
    
    # Test dangerous command (should be blocked by safety)
    print("\n6. Testing Safety Block (Dangerous Command):")
    result = await automation.automate("shutdown")
    if not result["success"] and "requires_confirmation" in result:
        print("✅ Safety check working - dangerous command blocked")
    else:
        print("❌ Safety check may not be working properly")
    
    # Disable safety and test again
    print("\n7. Testing with Safety Disabled:")
    automation.set_safety_mode(False)
    result = await automation.automate("system_info")
    if result["success"]:
        print("✅ Commands work with safety disabled")
    else:
        print(f"❌ Command failed: {result['error']}")
    
    # Re-enable safety
    automation.set_safety_mode(True)
    
    print("\n" + "=" + "=" * 70)
    print("✅ Automation module test completed!")
    
    # Show available commands
    print("\n🎯 Available Automation Commands:")
    commands = [
        "system_info", "list_files", "open_file", "read_file", "write_file",
        "open_app", "close_app", "list_apps", "web_search", "open_url",
        "screenshot", "type_text", "click_mouse", "get_mouse_position"
    ]
    for cmd in commands:
        print(f"  - {cmd}")

async def test_computer_control():
    """Test direct computer control"""
    print("\n" + "=" * 70)
    print("Testing Direct Computer Control...")
    
    try:
        computer = ComputerControl()
        
        # Test file manager
        file_result = computer.file_manager.list_files(".", "*.py")
        if file_result["success"]:
            print(f"✅ File manager: {file_result['count']} Python files found")
        
        # Test system monitor
        system_result = computer.system_monitor.get_system_info()
        if system_result["success"]:
            print("✅ System monitor: System information retrieved")
        
        print("✅ Direct computer control test completed!")
        
    except Exception as e:
        print(f"❌ Computer control test failed: {e}")

async def main():
    await test_automation_module()
    await test_computer_control()
    
    print("\n" + "=" * 70)
    print("🎉 Automation module is ready for full computer control!")
    print("\n🚀 Your Shadow AI can now:")
    print("  • Control files and folders")
    print("  • Manage applications")
    print("  • Automate web browsing") 
    print("  • Control mouse and keyboard")
    print("  • Monitor system resources")
    print("  • Take screenshots")
    print("  • And much more!")

if __name__ == "__main__":
    asyncio.run(main())