import time
import sys
import os

# Forces Python to check your local folders first
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vault.token_manager import generate_token
# FIXED: We now import from 'database' instead of 'redis'
from database.mapping import save_placeholder_mapping, get_real_data

def run_integration_test():
    print("🧪 Running Privacy Data Layer Integration Test...\n")
    
    total_start = time.time()
    
    # Step 1: Generate Token from Vault
    entity_type = "NAME"
    sensitive_data = "Dr. Alex Vance / 555-0199"
    token, gen_latency = generate_token(entity_type)
    
    # Step 2: Store Mapping in Persistent Redis
    save_latency = save_placeholder_mapping(token, sensitive_data)
    
    # Step 3: Perform Reverse Mapping Retrieval
    retrieved_data, fetch_latency = get_real_data(token)
    
    total_latency = (time.time() - total_start) * 1000
    
    # Print Performance Metrics
    print("--------------------------------------------------")
    print(f"1. Token Generated : {token} ({gen_latency:.3f} ms)")
    print(f"2. Data Stored    : {sensitive_data} ({save_latency:.3f} ms)")
    print(f"3. Data Retrieved : {retrieved_data} ({fetch_latency:.3f} ms)")
    print("--------------------------------------------------")
    
    if retrieved_data == sensitive_data:
        print("✅ INTEGRATION TEST PASSED: Full tokenization & reverse-mapping lifecycle succeeded!")
        print(f"⚡ Total Data Layer Latency: {total_latency:.3f} ms")
    else:
        print("❌ INTEGRATION TEST FAILED: Retrieved data does not match original data.")

if __name__ == "__main__":
    run_integration_test()