#!/usr/bin/env python3
"""
Simple test script to verify the health chatbot backend works correctly.
Run this before deploying to ensure everything is working.
"""

import requests
import json
import sys

def test_health_endpoint(base_url):
    """Test the health check endpoint"""
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            data = response.json()
            print("✅ Health endpoint working:", data)
            return True
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")
        return False

def test_health_analysis(base_url):
    """Test the health analysis endpoint"""
    try:
        test_data = {
            "text": "I have a headache and feel tired"
        }
        response = requests.post(
            f"{base_url}/analyze-health",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("✅ Health analysis working")
                print(f"   Urgency: {data['data'].get('urgency_level', 'unknown')}")
                print(f"   Categories: {list(data['data'].get('health_categories', {}).keys())}")
                return True
            else:
                print(f"❌ Health analysis failed: {data.get('error')}")
                return False
        else:
            print(f"❌ Health analysis HTTP error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health analysis error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Health Chatbot Backend...")
    
    # Test local deployment
    base_url = "http://localhost:5000"
    
    print(f"\n📍 Testing against: {base_url}")
    
    # Test health endpoint
    health_ok = test_health_endpoint(base_url)
    
    # Test health analysis
    analysis_ok = test_health_analysis(base_url)
    
    # Summary
    print(f"\n📊 Test Results:")
    print(f"   Health Endpoint: {'✅ PASS' if health_ok else '❌ FAIL'}")
    print(f"   Health Analysis: {'✅ PASS' if analysis_ok else '❌ FAIL'}")
    
    if health_ok and analysis_ok:
        print("\n🎉 All tests passed! Backend is ready for deployment.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please check the backend before deploying.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 