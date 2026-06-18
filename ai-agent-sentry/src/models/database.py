"""
Enterprise Database Models
Supports 10,000+ agents with PostgreSQL
"""

from sqlalchemy import (
    create_engine, Column, String, Integer, Float, 
    DateTime, JSON, Boolean, Text, ForeignKey, Index
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os
import logging

logger = logging.getLogger(__name__)

Base = declarative_base()

# ============================================
# ENTERPRISE MODELS
# ============================================

class EnterpriseAgent(Base):
    """Complete agent model for enterprise"""
    __tablename__ = 'enterprise_agents'
    
    # Primary fields
    id = Column(String(50), primary_key=True)
    name = Column(String(200), nullable=False)
    agent_type = Column(String(50), nullable=False)
    endpoint = Column(String(500))
    
    # Security fields
    risk_score = Column(Float, default=0.0)
    is_authorized = Column(Boolean, default=False)
    is_quarantined = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    # Metadata
    capabilities = Column(JSON, default=[])
    permissions = Column(JSON, default=[])
    tags = Column(JSON, default=[])
    
    # Ownership & Multi-tenancy
    company_id = Column(String(50), index=True)
    department = Column(String(100))
    owner_id = Column(String(50))
    team_id = Column(String(50))
    
    # Timestamps
    discovered_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    activities = relationship("EnterpriseActivity", back_populates="agent")
    alerts = relationship("EnterpriseAlert", back_populates="agent")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_agent_company', 'company_id'),
        Index('idx_agent_risk', 'risk_score'),
        Index('idx_agent_active', 'is_active'),
        Index('idx_agent_authorized', 'is_authorized'),
    )

class EnterpriseActivity(Base):
    """Activity tracking for audit"""
    __tablename__ = 'enterprise_activities'
    
    id = Column(Integer, primary_key=True)
    activity_id = Column(String(50), unique=True, index=True)
    agent_id = Column(String(50), ForeignKey('enterprise_agents.id'), index=True)
    
    action_type = Column(String(50))
    resource = Column(String(500))
    data_volume = Column(Integer, default=0)
    anomalies = Column(JSON, default=[])
    
    status = Column(String(20), default='monitored')
    severity = Column(String(20), default='info')
    
    # Context
    source_ip = Column(String(50))
    user_agent = Column(String(500))
    session_id = Column(String(100))
    request_id = Column(String(100))
    
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    agent = relationship("EnterpriseAgent", back_populates="activities")

class EnterpriseAlert(Base):
    """Security alerts"""
    __tablename__ = 'enterprise_alerts'
    
    id = Column(Integer, primary_key=True)
    alert_id = Column(String(50), unique=True, index=True)
    agent_id = Column(String(50), ForeignKey('enterprise_agents.id'), index=True)
    
    alert_type = Column(String(50))
    severity = Column(String(20))  # CRITICAL, HIGH, MEDIUM, LOW
    status = Column(String(20), default='open')  # open, acknowledged, resolved
    
    message = Column(Text)
    details = Column(JSON)
    response_action = Column(String(50))
    response_status = Column(String(20))
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    resolved_at = Column(DateTime)
    
    # Relationships
    agent = relationship("EnterpriseAgent", back_populates="alerts")

class EnterpriseAuditLog(Base):
    """Complete audit trail for compliance"""
    __tablename__ = 'enterprise_audit_logs'
    
    id = Column(Integer, primary_key=True)
    log_id = Column(String(50), unique=True, index=True)
    
    # Who
    user_id = Column(String(50), index=True)
    user_role = Column(String(50))
    user_ip = Column(String(50))
    
    # What
    action = Column(String(100))
    resource_type = Column(String(50))
    resource_id = Column(String(50))
    
    # Context
    details = Column(JSON)
    changes = Column(JSON)  # Before/after
    
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

# ============================================
# DATABASE MANAGER
# ============================================

class DatabaseManager:
    """Enterprise database manager"""
    
    def __init__(self, db_url=None):
        """Initialize with PostgreSQL"""
        if not db_url:
            db_url = os.getenv(
                'DATABASE_URL',
                'postgresql://user:password@localhost:5432/ai_sentry'
            )
        
        self.engine = create_engine(
            db_url,
            pool_size=20,  # Connection pool
            max_overflow=40,
            pool_pre_ping=True,
            echo=False
        )
        
        self.Session = sessionmaker(
            bind=self.engine,
            autocommit=False,
            autoflush=False
        )
        
        self.create_tables()
        logger.info(f"✅ Database connected: {db_url.split('@')[-1]}")
    
    def create_tables(self):
        """Create all tables"""
        Base.metadata.create_all(self.engine)
        logger.info("✅ Database tables created")
    
    def get_session(self):
        """Get database session"""
        return self.Session()
    
    async def save_agent(self, agent_data):
        """Save agent to database"""
        session = self.get_session()
        try:
            agent = EnterpriseAgent(**agent_data)
            session.add(agent)
            session.commit()
            return agent
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to save agent: {e}")
            raise
        finally:
            session.close()
    
    async def get_agent(self, agent_id):
        """Get agent by ID"""
        session = self.get_session()
        try:
            return session.query(EnterpriseAgent).filter_by(id=agent_id).first()
        finally:
            session.close()
    
    async def get_all_agents(self, company_id=None, limit=100):
        """Get all agents with filtering"""
        session = self.get_session()
        try:
            query = session.query(EnterpriseAgent)
            if company_id:
                query = query.filter_by(company_id=company_id)
            return query.limit(limit).all()
        finally:
            session.close()
    
    async def save_activity(self, activity_data):
        """Save activity log"""
        session = self.get_session()
        try:
            activity = EnterpriseActivity(**activity_data)
            session.add(activity)
            session.commit()
            return activity
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to save activity: {e}")
            raise
        finally:
            session.close()
    
    async def save_alert(self, alert_data):
        """Save alert"""
        session = self.get_session()
        try:
            alert = EnterpriseAlert(**alert_data)
            session.add(alert)
            session.commit()
            return alert
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to save alert: {e}")
            raise
        finally:
            session.close()
    
    async def get_alerts(self, severity=None, status='open', limit=50):
        """Get alerts with filtering"""
        session = self.get_session()
        try:
            query = session.query(EnterpriseAlert).filter_by(status=status)
            if severity:
                query = query.filter_by(severity=severity)
            return query.order_by(EnterpriseAlert.created_at.desc()).limit(limit).all()
        finally:
            session.close()