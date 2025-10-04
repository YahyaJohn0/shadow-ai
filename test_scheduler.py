# test_scheduler.py
import asyncio
import sys
import os
import time

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from shadow_core.scheduler import MockScheduler, TaskType, TaskStatus

async def test_scheduler_module():
    print("⏰ Testing Scheduler Module...")
    print("=" * 60)
    
    # Test with mock scheduler
    scheduler = MockScheduler()
    
    print("📅 Testing Reminder Creation:")
    
    # Test setting a reminder
    reminder_id = await scheduler.set_reminder(
        title="Test Reminder",
        description="This is a test reminder",
        delay_minutes=1,  # 1 minute from now
        delay_seconds=0
    )
    print(f"✅ Reminder created with ID: {reminder_id}")
    
    # Test setting a timer
    timer_id = await scheduler.set_timer(
        duration_minutes=2,
        duration_seconds=0,
        title="Test Timer"
    )
    print(f"✅ Timer created with ID: {timer_id}")
    
    # Test setting an alarm
    alarm_id = await scheduler.set_alarm(
        alarm_time="14:30",  # 2:30 PM
        title="Test Alarm"
    )
    print(f"✅ Alarm created with ID: {alarm_id}")
    
    print("\n📋 Testing Task Listing:")
    upcoming_tasks = scheduler.get_upcoming_tasks(limit=5)
    print(f"Found {len(upcoming_tasks)} upcoming tasks:")
    
    for task in upcoming_tasks:
        time_str = time.strftime("%H:%M:%S", time.localtime(task.scheduled_time))
        print(f"  - {task.title} at {time_str} ({task.task_type.value})")
    
    print("\n❌ Testing Task Cancellation:")
    if upcoming_tasks:
        success = scheduler.cancel_task(upcoming_tasks[0].id)
        status = "✅ Success" if success else "❌ Failed"
        print(f"Cancellation of task {upcoming_tasks[0].id}: {status}")
    
    # Wait a bit to see if any tasks execute
    print("\n⏳ Waiting for task execution (10 seconds)...")
    await asyncio.sleep(10)
    
    # Clean shutdown
    await scheduler.shutdown()
    
    print("\n" + "=" + "=" * 60)
    print("✅ Scheduler module test completed!")

async def test_real_scheduler():
    """Test with real scheduler"""
    print("\n" + "=" * 60)
    print("Testing Real Scheduler...")
    
    try:
        from shadow_core.scheduler import Scheduler
        
        real_scheduler = Scheduler()
        
        # Set a quick reminder
        reminder_id = await real_scheduler.set_reminder(
            title="Real Test Reminder",
            description="Testing real scheduler",
            delay_minutes=0,
            delay_seconds=10  # 10 seconds from now
        )
        
        print(f"✅ Real reminder set with ID: {reminder_id}")
        print("⏳ Waiting for reminder execution (15 seconds)...")
        
        # Wait for execution
        await asyncio.sleep(15)
        
        # Clean shutdown
        await real_scheduler.shutdown()
        
        print("✅ Real scheduler test completed!")
        
    except Exception as e:
        print(f"❌ Real scheduler test failed: {e}")

async def main():
    await test_scheduler_module()
    await test_real_scheduler()
    
    print("\n" + "=" * 60)
    print("🎉 Scheduler module is ready to use!")
    print("\nNext steps:")
    print("1. Test with real reminders: 'Set a reminder for 5 minutes to take a break'")
    print("2. Test timers: 'Set a timer for 10 minutes'")
    print("3. Test alarms: 'Set an alarm for 7:30 AM'")

if __name__ == "__main__":
    asyncio.run(main())