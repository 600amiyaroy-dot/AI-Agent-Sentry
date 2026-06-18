"""
Test Suite for AI Agent Sentry
Run with: pytest tests/
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import AIAgentSentry

async def test_discovery():
    """Test agent discovery"""
    system = AIAgentSentry()
    await system.start()
    assert len(system.discovery.discovered_agents) > 0
    print("✅ Discovery test passed")

async def test_monitoring():
    """Test monitoring"""
    system = AIAgentSentry()
    await system.start()
    
    agent_id = list(system.discovery.discovered_agents.keys())[0]
    activity = await system.monitor.log_activity(
        agent_id, 'api_call', '/api/test', 100
    )
    assert activity.activity_id is not None
    print("✅ Monitoring test passed")

async def test_response():
    """Test response engine"""
    system = AIAgentSentry()
    await system.start()
    
    response = await system.response.process_alert(
        'UNAUTHORIZED_AGENT', 'agent_0002', {}
    )
    assert response['action'] == 'quarantine'
    print("✅ Response test passed")

def run_tests():
    """Run all tests"""
    print("🧪 Running tests...")
    asyncio.run(test_discovery())
    asyncio.run(test_monitoring())
    asyncio.run(test_response())
    print("✅ All tests passed!")

if __name__ == "__main__":
    run_tests()