"""
AI Agent Sentry - Web Dashboard
Run with: uvicorn web_dashboard:app --reload
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
import asyncio
import json
from datetime import datetime
from typing import Dict, List
import logging

# Import your existing system
import sys
sys.path.append('.')

# ============================================
# CREATE FASTAPI APP FIRST (MOST IMPORTANT!)
# ============================================
app = FastAPI(title="AI Agent Sentry Dashboard", version="1.0.0")

# Global system instance
system = None

# ============================================
# HEALTH CHECK ENDPOINTS (MUST BE AFTER app IS CREATED)
# ============================================
@app.get("/health")
async def health_check():
    """Health check endpoint for Docker"""
    return {
        "status": "healthy",
        "service": "AI Agent Sentry",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/ready")
async def readiness_check():
    """Readiness check for Kubernetes"""
    return {
        "status": "ready",
        "service": "AI Agent Sentry"
    }

# ============================================
# DASHBOARD AND API ENDPOINTS
# ============================================

@app.on_event("startup")
async def startup_event():
    """Initialize the system on startup"""
    global system
    try:
        from main import AIAgentSentry
        system = AIAgentSentry()
        await system.start()
        logging.info("🚀 Dashboard started successfully!")
    except Exception as e:
        logging.error(f"Failed to start system: {e}")
        system = None

@app.get("/", response_class=HTMLResponse)
async def home():
    """Main dashboard page"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI Agent Sentry Dashboard</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            .container { max-width: 1400px; margin: 0 auto; }
            h1 {
                color: white;
                text-align: center;
                font-size: 2.5rem;
                margin-bottom: 30px;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }
            .stats-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }
            .stat-card {
                background: white;
                padding: 20px;
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                text-align: center;
                transition: transform 0.3s;
            }
            .stat-card:hover { transform: translateY(-5px); }
            .stat-number { font-size: 2.5rem; font-weight: bold; color: #667eea; }
            .stat-label { color: #666; margin-top: 10px; font-size: 0.9rem; }
            .stat-critical { color: #e74c3c; }
            .stat-warning { color: #f39c12; }
            .stat-safe { color: #2ecc71; }
            .agent-table {
                background: white;
                border-radius: 15px;
                padding: 20px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                margin-bottom: 30px;
                overflow-x: auto;
            }
            table {
                width: 100%;
                border-collapse: collapse;
            }
            th, td {
                padding: 12px;
                text-align: left;
                border-bottom: 1px solid #eee;
            }
            th {
                background: #f8f9fa;
                font-weight: 600;
                color: #333;
            }
            tr:hover { background: #f8f9fa; }
            .badge {
                padding: 5px 10px;
                border-radius: 20px;
                font-size: 0.8rem;
                font-weight: 600;
            }
            .badge-danger { background: #fee; color: #e74c3c; }
            .badge-success { background: #efe; color: #2ecc71; }
            .badge-warning { background: #ffeaa7; color: #f39c12; }
            .badge-info { background: #e3f2fd; color: #1976d2; }
            .risk-bar {
                width: 100px;
                height: 8px;
                background: #eee;
                border-radius: 10px;
                overflow: hidden;
                display: inline-block;
            }
            .risk-fill { height: 100%; border-radius: 10px; transition: width 0.3s; }
            .risk-high { background: #e74c3c; }
            .risk-medium { background: #f39c12; }
            .risk-low { background: #2ecc71; }
            .refresh-btn {
                background: white;
                border: none;
                padding: 10px 30px;
                border-radius: 25px;
                font-size: 1rem;
                font-weight: 600;
                color: #667eea;
                cursor: pointer;
                box-shadow: 0 5px 15px rgba(0,0,0,0.2);
                transition: all 0.3s;
                margin-bottom: 20px;
            }
            .refresh-btn:hover {
                transform: scale(1.05);
                box-shadow: 0 8px 25px rgba(0,0,0,0.3);
            }
            .alert-box {
                background: #fff3cd;
                border-left: 4px solid #ffc107;
                padding: 15px;
                border-radius: 10px;
                margin-bottom: 20px;
            }
            .logs {
                background: #1e1e1e;
                color: #d4d4d4;
                border-radius: 15px;
                padding: 20px;
                font-family: 'Consolas', monospace;
                font-size: 0.9rem;
                max-height: 300px;
                overflow-y: auto;
            }
            .log-entry { padding: 5px 0; border-bottom: 1px solid #333; }
            .log-time { color: #858585; margin-right: 10px; }
            .log-info { color: #4fc3f7; }
            .log-warning { color: #ffb74d; }
            .log-danger { color: #ef5350; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🛡️ AI Agent Sentry Dashboard</h1>
            <div style="text-align: center; margin-bottom: 20px;">
                <button class="refresh-btn" onclick="location.reload()">🔄 Refresh Data</button>
            </div>
            <div class="stats-grid" id="stats">
                <div class="stat-card">
                    <div class="stat-number" id="totalAgents">-</div>
                    <div class="stat-label">Total Agents</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number stat-critical" id="highRisk">-</div>
                    <div class="stat-label">High Risk Agents</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number stat-warning" id="unauthorized">-</div>
                    <div class="stat-label">Unauthorized Agents</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number stat-safe" id="authorized">-</div>
                    <div class="stat-label">Authorized Agents</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" id="alerts">-</div>
                    <div class="stat-label">Total Alerts</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" id="responses">-</div>
                    <div class="stat-label">Responses Executed</div>
                </div>
            </div>
            <div class="agent-table">
                <h2 style="margin-bottom: 20px; color: #333;">📋 Agent Inventory</h2>
                <table id="agentTable">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Name</th>
                            <th>Type</th>
                            <th>Risk Score</th>
                            <th>Status</th>
                            <th>Capabilities</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody id="agentBody">
                        <tr><td colspan="7" style="text-align: center;">Loading...</td></tr>
                    </tbody>
                </table>
            </div>
            <div class="agent-table">
                <h2 style="margin-bottom: 20px; color: #333;">🚨 Recent Alerts</h2>
                <div id="alertsContent">
                    <p style="color: #666;">Loading alerts...</p>
                </div>
            </div>
            <div class="agent-table">
                <h2 style="margin-bottom: 20px; color: #333;">📜 Activity Log</h2>
                <div class="logs" id="logs">
                    <div class="log-entry">
                        <span class="log-time">[System]</span>
                        <span class="log-info">Monitoring agents in real-time...</span>
                    </div>
                </div>
            </div>
        </div>
        <script>
            async function fetchData() {
                try {
                    const agentsRes = await fetch('/api/agents');
                    const agents = await agentsRes.json();
                    const statsRes = await fetch('/api/stats');
                    const stats = await statsRes.json();
                    
                    document.getElementById('totalAgents').textContent = stats.total_agents || 0;
                    document.getElementById('highRisk').textContent = stats.high_risk || 0;
                    document.getElementById('unauthorized').textContent = stats.unauthorized || 0;
                    document.getElementById('authorized').textContent = stats.authorized || 0;
                    document.getElementById('alerts').textContent = stats.alerts || 0;
                    document.getElementById('responses').textContent = stats.responses || 0;
                    
                    const tbody = document.getElementById('agentBody');
                    tbody.innerHTML = '';
                    
                    agents.forEach(agent => {
                        const riskClass = agent.risk_score > 50 ? 'risk-high' : 
                                        agent.risk_score > 30 ? 'risk-medium' : 'risk-low';
                        const statusClass = agent.is_authorized ? 'badge-success' : 'badge-danger';
                        const statusText = agent.is_authorized ? '✅ Authorized' : '❌ Unauthorized';
                        
                        const tr = document.createElement('tr');
                        tr.innerHTML = `
                            <td><code>${agent.agent_id}</code></td>
                            <td><strong>${agent.name}</strong></td>
                            <td><span class="badge badge-info">${agent.type}</span></td>
                            <td>
                                <div class="risk-bar">
                                    <div class="risk-fill ${riskClass}" style="width: ${agent.risk_score}%"></div>
                                </div>
                                ${agent.risk_score}%
                            </td>
                            <td><span class="badge ${statusClass}">${statusText}</span></td>
                            <td>${agent.capabilities ? agent.capabilities.join(', ') : 'None'}</td>
                            <td>
                                <button onclick="quarantine('${agent.agent_id}')" 
                                        style="background: #e74c3c; color: white; border: none; padding: 5px 10px; border-radius: 5px; cursor: pointer;">
                                    🛑 Quarantine
                                </button>
                            </td>
                        `;
                        tbody.appendChild(tr);
                    });
                    
                    const alertsRes = await fetch('/api/alerts');
                    const alerts = await alertsRes.json();
                    const alertDiv = document.getElementById('alertsContent');
                    if (alerts.length === 0) {
                        alertDiv.innerHTML = '<p style="color: #2ecc71;">✅ No alerts - All agents are behaving normally!</p>';
                    } else {
                        let html = '<ul style="color: #856404; padding-left: 20px;">';
                        alerts.slice(0, 5).forEach(alert => {
                            html += `<li>${alert.timestamp} - <strong>${alert.alert_type}</strong> for ${alert.agent_id} → ${alert.action || 'Logged'}</li>`;
                        });
                        html += '</ul>';
                        if (alerts.length > 5) {
                            html += `<p style="color: #666;">... and ${alerts.length - 5} more alerts</p>`;
                        }
                        alertDiv.innerHTML = html;
                    }
                } catch (error) {
                    console.error('Error fetching data:', error);
                }
            }

            async function quarantine(agentId) {
                if (confirm(`Quarantine agent ${agentId}?`)) {
                    const response = await fetch(`/api/quarantine/${agentId}`, { method: 'POST' });
                    const result = await response.json();
                    alert(result.message);
                    fetchData();
                }
            }

            fetchData();
            setInterval(fetchData, 5000);
        </script>
    </body>
    </html>
    """

@app.get("/api/agents")
async def get_agents():
    """Get all agents"""
    if not system:
        return []
    
    return [agent.to_dict() for agent in system.discovery.discovered_agents.values()]

@app.get("/api/stats")
async def get_stats():
    """Get system statistics"""
    if not system:
        return {
            "total_agents": 0,
            "high_risk": 0,
            "unauthorized": 0,
            "authorized": 0,
            "alerts": 0,
            "responses": 0
        }
    
    agents = system.discovery.discovered_agents.values()
    high_risk = sum(1 for a in agents if a.risk_score > 50)
    unauthorized = sum(1 for a in agents if not a.is_authorized)
    
    return {
        "total_agents": len(agents),
        "high_risk": high_risk,
        "unauthorized": unauthorized,
        "authorized": len(agents) - unauthorized,
        "alerts": system.monitor.alert_count if system.monitor else 0,
        "responses": len(system.response.response_log) if system.response else 0
    }

@app.get("/api/alerts")
async def get_alerts():
    """Get recent alerts"""
    if not system or not system.response:
        return []
    
    return system.response.response_log[-10:]

@app.get("/api/logs")
async def get_logs():
    """Get recent logs"""
    return [
        {"timestamp": datetime.now().isoformat(), "level": "log-info", "message": "System is monitoring agents..."},
        {"timestamp": datetime.now().isoformat(), "level": "log-info", "message": "4 agents discovered"},
        {"timestamp": datetime.now().isoformat(), "level": "log-info", "message": "Real-time monitoring active..."}
    ]

@app.post("/api/quarantine/{agent_id}")
async def quarantine_agent(agent_id: str):
    """Quarantine an agent"""
    if not system:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    if agent_id in system.discovery.discovered_agents:
        agent = system.discovery.discovered_agents[agent_id]
        agent.is_authorized = False
        return {"status": "success", "message": f"Agent {agent.name} has been quarantined"}
    
    raise HTTPException(status_code=404, detail="Agent not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)