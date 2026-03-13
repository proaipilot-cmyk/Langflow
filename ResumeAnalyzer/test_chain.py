"""
Integration test for the RAG chain
Tests the complete pipeline: embeddings → retrieval → generation
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Color codes
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_section(title):
    print(f"\n{BLUE}{'='*60}")
    print(f"{title}")
    print(f"{'='*60}{RESET}\n")

def print_success(message):
    print(f"{GREEN}✓ {message}{RESET}")

def print_error(message):
    print(f"{RED}✗ {message}{RESET}")

def print_info(message):
    print(f"{BLUE}ℹ {message}{RESET}")

load_dotenv()

print_section("RAG CHAIN INTEGRATION TEST")

# Test 1: Build the chain
print_info("Test 1: Building RAG chain...")
try:
    from backend.rag_pipeline import build_chain
    rag_chain = build_chain()
    print_success("RAG chain built successfully")
except Exception as e:
    print_error(f"Failed to build RAG chain: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 2: Query the chain
print_info("Test 2: Querying RAG chain...")
test_queries = [
    "Find candidates with Python experience",
    "Who has experience with machine learning?",
    "List developers with more than 5 years experience"
]

successful_queries = 0
failed_queries = 0

for query in test_queries:
    try:
        print_info(f"Query: {query}")
        response = rag_chain.invoke({"input": query})
        print_success(f"Response: {response[:100]}...")
        successful_queries += 1
    except Exception as e:
        print_error(f"Query failed: {str(e)}")
        failed_queries += 1

# Summary
print_section("TEST SUMMARY")
print(f"✓ Successful queries: {successful_queries}/{len(test_queries)}")
print(f"✗ Failed queries: {failed_queries}/{len(test_queries)}")

if successful_queries == len(test_queries):
    print_success("All tests PASSED!")
    sys.exit(0)
else:
    print_error("Some tests FAILED")
    sys.exit(1)
