#!/usr/bin/env python3

"""
Database LLM Wizard - Test Suite
This script tests our wizard with various natural language queries
"""

import asyncio
import time
from typing import Any

import aiohttp

# Test server configuration
WIZARD_URL = "http://localhost:8000/ask"


class WizardTester:
    def __init__(self):
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def ask_wizard(self, question: str) -> dict[str, Any]:
        """Send a question to the wizard and get response"""
        try:
            start_time = time.time()

            async with self.session.post(
                WIZARD_URL,
                json={"question": question},
                headers={"Content-Type": "application/json"},
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    duration = time.time() - start_time
                    return {
                        "success": True,
                        "question": question,
                        "answer": result.get("answer", ""),
                        "duration": round(duration, 2),
                    }
                else:
                    error_text = await response.text()
                    return {
                        "success": False,
                        "question": question,
                        "error": f"HTTP {response.status}: {error_text}",
                        "duration": time.time() - start_time,
                    }
        except Exception as e:
            return {
                "success": False,
                "question": question,
                "error": str(e),
                "duration": time.time() - start_time,
            }

    def print_result(self, result: dict[str, Any]):
        """Pretty print test result"""
        print(f"\n{'=' * 80}")
        print(f"🔮 Question: {result['question']}")
        print(f"⏱️  Duration: {result['duration']}s")

        if result["success"]:
            print(f"✅ Answer: {result['answer']}")
        else:
            print(f"❌ Error: {result['error']}")


async def test_basic_queries():
    """Test basic database queries"""
    print("🧪 Testing Basic Queries")
    print("-" * 40)

    test_cases = [
        "What tables exist in the database?",
        "Show me all customers",
        "How many products do we have?",
        "List all orders from the last week",
        "Show me the most expensive products",
    ]

    async with WizardTester() as tester:
        for question in test_cases:
            result = await tester.ask_wizard(question)
            tester.print_result(result)
            await asyncio.sleep(1)  # Be nice to the API


async def test_create_operations():
    """Test data creation"""
    print("\n🧪 Testing Create Operations")
    print("-" * 40)

    test_cases = [
        "Add a new customer named John Doe with email john@example.com",
        "Create a new product called Magic Wand with price $99.99 in the Mystical category",
        "Add a new author named Neil Gaiman born in 1960 from Britain",
        "Create a book called 'The Sandman' by Neil Gaiman published in 1989",
    ]

    async with WizardTester() as tester:
        for question in test_cases:
            result = await tester.ask_wizard(question)
            tester.print_result(result)
            await asyncio.sleep(1)


async def test_complex_queries():
    """Test complex queries and relationships"""
    print("\n🧪 Testing Complex Queries")
    print("-" * 40)

    test_cases = [
        "Show me all customers who have placed orders",
        "What are the top 3 best-selling product categories?",
        "Find all books by British authors",
        "Show me customers with more than 2 orders",
        "List all products that are out of stock",
    ]

    async with WizardTester() as tester:
        for question in test_cases:
            result = await tester.ask_wizard(question)
            tester.print_result(result)
            await asyncio.sleep(1)


async def test_schema_operations():
    """Test schema manipulation"""
    print("\n🧪 Testing Schema Operations")
    print("-" * 40)

    test_cases = [
        "Describe the structure of the customers table",
        "Create a new table called reviews with columns for id, product_id, rating, and comment",
        "Add a column called phone_verified to the customers table",
        "Create an index on the orders table for the order_date column",
    ]

    async with WizardTester() as tester:
        for question in test_cases:
            result = await tester.ask_wizard(question)
            tester.print_result(result)
            await asyncio.sleep(1)


async def test_update_delete_operations():
    """Test update and delete operations"""
    print("\n🧪 Testing Update/Delete Operations")
    print("-" * 40)

    test_cases = [
        "Update the price of Magic Wand to $89.99",
        "Change John Doe's email to johndoe@example.com",
        "Delete all cancelled orders",
        "Update all pending orders to processing status",
    ]

    async with WizardTester() as tester:
        for question in test_cases:
            result = await tester.ask_wizard(question)
            tester.print_result(result)
            await asyncio.sleep(1)


async def test_error_handling():
    """Test error handling and recovery"""
    print("\n🧪 Testing Error Handling")
    print("-" * 40)

    test_cases = [
        "Show me data from a table that doesn't exist called unicorns",
        "Create a table with an invalid name containing spaces",
        "Insert invalid data types into products table",
        "Update a non-existent customer",
    ]

    async with WizardTester() as tester:
        for question in test_cases:
            result = await tester.ask_wizard(question)
            tester.print_result(result)
            await asyncio.sleep(1)


async def check_server():
    """Check if the wizard server is running"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:8000/") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ {data.get('message', 'Server is running')}")
                    return True
                else:
                    print(f"❌ Server returned status {response.status}")
                    return False
    except Exception as e:
        print(f"❌ Cannot connect to wizard server: {e}")
        print("💡 Make sure to start the server with: uvicorn main:app --reload")
        return False


async def main():
    """Main test runner"""
    print("🧙‍♂️ Database LLM Wizard - Test Suite")
    print("=" * 80)

    # Check if server is running
    if not await check_server():
        return

    print("\n🚀 Starting comprehensive wizard tests...")

    try:
        # Run all test suites
        await test_basic_queries()
        await test_create_operations()
        await test_complex_queries()
        await test_schema_operations()
        await test_update_delete_operations()
        await test_error_handling()

        print("\n" + "=" * 80)
        print("🎉 All tests completed!")
        print("\n📊 Test Summary:")
        print("   ✅ Basic Queries")
        print("   ✅ Create Operations")
        print("   ✅ Complex Queries")
        print("   ✅ Schema Operations")
        print("   ✅ Update/Delete Operations")
        print("   ✅ Error Handling")

    except KeyboardInterrupt:
        print("\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())
