#!/usr/bin/env python3
"""
Test script for the hybrid ML/rule-based health analyzer
"""

import requests
import json
import time

def test_health_endpoint(base_url="http://localhost:5000"):
    """Test the health check endpoint"""
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            data = response.json()
            print("✅ Health check successful")
            print(f"   Status: {data['status']}")
            print(f"   ML Available: {data.get('ml_available', 'N/A')}")
            print(f"   Analysis Method: {data.get('analysis_method', 'N/A')}")
            return data
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Health check error: {str(e)}")
        return None

def test_single_analysis(base_url="http://localhost:5000"):
    """Test single text analysis"""
    test_cases = [
        "I have a terrible headache and feel very anxious about it",
        "I'm feeling great today, my exercise routine is working well",
        "I'm experiencing chest pain and shortness of breath",
        "I'm feeling a bit tired but overall okay"
    ]
    
    for i, text in enumerate(test_cases, 1):
        try:
            print(f"\n🧪 Test Case {i}: {text[:50]}...")
            
            response = requests.post(
                f"{base_url}/analyze-health",
                json={"text": text},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    result = data["data"]
                    print(f"   ✅ Analysis successful")
                    print(f"   📊 Urgency: {result.get('urgency_level', 'N/A')}")
                    print(f"   🧠 Sentiment: {result.get('sentiment_analysis', {}).get('sentiment', 'N/A')}")
                    print(f"   🔬 Method: {result.get('analysis_method', 'N/A')}")
                    print(f"   🤖 ML Available: {result.get('ml_available', 'N/A')}")
                else:
                    print(f"   ❌ Analysis failed: {result.get('error', 'Unknown error')}")
            else:
                print(f"   ❌ Request failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Test error: {str(e)}")
        
        time.sleep(0.5)  # Small delay between requests

def test_batch_analysis(base_url="http://localhost:5000"):
    """Test batch analysis"""
    texts = [
        "I have a headache",
        "I'm feeling anxious",
        "I need to exercise more",
        "I have diabetes"
    ]
    
    try:
        print(f"\n🧪 Batch Analysis Test")
        
        response = requests.post(
            f"{base_url}/analyze-health-batch",
            json={"texts": texts},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                results = data["data"]
                summary = data.get("summary", {})
                print(f"   ✅ Batch analysis successful")
                print(f"   📊 Total processed: {summary.get('total', 0)}")
                print(f"   ✅ Valid results: {summary.get('valid', 0)}")
                print(f"   ❌ Errors: {summary.get('errors', 0)}")
                
                # Show first result details
                if results:
                    first_result = results[0]
                    print(f"   🔬 First result method: {first_result.get('analysis_method', 'N/A')}")
                    print(f"   🤖 ML Available: {first_result.get('ml_available', 'N/A')}")
            else:
                print(f"   ❌ Batch analysis failed: {data.get('error', 'Unknown error')}")
        else:
            print(f"   ❌ Request failed: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Batch test error: {str(e)}")

def main():
    """Main test function"""
    print("🚀 Testing Hybrid ML/Rule-based Health Analyzer")
    print("=" * 50)
    
    # Test health endpoint
    health_data = test_health_endpoint()
    
    if health_data:
        # Test single analysis
        test_single_analysis()
        
        # Test batch analysis
        test_batch_analysis()
        
        print("\n" + "=" * 50)
        print("🎉 Testing completed!")
        
        # Summary
        ml_available = health_data.get('ml_available', False)
        analysis_method = health_data.get('analysis_method', 'unknown')
        
        print(f"\n📋 Summary:")
        print(f"   ML Models: {'✅ Available' if ml_available else '❌ Not Available'}")
        print(f"   Analysis Method: {analysis_method}")
        
        if ml_available:
            print("   💡 Using ML-enhanced analysis with RoBERTa sentiment analysis")
        else:
            print("   💡 Using rule-based analysis (suitable for deployment)")
            
    else:
        print("❌ Cannot run tests - health endpoint not available")
        print("   Make sure the server is running: python app.py")

if __name__ == "__main__":
    main() 