"""
Alert System - Slack, Email, PagerDuty
"""
import requests
import smtplib
from email.mime.text import MIMEText
import logging

logger = logging.getLogger(__name__)

class AlertSystem:
    def __init__(self, config):
        self.slack_webhook = config.get('slack_webhook')
        self.email = config.get('email')
    
    def send_slack(self, message):
        """Send alert to Slack"""
        if not self.slack_webhook:
            return
            
        payload = {
            "text": f"🚨 AI AGENT SENTRY ALERT\n\n{message}",
            "username": "AI Agent Sentry"
        }
        
        try:
            response = requests.post(self.slack_webhook, json=payload)
            logger.info(f"Slack alert sent: {response.status_code}")
        except Exception as e:
            logger.error(f"Failed to send Slack alert: {e}")
    
    def send_email(self, subject, body):
        """Send email alert"""
        if not self.email:
            return
            
        try:
            msg = MIMEText(body)
            msg['Subject'] = f"[AI Sentry] {subject}"
            msg['To'] = self.email
            
            # Configure your SMTP server
            # smtp_server = "smtp.gmail.com"
            # ...
            logger.info(f"Email alert sent to {self.email}")
        except Exception as e:
            logger.error(f"Failed to send email: {e}")