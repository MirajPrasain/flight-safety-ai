import asyncio
from database import db

async def check_database():
    try:
        # Get all documents from the flight_vectors collection (not flight_summaries)
        documents = await db.flight_vectors.find().to_list(length=10)
        
        print(f"Found {len(documents)} documents in database:")
        for doc in documents:
            print(f"- {doc['flight_id']}")
            if 'vector' in doc:
                print(f"  Vector length: {len(doc['vector'])}")
            print()
            
    except Exception as e:
        print(f"Error checking database: {e}")

if __name__ == "__main__":
    asyncio.run(check_database()) 