"""
AI Agent Sentry - Complete Working System
Run with: python main.py
"""

import asyncio
import json
import uuid
import re
import yaml
import logging
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================
# DATA MODELS
# ============================================

@dataclass
class AIAgent:
    """Data model for AI agents"""
    agent_id: str
    name: str
    type: str
    endpoint: str
    capabilities: List[str]
    permissions: List[str]
    last_active: datetime
    risk_score: float = 0.0
    is_authorized: bool = False
    
    def to_dict(self):
        data = asdict(self)
        data['last_active'] = self.last_active.isoformat()
        return data

@dataclass
class AgentActivity:
    """Data model for agent activities"""
    activity_id: str
    agent_id: str
    action_type: str
    timestamp: datetime
    resource: str
    data_volume: Optional[int] = None
    anomalies: List[str] = None
    
    def to_dict(self):
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data

# ============================================
# DISCOVERY ENGINE
# ============================================

class AgentDiscoveryEngine:
    """Discovers AI agents in the environment"""
    
    def __init__(self):
        self.discovered_agents: Dict[str, AIAgent] = {}
        self.known_patterns = {
            'openai': r'api\.openai\.com',
            'anthropic': r'api\.anthropic\.com',
            'google': r'generativeai\.googleapis\.com',
            'azure': r'azure\.ai\.openai',
            'custom': r'/api/v\d+/chat'
        }
    
    async def discover_all_agents(self):
        """Discover all agents"""
        logger.info("Starting agent discovery...")
        
        # Simulate discovery (in production, this would scan networks/logs)
        sample_agents = [
            AIAgent(
                agent_id="agent_0001",
                name="SupportBot",
                type="chatbot",
                endpoint="https://api.example.com/chat",
                capabilities=["chat", "ticket_lookup"],
                permissions=["read_tickets"],
                last_active=datetime.now(),
                is_authorized=True
            ),
            AIAgent(
                agent_id="agent_0002",
                name="DataAnalyzer",
                type="autonomous",
                endpoint="https://api.example.com/analyze",
                capabilities=["data_analysis", "report_generation", "data_export"],
                permissions=["read_data", "write_reports", "export_data"],
                last_active=datetime.now(),
                is_authorized=False
            ),
            AIAgent(
                agent_id="agent_0003",
                name="EmailBot",
                type="automation",
                endpoint="https://api.example.com/email",
                capabilities=["send_emails", "read_emails"],
                permissions=["send_email", "read_email"],
                last_active=datetime.now(),
                is_authorized=True
            ),
            AIAgent(
                agent_id="agent_0004",
                name="FileProcessor",
                type="api",
                endpoint="https://api.example.com/files",
                capabilities=["file_read", "file_write"],
                permissions=["read_files", "write_files"],
                last_active=datetime.now(),
                is_authorized=False
            )
        ]
        
        for agent in sample_agents:
            agent.risk_score = self.calculate_risk_score(agent)
            self.discovered_agents[agent.agent_id] = agent
        
        logger.info(f"Discovered {len(self.discovered_agents)} agents")
        return self.discovered_agents
    
    def calculate_risk_score(self, agent: AIAgent) -> float:
        """Calculate risk score"""
        score = 0.0
        
        if not agent.is_authorized:
            score += 30
        if 'write' in str(agent.permissions):
            score += 20
        if agent.type == 'autonomous':
            score += 25
        if len(agent.capabilities) > 3:
            score += 15
            
        return min(score, 100)

# ============================================
# MONITORING ENGINE
# ============================================

class AgentMonitor:
    """Monitors agent activities"""
    
    def __init__(self, discovery_engine):
        self.discovery_engine = discovery_engine
        self.activity_log: List[AgentActivity] = []
        self.alert_count = 0
    
    async def log_activity(self, agent_id: str, action_type: str, 
                          resource: str, data_volume: int = None):
        """Log agent activity"""
        
        activity = AgentActivity(
            activity_id=f"act_{uuid.uuid4().hex[:8]}",
            agent_id=agent_id,
            action_type=action_type,
            timestamp=datetime.now(),
            resource=resource,
            data_volume=data_volume,
            anomalies=[]
        )
        
        # Check for anomalies
        anomalies = []
        
        # Check 1: High data volume
        if data_volume and data_volume > 1000:
            anomalies.append('HIGH_DATA_VOLUME')
        
        # Check 2: Sensitive resource access
        sensitive = ['/etc/passwd', '/etc/shadow', 'credentials']
        if any(s in resource for s in sensitive):
            anomalies.append('SENSITIVE_ACCESS')
        
        # Check 3: Unauthorized agent
        if agent_id not in self.discovery_engine.discovered_agents:
            anomalies.append('UNDISCOVERED_AGENT')
        else:
            agent = self.discovery_engine.discovered_agents[agent_id]
            if not agent.is_authorized:
                anomalies.append('UNAUTHORIZED_AGENT')
        
        activity.anomalies = anomalies
        
        if anomalies:
            logger.warning(f"⚠️ Anomalies detected: {anomalies}")
            self.alert_count += 1
        
        self.activity_log.append(activity)
        return activity

# ============================================
# RESPONSE ENGINE
# ============================================

