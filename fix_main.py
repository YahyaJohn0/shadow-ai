# fix_decision_args.py
import re

def fix_decision_engine_arguments():
    """Fix the DecisionEngine missing arguments error"""
    print("🔧 Fixing DecisionEngine missing arguments...")
    
    with open('main.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the exact line causing the error
    error_pattern = r'self\.decision_engine = DecisionEngine\(\)'
    
    if error_pattern in content:
        print("✅ Found the problematic DecisionEngine() call")
        
        # Replace with proper initialization
        fixed_line = '''self.decision_engine = DecisionEngine(
            brain=self.brain,
            memory=self.memory,
            messaging=self.messaging,
            scheduler=self.scheduler,
            knowledge=self.knowledge,
            automation=self.automation
        )'''
        
        new_content = content.replace(error_pattern, fixed_line)
        
        with open('main.py', 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("✅ Fixed DecisionEngine arguments!")
        return True
    else:
        print("❌ Could not find the exact error pattern")
        return False

if __name__ == "__main__":
    if fix_decision_engine_arguments():
        print("\n🚀 Fixed! Now restart Shadow AI:")
        print("python main.py")
    else:
        print("❌ Fix failed - trying alternative approach...")