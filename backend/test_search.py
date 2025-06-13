import asyncio
from search_utils import search_similar_flights

async def test_search():
    test_query = "The aircraft descended below glide slope and terrain warnings were ignored."
    print(f"🔍 Searching for: {test_query}")
    print("=" * 80)
    
    results = await search_similar_flights(test_query)
    
    print(f"Found {len(results)} similar flights:")
    print("=" * 80)
    
    for i, r in enumerate(results, 1):
        print(f"{i}. ✈️ {r['flight_id']} — Similarity: {r['similarity']:.4f}")
        print(f"   Summary: {r['summary']}")
        print()

if __name__ == "__main__":
    asyncio.run(test_search()) 