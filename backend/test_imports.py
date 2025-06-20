#!/usr/bin/env python
"""Test script to verify Django model imports are working correctly"""

import os
import sys
import django

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# Test imports
try:
    from apps.ai_analytics.models import (
        RiskProfile, RiskIndicator, InterventionPlan, 
        AlertConfiguration, Alert
    )
    print("✅ AI Analytics models imported successfully")
    
    # Check JSONField usage
    risk_profile_fields = RiskProfile._meta.get_fields()
    json_fields = [f for f in risk_profile_fields if f.__class__.__name__ == 'JSONField']
    print(f"✅ Found {len(json_fields)} JSONField(s) in RiskProfile model")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

try:
    from apps.grades.admin import GeneralAverageAdmin, SubjectAverageAdmin
    print("✅ Grades admin classes imported successfully")
    
    # Check if SubjectAverageAdmin is registered
    from django.contrib import admin
    from apps.grades.models import SubjectAverage
    if admin.site.is_registered(SubjectAverage):
        print("✅ SubjectAverage model is properly registered in admin")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

print("\n🎉 All imports are working correctly!")