# FinBrain Project - simulate_login_load.py - MIT License (c) 2025 Nadav Eshed


import requests
import time
from concurrent.futures import ThreadPoolExecutor
import os
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv(dotenv_path="server/configs/.env.development")

# MY API URL
API_URL = "https://api.finbrain.uk/api/login"

# Email and password for the login request
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")

# Total number of login attempts
TOTAL_REQUESTS = 100000     

# How many to send at the same time
BATCH_SIZE = 10000       

# Number of times to repeat the batch
ROUNDS = TOTAL_REQUESTS // BATCH_SIZE  

# Total number of successful and failed login attempts
total_success = 0
total_failures = 0

# List to store the duration of each login attempt
all_durations = []


def send_login_request(index):
    """
    Send one login request
    """
    try:
        # Start the timer, send the request and stop the timer
        start = time.time()
        response = requests.post(API_URL, json={"email": EMAIL, "password": PASSWORD})
        duration = time.time() - start

        # Check if the login was successful
        if response.status_code == 200:
            return True, duration
        else:
            return False, duration
    except:
        return False, 0


if __name__ == "__main__":
    print(f"Starting {TOTAL_REQUESTS} login requests...")
    print(f"Sending {BATCH_SIZE} requests in parallel x {ROUNDS} rounds\n")

    # Start the timer
    test_start_time = time.time()

    # Send the requests in rounds
    for round_number in range(ROUNDS):
        print(f"--- Round {round_number + 1} ---")

        # Create a pool of threads and send all requests in parallel
        with ThreadPoolExecutor(max_workers=BATCH_SIZE) as executor:
            # executor.map(...) runs the send_login_request function for every number in range(BATCH_SIZE)
            # It executes them in parallel using threads
            # The result is an iterator of return values (tuples like (True, 0.21) or (False, 0.0))
            results = results = list(executor.map(send_login_request, range(BATCH_SIZE)))

        # Count how many succeeded/failed in this round
        round_success = 0
        round_failures = 0

        for success, duration in results:
            all_durations.append(duration)
            if success:
                round_success += 1
                total_success += 1
            else:
                round_failures += 1
                total_failures += 1

        print(f"Successful: {round_success} | Failed: {round_failures}\n")


    # === SUMMARY ===
    # Stop the timer and calculate the total duration, average time per request and total test duration
    test_end_time = time.time()
    total_duration = test_end_time - test_start_time
    average_time = sum(all_durations) / len(all_durations) if all_durations else 0

    print("Test Complete")
    print("----------------------------")
    print(f"Total Requests: {TOTAL_REQUESTS}")
    print(f"Successful: {total_success}")
    print(f"Failed: {total_failures}")
    print(f"Average Time per Request: {average_time:.2f} seconds")
    print(f"Total Test Duration: {total_duration:.2f} seconds")
