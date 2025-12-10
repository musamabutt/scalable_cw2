import time
import requests
from concurrent.futures import ThreadPoolExecutor

URL = "https://videoapp-esbxhscadcg8d8bc.uksouth-01.azurewebsites.net/videos"   # change to your local FastAPI route

def run_request():
    start = time.time()
    r = requests.get(URL)
    end = time.time()
    return end - start

def run_load_test(num_requests=50, workers=10):
    print(f"Running load test: {num_requests} requests using {workers} workers")

    with ThreadPoolExecutor(max_workers=workers) as executor:
        results = list(executor.map(lambda _: run_request(), range(num_requests)))

    avg = sum(results) / len(results)
    mx = max(results)
    mn = min(results)

    print("\n--- Load Test Results ---")
    print(f"Average response time: {avg:.4f}s")
    print(f"Fastest response: {mn:.4f}s")
    print(f"Slowest response: {mx:.4f}s")

if __name__ == "__main__":
    run_load_test(50, 10)
