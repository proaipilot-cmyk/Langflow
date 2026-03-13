"""
Comprehensive connectivity test for all services
Tests: MongoDB, Mistral AI, OpenRouter
"""

import os
import sys
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

# Color codes for output
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

def print_warning(message):
    print(f"{YELLOW}⚠ {message}{RESET}")

def print_info(message):
    print(f"{BLUE}ℹ {message}{RESET}")

# ============================================================================
# 1. TEST ENVIRONMENT VARIABLES
# ============================================================================
def test_environment_variables():
    print_section("1. CHECKING ENVIRONMENT VARIABLES")

    required_vars = {
        'MONGO_URI': 'MongoDB Connection String',
        'MISTRAL_API_KEY': 'Mistral AI API Key',
        'OPENROUTER_API_KEY': 'OpenRouter API Key'
    }

    all_valid = True

    for var_name, description in required_vars.items():
        value = os.getenv(var_name)
        if value:
            masked_value = value[:10] + "..." + value[-10:] if len(value) > 20 else "***"
            print_success(f"{description} ({var_name}): {masked_value}")
        else:
            print_error(f"{description} ({var_name}): NOT SET")
            all_valid = False

    return all_valid

# ============================================================================
# 2. TEST MONGODB CONNECTION
# ============================================================================
def test_mongodb_connection():
    print_section("2. TESTING MONGODB CONNECTION")

    try:
        from pymongo import MongoClient
        from pymongo.errors import ServerSelectionTimeoutError, ConnectionFailure

        mongo_uri = os.getenv('MONGO_URI')
        if not mongo_uri:
            print_error("MONGO_URI not set")
            return False

        print_info("Connecting to MongoDB Atlas...")
        client = MongoClient(
            mongo_uri,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=10000,
            retryWrites=True,
        )

        print_info("Sending ping command...")
        client.admin.command('ping')
        print_success("MongoDB connection successful!")

        db = client['ResumeCollection']
        collection = db['ResumeCollection']

        doc_count = collection.count_documents({})
        print_success(f"Database 'ResumeCollection' accessible")
        print_info(f"Collection 'ResumeCollection' has {doc_count} documents")

        # Regular indexes (only shows _id and any custom indexes — NOT Atlas Search indexes)
        indexes = collection.list_indexes()
        index_names = [idx['name'] for idx in indexes]
        print_info(f"Regular indexes: {', '.join(index_names)}")

        # Atlas Vector Search indexes require list_search_indexes() — a separate API
        print_info("Checking Atlas Search indexes...")
        search_indexes = list(collection.list_search_indexes())

        if search_indexes:
            for idx in search_indexes:
                status = idx.get('status', 'UNKNOWN')
                idx_type = idx.get('type', 'unknown')
                print_success(f"Search index found: '{idx['name']}' | type: {idx_type} | status: {status}")
        else:
            print_warning("No Atlas Search indexes found on this collection.")

        vector_index_names = [idx['name'] for idx in search_indexes]
        if 'Resume_Vector' in vector_index_names:
            print_success("Vector index 'Resume_Vector' confirmed and ready!")
        else:
            print_warning("Vector index 'Resume_Vector' NOT found in Atlas Search indexes.")
            print_warning("Create it in MongoDB Atlas under: Atlas Search > Create Search Index > Vector Search")

        client.close()
        return True

    except ServerSelectionTimeoutError as e:
        print_error(f"MongoDB connection timeout: {str(e)}")
        print_warning("Check: Network connectivity, IP whitelist in MongoDB Atlas, MONGO_URI validity")
        return False
    except ConnectionFailure as e:
        print_error(f"MongoDB connection failed: {str(e)}")
        return False
    except Exception as e:
        print_error(f"MongoDB test error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

# ============================================================================
# 3. TEST MISTRAL AI EMBEDDINGS
# ============================================================================
def test_mistral_embeddings():
    print_section("3. TESTING MISTRAL AI EMBEDDINGS")

    try:
        from langchain_mistralai import MistralAIEmbeddings

        api_key = os.getenv('MISTRAL_API_KEY')
        if not api_key:
            print_error("MISTRAL_API_KEY not set")
            return False

        print_info("Initializing Mistral embeddings...")
        embeddings = MistralAIEmbeddings(
            model="mistral-embed",
            api_key=api_key
        )

        print_info("Generating test embedding for: 'Python developer with 5 years experience'")
        test_embedding = embeddings.embed_query("Python developer with 5 years experience")

        print_success("Mistral embeddings working!")
        print_info(f"Embedding dimension: {len(test_embedding)}")
        print_info(f"Sample values (first 5): {test_embedding[:5]}")

        return True

    except Exception as e:
        print_error(f"Mistral AI test error: {str(e)}")
        print_warning("Check: API key validity, Rate limits, Mistral API status")
        import traceback
        traceback.print_exc()
        return False

# ============================================================================
# 4. TEST OPENROUTER API
# ============================================================================
def test_openrouter_api():
    print_section("4. TESTING OPENROUTER API")

    try:
        from langchain_openai import ChatOpenAI

        api_key = os.getenv('OPENROUTER_API_KEY')
        if not api_key:
            print_error("OPENROUTER_API_KEY not set")
            return False

        print_info("Initializing OpenRouter LLM...")
        llm = ChatOpenAI(
            model="meta-llama/llama-3-8b-instruct",
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key
        )

        print_info("Sending test prompt: 'What is your name?'")
        response = llm.invoke("What is your name?")

        print_success("OpenRouter API working!")
        print_info(f"Response: {response.content[:100]}...")

        return True

    except Exception as e:
        print_error(f"OpenRouter API test error: {str(e)}")
        print_warning("Check: API key validity, Rate limits, API endpoint status")
        print_warning("Also check: openrouter.ai/settings/privacy — enable third-party providers for free models")
        import traceback
        traceback.print_exc()
        return False

# ============================================================================
# 5. TEST FULL VECTOR SEARCH INTEGRATION
# ============================================================================
def test_vector_search_integration():
    print_section("5. TESTING VECTOR SEARCH INTEGRATION")

    try:
        from langchain_mistralai import MistralAIEmbeddings
        from langchain_mongodb import MongoDBAtlasVectorSearch
        from pymongo import MongoClient

        print_info("Setting up MongoDB connection...")
        mongo_uri = os.getenv('MONGO_URI')
        client = MongoClient(
            mongo_uri,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=10000,
        )

        db = client['ResumeCollection']
        collection = db['ResumeCollection']

        print_info("Initializing embeddings...")
        api_key = os.getenv('MISTRAL_API_KEY')
        embeddings = MistralAIEmbeddings(
            model="mistral-embed",
            api_key=api_key
        )

        print_info("Initializing vector store...")
        vector_store = MongoDBAtlasVectorSearch(
            collection=collection,
            embedding=embeddings,
            index_name="Resume_Vector"
        )

        print_info("Testing vector search with query: 'Python developer'")
        retriever = vector_store.as_retriever(search_kwargs={"k": 3})
        results = retriever.invoke("Python developer")

        print_success("Vector search working!")
        print_info(f"Found {len(results)} results")

        if len(results) > 0:
            print_info(f"Top result preview: {results[0].page_content[:100]}...")
        else:
            print_warning("No results found. Check if documents are indexed in MongoDB.")

        client.close()
        return True

    except Exception as e:
        print_error(f"Vector search integration test error: {str(e)}")
        print_warning("Check: Vector index exists in MongoDB, Documents are indexed")
        import traceback
        traceback.print_exc()
        return False

# ============================================================================
# MAIN TEST RUNNER
# ============================================================================
def main():
    print(f"\n{BLUE}{'='*60}")
    print("RESUME ANALYZER - CONNECTIVITY DIAGNOSTIC TEST")
    print(f"{'='*60}{RESET}\n")

    results = {}

    results['env_vars'] = test_environment_variables()
    results['mongodb'] = test_mongodb_connection()
    results['mistral'] = test_mistral_embeddings()
    results['openrouter'] = test_openrouter_api()
    results['vector_search'] = test_vector_search_integration()

    print_section("TEST SUMMARY")

    test_names = {
        'env_vars': 'Environment Variables',
        'mongodb': 'MongoDB Connection',
        'mistral': 'Mistral AI Embeddings',
        'openrouter': 'OpenRouter API',
        'vector_search': 'Vector Search Integration'
    }

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for key, name in test_names.items():
        if results[key]:
            print_success(f"{name}: PASSED")
        else:
            print_error(f"{name}: FAILED")

    print(f"\n{BLUE}Overall: {passed}/{total} tests passed{RESET}\n")

    if passed == total:
        print_success("All connectivity tests passed! ✓")
        return 0
    else:
        print_error("Some tests failed. Review errors above.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)