"""
Simple DDoS Simulation using requests library (synchronous)
Easier to run - just needs requests library which is likely already installed.
"""
import requests
import time
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:8000"
TOTAL_REQUESTS = 120  # More than the 100/minute limit
TEST_ENDPOINT = "/"  # Public root endpoint (no auth required)


def test_rate_limit():
    """Simple rate limit test."""
    print("\n" + "="*60)
    print("🔒 Simple Rate Limiting Test")
    print("="*60)
    print(f"Target: {API_BASE_URL}{TEST_ENDPOINT}")
    print(f"Total Requests: {TOTAL_REQUESTS}")
    print(f"Expected Rate Limit: 100 requests/minute")
    print("="*60 + "\n")
    
    url = f"{API_BASE_URL}{TEST_ENDPOINT}"
    results = {
        'success': 0,
        'rate_limited': 0,
        'errors': 0,
        'first_rate_limit': None
    }
    
    start_time = time.time()
    
    for i in range(1, TOTAL_REQUESTS + 1):
        try:
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                results['success'] += 1
                print(f"✅ Request {i:3d}: Success (200)")
            elif response.status_code == 429:
                results['rate_limited'] += 1
                if results['first_rate_limit'] is None:
                    results['first_rate_limit'] = i
                    print(f"\n🚨 RATE LIMIT TRIGGERED at request #{i}!\n")
                print(f"🛡️  Request {i:3d}: Rate Limited (429)")
            else:
                results['errors'] += 1
                print(f"❌ Request {i:3d}: Error ({response.status_code})")
        
        except requests.exceptions.RequestException as e:
            results['errors'] += 1
            print(f"❌ Request {i:3d}: Connection Error - {str(e)[:50]}")
        
        # Small delay to avoid overwhelming the system
        time.sleep(0.05)
    
    end_time = time.time()
    duration = end_time - start_time
    
    # Print results
    print("\n" + "="*60)
    print("📊 Test Results")
    print("="*60)
    print(f"\n⏱️  Duration: {duration:.2f} seconds")
    print(f"📈 Rate: {TOTAL_REQUESTS / duration:.2f} requests/second")
    print(f"\n📦 Summary:")
    print(f"   Total Requests: {TOTAL_REQUESTS}")
    print(f"   ✅ Successful: {results['success']}")
    print(f"   🛡️  Rate Limited: {results['rate_limited']}")
    print(f"   ❌ Errors: {results['errors']}")
    
    if results['first_rate_limit']:
        print(f"\n🚨 Rate Limiting:")
        print(f"   First blocked at request: #{results['first_rate_limit']}")
        print(f"   Allowed requests: {results['success']}")
        print(f"   Blocked requests: {results['rate_limited']}")
        print(f"   Block rate: {results['rate_limited'] / TOTAL_REQUESTS * 100:.1f}%")
    
    print("\n" + "="*60)
    if results['rate_limited'] > 0:
        print("✅ RATE LIMITING IS WORKING!")
        print(f"   Successfully blocked {results['rate_limited']} requests")
    else:
        print("⚠️  WARNING: No rate limiting detected!")
    print("="*60 + "\n")


if __name__ == "__main__":
    print("\n⚠️  Make sure your server is running:")
    print("   cd backend")
    print("   uvicorn app.main:app --reload\n")
    
    try:
        input("Press Enter to start the test (Ctrl+C to cancel)...")
        test_rate_limit()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test cancelled.\n")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        print("   Make sure the server is running!\n")
