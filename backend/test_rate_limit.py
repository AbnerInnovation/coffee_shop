"""
DDoS Simulation Script to Test Rate Limiting

This script simulates a DDoS attack by making rapid requests to the API
to verify that rate limiting is working correctly.
"""
import asyncio
import aiohttp
import time
from typing import Dict, List
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:8000"
TOTAL_REQUESTS = 150  # More than the 100/minute limit
CONCURRENT_REQUESTS = 10  # Number of concurrent requests
TEST_ENDPOINT = "/"  # Public root endpoint (no auth required)


class RateLimitTester:
    def __init__(self, base_url: str, endpoint: str):
        self.base_url = base_url
        self.endpoint = endpoint
        self.results: List[Dict] = []
        self.start_time = None
        self.end_time = None
    
    async def make_request(self, session: aiohttp.ClientSession, request_num: int):
        """Make a single request and record the result."""
        url = f"{self.base_url}{self.endpoint}"
        try:
            start = time.time()
            async with session.get(url) as response:
                duration = time.time() - start
                result = {
                    'request_num': request_num,
                    'status': response.status,
                    'duration': duration,
                    'timestamp': datetime.now().isoformat(),
                    'rate_limited': response.status == 429
                }
                self.results.append(result)
                return result
        except Exception as e:
            result = {
                'request_num': request_num,
                'status': 'ERROR',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            self.results.append(result)
            return result
    
    async def run_batch(self, session: aiohttp.ClientSession, start_num: int, batch_size: int):
        """Run a batch of concurrent requests."""
        tasks = []
        for i in range(batch_size):
            task = self.make_request(session, start_num + i)
            tasks.append(task)
        
        return await asyncio.gather(*tasks)
    
    async def run_simulation(self, total_requests: int, concurrent: int):
        """Run the full DDoS simulation."""
        print(f"\n{'='*60}")
        print(f"🚀 Starting DDoS Simulation")
        print(f"{'='*60}")
        print(f"Target: {self.base_url}{self.endpoint}")
        print(f"Total Requests: {total_requests}")
        print(f"Concurrent Requests: {concurrent}")
        print(f"Expected Rate Limit: 100 requests/minute")
        print(f"{'='*60}\n")
        
        self.start_time = time.time()
        
        async with aiohttp.ClientSession() as session:
            # Run requests in batches
            for batch_start in range(0, total_requests, concurrent):
                batch_size = min(concurrent, total_requests - batch_start)
                print(f"📤 Sending requests {batch_start + 1} to {batch_start + batch_size}...")
                
                await self.run_batch(session, batch_start, batch_size)
                
                # Small delay between batches to simulate realistic traffic
                await asyncio.sleep(0.1)
        
        self.end_time = time.time()
        self.print_results()
    
    def print_results(self):
        """Print detailed results of the simulation."""
        total_duration = self.end_time - self.start_time
        successful = [r for r in self.results if r['status'] == 200]
        rate_limited = [r for r in self.results if r.get('rate_limited', False)]
        errors = [r for r in self.results if r['status'] not in [200, 429]]
        
        print(f"\n{'='*60}")
        print(f"📊 DDoS Simulation Results")
        print(f"{'='*60}\n")
        
        print(f"⏱️  Total Duration: {total_duration:.2f} seconds")
        print(f"📈 Requests per second: {len(self.results) / total_duration:.2f}")
        print(f"\n📦 Request Summary:")
        print(f"   Total Requests: {len(self.results)}")
        print(f"   ✅ Successful (200): {len(successful)}")
        print(f"   🛡️  Rate Limited (429): {len(rate_limited)}")
        print(f"   ❌ Errors: {len(errors)}")
        
        if rate_limited:
            first_rate_limit = rate_limited[0]['request_num']
            print(f"\n🚨 Rate Limiting Details:")
            print(f"   First rate-limited request: #{first_rate_limit}")
            print(f"   Rate limiting triggered after: {len(successful)} successful requests")
            print(f"   Percentage blocked: {len(rate_limited) / len(self.results) * 100:.1f}%")
        
        # Average response times
        if successful:
            avg_success_time = sum(r['duration'] for r in successful) / len(successful)
            print(f"\n⚡ Performance:")
            print(f"   Average response time (successful): {avg_success_time*1000:.2f}ms")
        
        if rate_limited:
            avg_blocked_time = sum(r['duration'] for r in rate_limited if 'duration' in r) / len(rate_limited)
            print(f"   Average response time (rate limited): {avg_blocked_time*1000:.2f}ms")
        
        # Status breakdown
        print(f"\n📋 Status Code Breakdown:")
        status_counts = {}
        for result in self.results:
            status = result['status']
            status_counts[status] = status_counts.get(status, 0) + 1
        
        for status, count in sorted(status_counts.items()):
            print(f"   {status}: {count} requests")
        
        # Verdict
        print(f"\n{'='*60}")
        if rate_limited:
            print(f"✅ RATE LIMITING IS WORKING!")
            print(f"   The API successfully blocked {len(rate_limited)} requests")
            print(f"   after allowing approximately {len(successful)} requests.")
        else:
            print(f"⚠️  WARNING: No rate limiting detected!")
            print(f"   All {len(successful)} requests were successful.")
            print(f"   Rate limiting may not be configured correctly.")
        print(f"{'='*60}\n")
        
        # Show first few rate-limited responses
        if rate_limited:
            print(f"📝 Sample Rate-Limited Responses (first 5):")
            for i, result in enumerate(rate_limited[:5], 1):
                print(f"   {i}. Request #{result['request_num']} - Status: {result['status']} - Time: {result['timestamp']}")
            print()


async def main():
    """Main function to run the simulation."""
    print("\n" + "="*60)
    print("🔒 Rate Limiting DDoS Simulation Test")
    print("="*60)
    print("\n⚠️  NOTE: Make sure your FastAPI server is running!")
    print("   Start it with: uvicorn app.main:app --reload")
    print("\n   Press Ctrl+C to cancel...\n")
    
    # Wait a moment for user to read
    await asyncio.sleep(2)
    
    tester = RateLimitTester(API_BASE_URL, TEST_ENDPOINT)
    
    try:
        await tester.run_simulation(TOTAL_REQUESTS, CONCURRENT_REQUESTS)
    except KeyboardInterrupt:
        print("\n\n⚠️  Simulation cancelled by user.")
    except Exception as e:
        print(f"\n\n❌ Error during simulation: {e}")
        print(f"   Make sure the server is running at {API_BASE_URL}")


if __name__ == "__main__":
    print("\n🚀 Starting Rate Limit Test...")
    asyncio.run(main())
