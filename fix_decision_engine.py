# fix_decision_engine.py
import re

def fix_decision_engine_initialization():
    # Read the main.py file
    with open('main.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the DecisionEngine initialization line
    pattern = r'self\.decision_engine\s*=\s*DecisionEngine\(\)'
    
    if re.search(pattern, content):
        # Replace with proper initialization - brain and memory are created before decision_engine
        fixed_line = 'self.decision_engine = DecisionEngine(self.brain, self.memory)'
        content = re.sub(pattern, fixed_line, content)
        
        # Write the fixed content back
        with open('main.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Fixed DecisionEngine initialization in main.py!")
        return True
    else:
        print("❌ Could not find DecisionEngine initialization to fix")
        return False

if __name__ == "__main__":
    print("🔧 Fixing DecisionEngine initialization...")
    if fix_decision_engine_initialization():
        print("\n🚀 Now restart Shadow AI:")
        print("python main.py")
    else:
        print("\n❌ Fix failed. Please check the main.py file manually.")