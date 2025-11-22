#!/usr/bin/env python3
"""
Model Retraining Script
Run this script to retrain ML models with new survey data from production
"""

import os
import sys
import pandas as pd
from datetime import datetime
import joblib
from pathlib import Path

# Add the parent directory to the path so we can import from app
sys.path.append(str(Path(__file__).parent.parent))

from app.database import get_supabase_admin
from app.ml.weight_calculator import TaskWeightCalculator
from app.ml.priority_calculator import PriorityCalculator

def fetch_survey_data():
    """Fetch all survey data from Supabase"""
    print("📊 Fetching survey data from Supabase...")
    
    supabase = get_supabase_admin()
    if not supabase:
        raise Exception("Could not connect to Supabase")
    
    # Fetch survey responses
    response = supabase.table("survey_responses").select("*").execute()
    
    if not response.data:
        print("⚠️  No survey data found")
        return None
    
    df = pd.DataFrame(response.data)
    print(f"✅ Found {len(df)} survey responses")
    return df

def retrain_weight_calculator(survey_df):
    """Retrain the task weight calculator with new data"""
    print("\n🔄 Retraining Weight Calculator...")
    
    # Initialize calculator
    calculator = TaskWeightCalculator()
    
    # Prepare training data from survey responses
    # This assumes survey_df has columns matching the expected features
    if len(survey_df) < 10:
        print("⚠️  Not enough data to retrain weight calculator (need at least 10 samples)")
        return False
    
    try:
        # Train the model (you may need to adjust this based on your survey schema)
        calculator.train_model(survey_df)
        
        # Save the updated model
        model_path = Path(__file__).parent.parent / "models" / "weight_model.joblib"
        model_path.parent.mkdir(parents=True, exist_ok=True)
        
        joblib.dump(calculator.model, model_path)
        print(f"✅ Weight calculator model saved to {model_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error retraining weight calculator: {e}")
        return False

def retrain_priority_calculator(survey_df):
    """Retrain the priority calculator with new data"""
    print("\n🔄 Retraining Priority Calculator...")
    
    # Initialize calculator
    calculator = PriorityCalculator()
    
    if len(survey_df) < 10:
        print("⚠️  Not enough data to retrain priority calculator (need at least 10 samples)")
        return False
    
    try:
        # Train the model
        calculator.train_model(survey_df)
        
        # Save the updated model
        model_path = Path(__file__).parent.parent / "models" / "priority_model.joblib"
        model_path.parent.mkdir(parents=True, exist_ok=True)
        
        joblib.dump(calculator.model, model_path)
        print(f"✅ Priority calculator model saved to {model_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error retraining priority calculator: {e}")
        return False

def update_model_metadata():
    """Update model metadata with retraining timestamp"""
    metadata = {
        "last_retrained": datetime.now().isoformat(),
        "version": "1.0.0"
    }
    
    metadata_path = Path(__file__).parent.parent / "models" / "metadata.json"
    
    import json
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"✅ Model metadata updated: {metadata_path}")

def main():
    """Main retraining workflow"""
    print("🚀 Starting Model Retraining Process")
    print("=" * 50)
    
    try:
        # Fetch new survey data
        survey_df = fetch_survey_data()
        
        if survey_df is None or len(survey_df) == 0:
            print("❌ No survey data available for retraining")
            return False
        
        print(f"📈 Training with {len(survey_df)} survey responses")
        
        # Retrain models
        weight_success = retrain_weight_calculator(survey_df)
        priority_success = retrain_priority_calculator(survey_df)
        
        if weight_success or priority_success:
            update_model_metadata()
            print("\n🎉 Model retraining completed successfully!")
            print("\n📝 Next steps:")
            print("1. Test the updated models locally")
            print("2. Commit and push changes to GitHub")
            print("3. GitHub Actions will automatically deploy to Google Cloud Run")
            return True
        else:
            print("\n❌ Model retraining failed")
            return False
            
    except Exception as e:
        print(f"\n❌ Error during retraining: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