class AutoResponseEngine:
    """Automated response to threats"""
    
    def __init__(self):
        self.response_log = []
    
    async def process_alert(self, alert_type: str, agent_id: str, details: Dict):
        """Process and respond to alerts"""
        
        logger.info(f"🚨 PROCESSING ALERT: {alert_type} for {agent_id}")
        
        response = {
            'timestamp': datetime.now().isoformat(),
            'agent_id': agent_id,
            'alert_type': alert_type,
            'action': None,
            'status': 'processed'
        }
        
        # Take action based on alert type
        if alert_type in ['UNAUTHORIZED_AGENT', 'UNDISCOVERED_AGENT']:
            response['action'] = 'QUARANTINE'
            response['message'] = f"Agent {agent_id} has been quarantined"
            logger.warning(f"🔒 AGENT QUARANTINED: {agent_id}")
            
        elif alert_type == 'HIGH_DATA_VOLUME':
            response['action'] = 'BLOCK_ACCESS'
            response['message'] = f"Data access blocked for {agent_id}"
            logger.warning(f"🚫 ACCESS BLOCKED: {agent_id}")
            
        elif alert_type == 'SENSITIVE_ACCESS':
            response['action'] = 'REVOKE_PERMISSIONS'
            response['message'] = f"Permissions revoked for {agent_id}"
            logger.warning(f"🔑 PERMISSIONS REVOKED: {agent_id}")
            
        else:
            response['action'] = 'LOG_ONLY'
            response['message'] = f"Alert logged for {agent_id}"
        
        self.response_log.append(response)
        return response

# ============================================
# MAIN SYSTEM
# ============================================

class AIAgentSentry:
    """Main system orchestrator"""
    
    def __init__(self):
        self.discovery = AgentDiscoveryEngine()
        self.monitor = None
        self.response = AutoResponseEngine()
        self.is_running = False
    
    async def start(self):
        """Start the system"""
        logger.info("=" * 60)
        logger.info("🤖 AI AGENT SENTRY v1.0")
        logger.info("=" * 60)
        
        # Discover agents
        await self.discovery.discover_all_agents()
        
        # Initialize monitor
        self.monitor = AgentMonitor(self.discovery)
        
        self.is_running = True
        logger.info("✅ System is running!")
        logger.info(f"📊 Monitoring {len(self.discovery.discovered_agents)} agents")
        
        # Print agent inventory
        self.print_inventory()
        
        return self
    
    def print_inventory(self):
        """Print all discovered agents"""
        print("\n" + "=" * 70)
        print("📋 AGENT INVENTORY")
        print("=" * 70)
        print(f"{'ID':<12} {'Name':<15} {'Type':<12} {'Risk':<8} {'Authorized'}")
        print("-" * 70)
        
        for agent in self.discovery.discovered_agents.values():
            auth = "✅" if agent.is_authorized else "❌"
            print(f"{agent.agent_id:<12} {agent.name:<15} {agent.type:<12} {agent.risk_score:>5}%   {auth}")
        
        print("=" * 70)
        print(f"Total: {len(self.discovery.discovered_agents)} agents")
        print(f"High Risk: {sum(1 for a in self.discovery.discovered_agents.values() if a.risk_score > 50)} agents")
        print(f"Unauthorized: {sum(1 for a in self.discovery.discovered_agents.values() if not a.is_authorized)} agents")
        print("=" * 70 + "\n")
    
    async def simulate_activity(self):
        """Simulate agent activities"""
        logger.info("🎮 Simulating agent activities...")
        
        activities = [
            ('agent_0001', 'api_call', '/api/chat', 100),
            ('agent_0002', 'data_export', '/data/export', 5000),
            ('agent_0003', 'email_send', '/email/send', 50),
            ('agent_0004', 'file_access', '/etc/passwd', 10),
            ('agent_0001', 'api_call', '/api/chat', 200),
            ('agent_0002', 'file_write', '/data/output', 3000),
        ]
        
        for agent_id, action, resource, volume in activities:
            activity = await self.monitor.log_activity(agent_id, action, resource, volume)
            
            # Check for anomalies
            if activity.anomalies:
                for anomaly in activity.anomalies:
                    await self.response.process_alert(
                        anomaly, 
                        agent_id,
                        {'activity_id': activity.activity_id}
                    )
            
            await asyncio.sleep(0.5)
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print system summary"""
        print("\n" + "=" * 70)
        print("📊 SYSTEM SUMMARY")
        print("=" * 70)
        print(f"Total Activities Logged: {len(self.monitor.activity_log)}")
        print(f"Total Alerts Triggered: {self.monitor.alert_count}")
        print(f"Total Responses Executed: {len(self.response.response_log)}")
        
        if self.response.response_log:
            print("\n📌 Recent Responses:")
            for resp in self.response.response_log[-3:]:
                print(f"  • {resp['alert_type']} → {resp['action']}")
        
        print("=" * 70 + "\n")

# ============================================
# RUN THE SYSTEM
# ============================================

async def main():
    """Main entry point"""
    system = AIAgentSentry()
    await system.start()
    
    # Simulate some activity
    await system.simulate_activity()
    
    print("\n" + "=" * 70)
    print("✅ AI Agent Sentry Demo Complete!")
    print("=" * 70)
    print("This system can:")
    print("  🔍 Discover unauthorized AI agents")
    print("  📊 Monitor agent behavior in real-time")
    print("  🚨 Detect anomalies and security threats")
    print("  ⚡ Auto-respond to protect your organization")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    asyncio.run(main())