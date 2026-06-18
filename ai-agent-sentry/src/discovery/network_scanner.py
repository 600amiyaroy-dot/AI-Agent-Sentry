"""
Enterprise Network Scanner
Real-time scanning for AI agents
"""

import asyncio
import socket
import subprocess
import aiohttp
from typing import List, Dict
import nmap  # pip install python-nmap
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class EnterpriseNetworkScanner:
    """Enterprise-grade network scanning"""
    
    def __init__(self):
        self.nm = nmap.PortScanner()
        self.common_ports = {
            'openai': [443, 5000, 8000],
            'anthropic': [443],
            'google_ai': [443, 8443],
            'azure_openai': [443, 8080],
            'custom_ai': [5000, 8000, 8080, 8443, 3000, 5001]
        }
        self.known_patterns = {
            'openai': ['api.openai.com', 'openai'],
            'anthropic': ['api.anthropic.com', 'anthropic'],
            'google': ['generativeai.googleapis.com', 'google'],
            'azure': ['azure.ai.openai', 'azure'],
            'custom': ['/api/v1/', '/v1/', '/chat', '/completion']
        }
    
    async def scan_network(self, network_range='192.168.1.0/24'):
        """Scan network for AI agents"""
        logger.info(f"🔍 Scanning network: {network_range}")
        
        discovered = []
        
        # Phase 1: Quick port scan
        live_hosts = await self._quick_scan(network_range)
        logger.info(f"Found {len(live_hosts)} live hosts")
        
        # Phase 2: Deep scan on live hosts
        for host in live_hosts:
            agents = await self._deep_scan_host(host)
            discovered.extend(agents)
        
        logger.info(f"✅ Found {len(discovered)} AI agents on network")
        return discovered
    
    async def _quick_scan(self, network_range):
        """Quick scan to find live hosts"""
        try:
            self.nm.scan(network_range, arguments='-sn -T4')
            return list(self.nm.all_hosts())
        except Exception as e:
            logger.error(f"Network scan failed: {e}")
            return []
    
    async def _deep_scan_host(self, host):
        """Deep scan individual host"""
        agents = []
        
        # Scan common ports
        for service, ports in self.common_ports.items():
            for port in ports:
                try:
                    if await self._check_port(host, port):
                        # Check if it's an AI service
                        if await self._is_ai_service(host, port):
                            agent = {
                                'host': host,
                                'port': port,
                                'service': service,
                                'endpoint': f"http://{host}:{port}",
                                'type': 'ai_api',
                                'capabilities': await self._detect_capabilities(host, port),
                                'risk_score': 50  # Default risk
                            }
                            agents.append(agent)
                except Exception as e:
                    continue
        
        return agents
    
    async def _check_port(self, host, port, timeout=1):
        """Check if port is open"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except:
            return False
    
    async def _is_ai_service(self, host, port):
        """Check if service is AI-related"""
        try:
            # Try to access common AI endpoints
            endpoints = [
                '/v1/chat/completions',
                '/v1/completions',
                '/generate',
                '/api/chat',
                '/predict'
            ]
            
            async with aiohttp.ClientSession() as session:
                for endpoint in endpoints:
                    try:
                        url = f"http://{host}:{port}{endpoint}"
                        async with session.get(url, timeout=2) as resp:
                            if resp.status < 500:
                                return True
                    except:
                        continue
            return False
        except:
            return False
    
    async def _detect_capabilities(self, host, port):
        """Detect what the AI agent can do"""
        capabilities = []
        
        # Try different endpoints to detect capabilities
        test_endpoints = {
            '/chat': 'chat',
            '/completion': 'completion', 
            '/embedding': 'embedding',
            '/classification': 'classification',
            '/generate': 'generation',
            '/analyze': 'analysis'
        }
        
        async with aiohttp.ClientSession() as session:
            for endpoint, capability in test_endpoints.items():
                try:
                    url = f"http://{host}:{port}{endpoint}"
                    async with session.get(url, timeout=1) as resp:
                        if resp.status < 500:
                            capabilities.append(capability)
                except:
                    continue
        
        return capabilities

class AWSScanner:
    """Scan AWS for AI services"""
    
    async def scan_aws(self, region='us-east-1'):
        """Scan AWS for AI services"""
        discovered = []
        
        try:
            import boto3  # pip install boto3
            
            # Check SageMaker endpoints
            sagemaker = boto3.client('sagemaker', region_name=region)
            endpoints = sagemaker.list_endpoints()
            
            for endpoint in endpoints['Endpoints']:
                if endpoint['Status'] == 'InService':
                    agent = {
                        'service': 'AWS SageMaker',
                        'name': endpoint['EndpointName'],
                        'endpoint': endpoint['EndpointArn'],
                        'type': 'aws_sagemaker',
                        'capabilities': ['ml_prediction'],
                        'risk_score': 30
                    }
                    discovered.append(agent)
            
            # Check Bedrock
            bedrock = boto3.client('bedrock', region_name=region)
            models = bedrock.list_foundation_models()
            
            for model in models.get('modelSummaries', []):
                agent = {
                    'service': 'AWS Bedrock',
                    'name': model['modelId'],
                    'type': 'aws_bedrock',
                    'capabilities': [model.get('outputModality', 'text')],
                    'risk_score': 20
                }
                discovered.append(agent)
                
        except ImportError:
            logger.warning("boto3 not installed. AWS scanning disabled.")
        except Exception as e:
            logger.error(f"AWS scan failed: {e}")
        
        return discovered

class AzureScanner:
    """Scan Azure for AI services"""
    
    async def scan_azure(self, subscription_id=None):
        """Scan Azure for AI services"""
        discovered = []
        
        try:
            from azure.identity import DefaultAzureCredential  # pip install azure-identity
            from azure.mgmt.cognitiveservices import CognitiveServicesManagementClient
            
            credential = DefaultAzureCredential()
            client = CognitiveServicesManagementClient(
                credential=credential,
                subscription_id=subscription_id
            )
            
            for account in client.accounts.list():
                if 'openai' in account.kind.lower():
                    agent = {
                        'service': 'Azure OpenAI',
                        'name': account.name,
                        'endpoint': account.properties.endpoint,
                        'type': 'azure_openai',
                        'capabilities': ['chat', 'completion'],
                        'risk_score': 30
                    }
                    discovered.append(agent)
                    
        except ImportError:
            logger.warning("Azure SDK not installed. Azure scanning disabled.")
        except Exception as e:
            logger.error(f"Azure scan failed: {e}")
        
        return discovered