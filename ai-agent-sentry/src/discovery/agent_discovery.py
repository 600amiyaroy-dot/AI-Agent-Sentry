"""
Agent Discovery Engine - Extended Version
"""
import asyncio
import re
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

@dataclass
class AIAgent:
    """Data model for AI agents"""
    agent_id: str
    name: str
    type: str  # 'chatbot', 'autonomous', 'api', 'automation'
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

class AgentDiscoveryEngine:
    """Discovers AI agents in the environment"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        self.discovered_agents: Dict[str, AIAgent] = {}
        self.config = self._load_config(config_path)
        self.known_patterns = {
            'openai': r'api\.openai\.com',
            'anthropic': r'api\.anthropic\.com',
            'google': r'generativeai\.googleapis\.com',
            'cohere': r'api\.cohere\.ai',
            'huggingface': r'api-inference\.huggingface\.co',
            'azure': r'azure\.ai\.openai',
            'custom': r'/api/v\d+/chat|/api/v\d+/completion'
        }
    
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file"""
        try:
            import yaml
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.warning(f"Config not loaded: {e}")
            return {}
    
    async def discover_all_agents(self):
        """Discover all agents"""
        logger.info("🔍 Starting agent discovery...")
        
        # Simulate discovery (in production, this would scan networks/logs)
        sample_agents = [
            AIAgent(
                agent_id="agent_0001",
                name="SupportBot",
                type="chatbot",
                endpoint="https://api.openai.com/v1/chat",
                capabilities=["chat", "ticket_lookup", "customer_support"],
                permissions=["read_tickets", "respond_tickets"],
                last_active=datetime.now(),
                is_authorized=True
            ),
            AIAgent(
                agent_id="agent_0002",
                name="DataAnalyzer",
                type="autonomous",
                endpoint="https://api.example.com/analyze",
                capabilities=["data_analysis", "report_generation", "data_export", "ml_training"],
                permissions=["read_data", "write_reports", "export_data", "train_models"],
                last_active=datetime.now(),
                is_authorized=False
            ),
            AIAgent(
                agent_id="agent_0003",
                name="EmailBot",
                type="automation",
                endpoint="https://api.example.com/email",
                capabilities=["send_emails", "read_emails", "schedule_emails"],
                permissions=["send_email", "read_email", "manage_calendar"],
                last_active=datetime.now(),
                is_authorized=True
            ),
            AIAgent(
                agent_id="agent_0004",
                name="FileProcessor",
                type="api",
                endpoint="https://api.example.com/files",
                capabilities=["file_read", "file_write", "file_delete"],
                permissions=["read_files", "write_files", "delete_files"],
                last_active=datetime.now(),
                is_authorized=False
            ),
            AIAgent(
                agent_id="agent_0005",
                name="MarketingAI",
                type="autonomous",
                endpoint="https://api.example.com/marketing",
                capabilities=["content_generation", "social_media_posting", "analytics"],
                permissions=["write_content", "post_social", "read_analytics"],
                last_active=datetime.now(),
                is_authorized=True
            )
        ]
        
        for agent in sample_agents:
            agent.risk_score = self.calculate_risk_score(agent)
            self.discovered_agents[agent.agent_id] = agent
        
        logger.info(f"✅ Discovered {len(self.discovered_agents)} agents")
        return self.discovered_agents
    
    def calculate_risk_score(self, agent: AIAgent) -> float:
        """Calculate risk score"""
        score = 0.0
        
        # Unauthorized agents = high risk
        if not agent.is_authorized:
            score += 30
        
        # Write/delete permissions = higher risk
        if 'write' in str(agent.permissions):
            score += 20
        if 'delete' in str(agent.permissions):
            score += 15
        
        # Autonomous agents = higher risk
        if agent.type == 'autonomous':
            score += 25
        
        # Many capabilities = higher risk
        if len(agent.capabilities) > 3:
            score += 10
        
        # Sensitive endpoints
        sensitive_keywords = ['data', 'export', 'admin', 'internal']
        if any(kw in agent.endpoint.lower() for kw in sensitive_keywords):
            score += 10
            
        return min(score, 100)
    
    async def get_inventory(self) -> Dict:
        """Get complete inventory"""
        inventory = {
            'total_agents': len(self.discovered_agents),
            'authorized_count': sum(1 for a in self.discovered_agents.values() if a.is_authorized),
            'unauthorized_count': sum(1 for a in self.discovered_agents.values() if not a.is_authorized),
            'high_risk_count': sum(1 for a in self.discovered_agents.values() if a.risk_score > 50),
            'agents_by_type': {},
            'agents': [a.to_dict() for a in self.discovered_agents.values()]
        }
        
        for agent in self.discovered_agents.values():
            if agent.type not in inventory['agents_by_type']:
                inventory['agents_by_type'][agent.type] = 0
            inventory['agents_by_type'][agent.type] += 1
        
        return inventory
    import socket
import subprocess

async def scan_network_ports(self, network="192.168.1.0/24"):
    """Actually scan network for AI agents"""
    # Simple port scan for common AI API ports
    ports = [5000, 8000, 8080, 8443, 3000, 5001, 8001]
    
    # Ping sweep first
    live_hosts = await self._ping_sweep(network)
    
    # Then port scan
    agents = []
    for host in live_hosts:
        for port in ports:
            if await self._check_port(host, port):
                agents.append({
                    'host': host,
                    'port': port,
                    'type': 'unknown'
                })
    
    return agents

async def _check_port(self, host, port):
    """Check if port is open"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False