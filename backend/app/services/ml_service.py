import pickle
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional
from datetime import datetime
import lightgbm as lgb
from sklearn.preprocessing import StandardScaler
from ..config import settings


class MLPredictionService:
    """Service for ML-based workload prediction and task analysis."""
    
    def __init__(self):
        self.model = None
        self.scaler = None
        self.is_trained = False
        self._load_or_create_model()
    
    def _load_or_create_model(self):
        """Load existing model or create a new one if none exists."""
        try:
            # In a real implementation, you would load a pre-trained model
            # For now, we'll create a simple rule-based model
            self._create_rule_based_model()
            self.is_trained = True
        except Exception as e:
            print(f"Error loading model: {str(e)}")
            self._create_rule_based_model()
            self.is_trained = True
    
    def _create_rule_based_model(self):
        """Create a simple rule-based model for initial predictions."""
        # This is a placeholder for a trained ML model
        # In production, you would train this on historical data
        self.base_hours = {
            "Assignment": 3.0,
            "Exam": 8.0,
            "Quiz": 2.0,
            "Project": 12.0,
            "Reading": 1.5,
            "Lab": 4.0
        }
    
    async def predict_workload(self, task_data: Dict[str, Any]) -> float:
        """
        Predict the workload (hours needed) for a given task.
        
        Args:
            task_data: Dictionary containing task information
            
        Returns:
            Predicted hours needed to complete the task
        """
        try:
            if self.is_trained and self.model:
                return await self._ml_predict(task_data)
            else:
                return self._rule_based_predict(task_data)
                
        except Exception as e:
            print(f"Prediction error: {str(e)}")
            # Fallback to rule-based prediction
            return self._rule_based_predict(task_data)
    
    async def _ml_predict(self, task_data: Dict[str, Any]) -> float:
        """
        Make prediction using trained ML model.
        
        Args:
            task_data: Task information dictionary
            
        Returns:
            Predicted hours
        """
        # Extract features for ML model
        features = self._extract_features(task_data)
        
        # Scale features if scaler is available
        if self.scaler:
            features = self.scaler.transform([features])
        else:
            features = [features]
        
        # Make prediction
        prediction = self.model.predict(features)[0]
        
        # Ensure prediction is reasonable
        return max(0.5, min(prediction, 40.0))  # Between 0.5 and 40 hours
    
    def _rule_based_predict(self, task_data: Dict[str, Any]) -> float:
        """
        Make prediction using rule-based approach.
        
        Args:
            task_data: Task information dictionary
            
        Returns:
            Predicted hours
        """
        task_type = task_data.get("task_type", "Assignment")
        grade_percentage = task_data.get("grade_percentage", 0)
        description_length = len(task_data.get("description", ""))
        
        # Base hours for task type
        base_hours = self.base_hours.get(task_type, 3.0)
        
        # Adjust based on grade percentage
        grade_multiplier = 1.0 + (grade_percentage / 100.0) * 0.5
        
        # Adjust based on description length (complexity indicator)
        complexity_multiplier = 1.0 + min(description_length / 500, 0.5)
        
        # Adjust based on instructor keywords
        keywords = task_data.get("instructor_keywords", [])
        keyword_multiplier = 1.0
        for keyword in keywords:
            if keyword.lower() in ["critical", "major", "comprehensive"]:
                keyword_multiplier += 0.3
            elif keyword.lower() in ["important", "significant"]:
                keyword_multiplier += 0.2
            elif keyword.lower() in ["challenging", "difficult"]:
                keyword_multiplier += 0.15
        
        # Calculate final prediction
        predicted_hours = base_hours * grade_multiplier * complexity_multiplier * keyword_multiplier
        
        # Add some randomness to simulate real-world variation
        noise = np.random.normal(0, 0.1)
        predicted_hours *= (1 + noise)
        
        # Ensure reasonable bounds
        return max(0.5, min(predicted_hours, 40.0))
    
    def _extract_features(self, task_data: Dict[str, Any]) -> List[float]:
        """
        Extract numerical features from task data for ML model.
        
        Args:
            task_data: Task information dictionary
            
        Returns:
            List of numerical features
        """
        features = []
        
        # Task type (one-hot encoded)
        task_types = ["Assignment", "Exam", "Quiz", "Project", "Reading", "Lab"]
        task_type = task_data.get("task_type", "Assignment")
        for t in task_types:
            features.append(1.0 if t == task_type else 0.0)
        
        # Grade percentage
        features.append(float(task_data.get("grade_percentage", 0)))
        
        # Description length
        features.append(float(len(task_data.get("description", ""))))
        
        # Days until due
        due_date = task_data.get("due_date")
        if due_date:
            try:
                due_datetime = datetime.strptime(due_date, "%Y-%m-%d")
                days_until = (due_datetime - datetime.now()).days
                features.append(float(max(0, days_until)))
            except:
                features.append(30.0)  # Default to 30 days
        else:
            features.append(30.0)
        
        # Instructor keywords count
        keywords = task_data.get("instructor_keywords", [])
        features.append(float(len(keywords)))
        
        # Importance indicators
        important_keywords = ["critical", "major", "important", "mandatory", "required"]
        importance_score = sum(1 for k in keywords if k.lower() in important_keywords)
        features.append(float(importance_score))
        
        return features
    
    async def update_model_with_feedback(self, task_data: Dict[str, Any], actual_hours: float):
        """
        Update the model with actual completion time feedback.
        
        Args:
            task_data: Original task data
            actual_hours: Actual hours taken to complete the task
        """
        try:
            # In a real implementation, you would:
            # 1. Store this feedback data
            # 2. Periodically retrain the model with new data
            # 3. Update the model file
            
            # For now, we'll just log the feedback
            print(f"Model feedback: Task '{task_data.get('title')}' - Predicted vs Actual: {task_data.get('predicted_hours')} vs {actual_hours}")
            
            # Store feedback for future model training
            feedback_data = {
                "task_data": task_data,
                "actual_hours": actual_hours,
                "timestamp": datetime.now().isoformat()
            }
            
            # In production, save this to a database or file
            # await self._save_feedback(feedback_data)
            
        except Exception as e:
            print(f"Error updating model with feedback: {str(e)}")
    
    async def get_model_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the ML model performance.
        
        Returns:
            Dictionary containing model statistics
        """
        try:
            # In a real implementation, you would calculate actual statistics
            # For now, return placeholder data
            return {
                "model_type": "LightGBM" if self.model else "Rule-based",
                "is_trained": self.is_trained,
                "total_predictions": 0,  # Would track this in production
                "average_accuracy": 0.85,  # Would calculate from validation data
                "last_updated": datetime.now().isoformat(),
                "feature_importance": {
                    "task_type": 0.35,
                    "grade_percentage": 0.25,
                    "description_length": 0.15,
                    "days_until_due": 0.15,
                    "instructor_keywords": 0.10
                }
            }
        except Exception as e:
            return {"error": str(e)}
    
    def train_model(self, training_data: List[Dict[str, Any]]):
        """
        Train the ML model with historical data.
        
        Args:
            training_data: List of historical task data with actual hours
        """
        try:
            if not training_data or len(training_data) < 10:
                print("Insufficient training data")
                return
            
            # Prepare training data
            X = []
            y = []
            
            for data_point in training_data:
                features = self._extract_features(data_point["task_data"])
                actual_hours = data_point["actual_hours"]
                
                X.append(features)
                y.append(actual_hours)
            
            X = np.array(X)
            y = np.array(y)
            
            # Scale features
            self.scaler = StandardScaler()
            X_scaled = self.scaler.fit_transform(X)
            
            # Train LightGBM model
            self.model = lgb.LGBMRegressor(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=6,
                random_state=42
            )
            
            self.model.fit(X_scaled, y)
            self.is_trained = True
            
            print("Model training completed successfully")
            
        except Exception as e:
            print(f"Model training failed: {str(e)}")
            self._create_rule_based_model()


# Create a singleton instance
ml_service = MLPredictionService()