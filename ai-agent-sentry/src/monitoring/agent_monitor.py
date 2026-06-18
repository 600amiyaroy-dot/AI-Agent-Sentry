"""
Agent Monitor - Real-time Activity Tracking
"""
import asyncio
import uuid
import logging
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

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

class AgentMonitor:
    """Monitors agent activities in real-time"""
    
    def __init__(self, discovery_engine):
        self.discovery_engine = discovery_engine
        self.activity_log: List[AgentActivity] = []
        self.alert_count = 0
    
    async def log_activity(self, agent_id: str, action_type: str, 
                          resource: str, data_volume: int = None):
        """Log agent activity and check for anomalies"""
        
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
        anomalies = await self._check_anomalies(activity)
        activity.anomalies = anomalies
        
        if anomalies:
            logger.warning(f"⚠️ Anomalies detected: {anomalies}")
            self.alert_count += 1
        
        self.activity_log.append(activity)
        return activity
    
    async def _check_anomalies(self, activity: AgentActivity) -> List[str]:
        """Check activity for anomalies"""
        anomalies = []
        
        # 1. High data volume
        if activity.data_volume and activity.data_volume > 1000:
            anomalies.append('HIGH_DATA_VOLUME')
        
        # 2. Sensitive resource access
        sensitive = ['/etc/passwd', '/etc/shadow', 'credentials', 
                     '/admin', '/internal', '/secrets']
        if any(s in activity.resource for s in sensitive):
            anomalies.append('SENSITIVE_ACCESS')
        
        # 3. Unauthorized agent
        if activity.agent_id not in self.discovery_engine.discovered_agents:
            anomalies.append('UNDISCOVERED_AGENT')
        else:
            agent = self.discovery_engine.discovered_agents.get(activity.agent_id)
            if agent and not agent.is_authorized:
                anomalies.append('UNAUTHORIZED_AGENT')
        
        # 4. High frequency (check last minute)
        recent = [a for a in self.activity_log 
                 if a.agent_id == activity.agent_id 
                 and (datetime.now() - a.timestamp).seconds < 60]
        if len(recent) > 10:
            anomalies.append('HIGH_FREQUENCY')
        
        return anomalies
    
    async def get_agent_summary(self, agent_id: str) -> Dict:
        """Get summary of agent activity"""
        activities = [a for a in self.activity_log if a.agent_id == agent_id]
        
        return {
            'agent_id': agent_id,
            'total_activities': len(activities),
            'anomaly_count': sum(len(a.anomalies) for a in activities),
            'latest_activity': activities[-1].to_dict() if activities else None
        }