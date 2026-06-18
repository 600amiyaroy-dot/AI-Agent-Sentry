"""
ML-based Anomaly Detection - Advanced
"""
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib
import os
import logging

logger = logging.getLogger(__name__)

class MLAnomalyDetector:
    """Machine Learning powered anomaly detection"""
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.trained = False
        self.model_path = "models/anomaly_model.pkl"
        
    def train(self, training_data):
        """Train the model on historical data"""
        logger.info("Training ML model...")
        
        if len(training_data) < 10:
            logger.warning("Not enough data for training")
            return
            
        # Extract features
        features = self._extract_features(training_data)
        scaled_features = self.scaler.fit_transform(features)
        
        # Train Isolation Forest
        self.model = IsolationForest(
            contamination=0.1,
            random_state=42,
            n_estimators=100
        )
        self.model.fit(scaled_features)
        self.trained = True
        
        # Save model
        os.makedirs("models", exist_ok=True)
        joblib.dump((self.model, self.scaler), self.model_path)
        logger.info("ML model trained and saved!")
    
    def detect(self, activities):
        """Detect anomalies in real-time"""
        if not self.trained:
            logger.warning("Model not trained yet!")
            return []
            
        features = self._extract_features(activities)
        scaled_features = self.scaler.transform(features)
        
        predictions = self.model.predict(scaled_features)
        scores = self.model.score_samples(scaled_features)
        
        anomalies = []
        for i, (pred, score) in enumerate(zip(predictions, scores)):
            if pred == -1 and abs(score) > 0.15:
                anomalies.append({
                    'activity_id': activities[i].activity_id,
                    'agent_id': activities[i].agent_id,
                    'anomaly_score': float(score),
                    'timestamp': activities[i].timestamp.isoformat()
                })
        
        return anomalies
    
    def _extract_features(self, activities):
        """Extract numeric features from activities"""
        features = []
        for activity in activities:
            # Feature 1: Activity frequency
            freq = len([a for a in activities if a.agent_id == activity.agent_id])
            
            # Feature 2: Data volume
            volume = activity.data_volume or 0
            
            # Feature 3: Time patterns
            hour = activity.timestamp.hour
            day = activity.timestamp.weekday()
            
            features.append([freq, volume, hour, day])
        
        return np.array(features)

# Add this to your main system
async def run_ml_detection():
    """Run ML detection on historical data"""
    detector = MLAnomalyDetector()
    
    # Use your monitor's activity log as training data
    # detector.train(monitor.activity_log[:50])
    
    # Detect anomalies in real-time
    # anomalies = detector.detect(monitor.activity_log[-10:])