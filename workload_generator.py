import requests
import time
import numpy as np
import matplotlib.pyplot as plt
from concurrent.futures import ThreadPoolExecutor
import uuid

URL = "https://serverless-app-1070589510446.europe-west8.run.app/compute"
#https://factorization-service-cloud.orangestone-19b7850d.italynorth.azurecontainerapps.io
#https://serverless-app-1070589510446.europe-west8.run.app
def send_request(req_id):
    """ Sends a request to the Cloud Run service and logs timing details. """
    start_time = time.time()
    try:
        response = requests.get(URL, params={"n": "62340", "req_id": req_id}, timeout=650)
        response.raise_for_status()
        end_time = time.time()
        return end_time - start_time
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None


def test_load(requests_per_second):
    """ Tests the system under load and returns performance metrics. """
    total_start_time = time.time()
    # it spawns multiple threads, each making an HTTP request in parallel.
    with ThreadPoolExecutor(max_workers=requests_per_second) as executor:
        req_ids = [str(uuid.uuid4()) for _ in range(requests_per_second)]
        times = list(executor.map(send_request, req_ids))

    total_end_time = time.time()
    total_time = total_end_time - total_start_time

    # filter out failed requests
    successful_times = [t for t in times if t is not None]

    if not successful_times:
        return float('inf'), 0

    # Calculate metrics
    successful_requests = len(successful_times)
    avg_exec_time = np.mean(successful_times)
    throughput = successful_requests / total_time  # Actual requests completed per second

    return avg_exec_time, throughput


def run_load_tests():
    """ Runs the complete set of load tests and generates plots. """
    request_counts = [1, 10, 50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]
    execution_times = []
    throughputs = []
    speedups = []

    # baseline metrics
    baseline_exec_time, baseline_throughput = test_load(1)
    print(f"[BASELINE] Execution Time: {baseline_exec_time:.2f}s, Throughput: {baseline_throughput:.2f} req/s")

    # Run tests for each request count
    for reqs in request_counts:
        print(f"\n[TEST] Running load test with {reqs} requests per second...")
        exec_time, throughput = test_load(reqs)

        # Store results
        execution_times.append(exec_time)
        throughputs.append(throughput)
        speedup = throughput / baseline_throughput if baseline_throughput > 0 else 0
        speedups.append(speedup)

        print(f"[RESULT] {reqs} RPS -> Execution Time: {exec_time:.2f}s, Throughput: {throughput:.2f} req/s")

    # create plots
    plt.figure(figsize=(15, 5))

    # Execution Time plot
    plt.subplot(1, 3, 1)
    plt.plot(request_counts, execution_times, marker='o', label="Execution Time")
    plt.xlabel("Requests per Second")
    plt.ylabel("Execution Time (s)")
    plt.title("Execution Time vs Requests per Second")
    plt.grid(True)
    plt.legend()

    # Throughput plot
    plt.subplot(1, 3, 2)
    plt.plot(request_counts, throughputs, marker='s', label="Throughput")
    plt.xlabel("Requests per Second")
    plt.ylabel("Throughput (req/s)")
    plt.title("Throughput vs Requests per Second")
    plt.grid(True)
    plt.legend()

    # Speedup plot
    plt.subplot(1, 3, 3)
    plt.plot(request_counts, speedups, marker='^', label="Speedup")
    plt.xlabel("Requests per Second")
    plt.ylabel("Speedup Factor")
    plt.title("Speedup vs Requests per Second")
    plt.grid(True)
    plt.legend()

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    run_load_tests()