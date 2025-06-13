import numpy as np
from sentence_transformers import SentenceTransformer
from database import db
from pymongo.errors import PyMongoError
from typing import List, Dict


async def search_similar_flights(query_summary: str, top_k: int = 3) -> List[Dict]:
    """
    Finds the top-K most similar flight summaries based on vector similarity.
    
    Args:
        query_summary: Input crash summary string to search for similar flights
        top_k: Optional input - how many most similar results to return (default: 3)
    
    Returns:
        List[Dict]: A list of dictionaries like {flight_id, summary, similarity}
    """
    try:
        # Step 1: Embed the new input summary
        model = SentenceTransformer("all-MiniLM-L6-v2")
        query_vector = model.encode(query_summary)
        
        # Step 2: Fetch all stored flight vectors
        flight_vector_collection = db["flight_vectors"]
        cursor = flight_vector_collection.find({}) #.find method returns a cursor
        #cursor is an object that points to documents outlined by query 
        flights = await cursor.to_list(length=None)

        # Step 3: Compute cosine similarity
        def cosine_similarity(v1, v2):
            # Converts both vectors to NumPy arrays, Uses the formula for dot product which measures how aligned the vectors are
            # Returns a number from -1 to 1, where: 1.0 = identical meaning 0.0 = no relation < 0 = opposite meaning
            v1 = np.array(v1)
            v2 = np.array(v2)
            return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)) #formula for cosine similarity.

        scored_flights = []
        for flight in flights:
            similarity = cosine_similarity(query_vector, flight["vector"]) #calculating cosine similary between any vector and a vector in our flight array 

            scored_flights.append({
                "flight_id": flight["flight_id"],
                "summary": flight["summary"],
                "similarity": similarity
            })

        # Step 4: Sort by similarity (descending) and return top K
        scored_flights.sort(key=lambda x: x["similarity"], reverse=True)
        return scored_flights[:top_k]

    except PyMongoError as e:
        print(f"❌ MongoDB error during search: {e}")
        return []
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return []

#testing search_utils.py to get similarity 

if __name__ == "__main__":
    import asyncio
    test_query = "The aircraft descended below glide slope and terrain warnings were ignored."
    results = asyncio.run(search_similar_flights(test_query))

    for r in results:
        print(f"✈️ {r['flight_id']} — Similarity: {r['similarity']:.4f}")
        print(f"Summary: {r['summary']}\n")
