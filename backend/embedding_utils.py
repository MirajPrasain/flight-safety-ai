from sentence_transformers import SentenceTransformer 
from database import db 
from pymongo.errors import PyMongoError 


#Hugging Face model for embeddings 
model = SentenceTransformer("all-MiniLM-L6-v2")
flight_vector_collection = db["flight_vectors"]


async def embed_and_store_flight_summary(flight_id: str, summary: str):
    """
    Converts a crash flight summary into a vector and stores it in MongoDB.
    """
    try:
        print(f"🔍 Embedding summary for {flight_id}...")

        #Generate the embedding 
        vector = model.encode(summary).tolist() 


        #Create the document 
        document = { 
            "flight_id" : flight_id, 
            "summary" : summary, 
            "vector" : vector 
        }

        await flight_vector_collection.insert_one(document) 
        # MongoDB is schema-less and auto-creates collections when you first insert a document into them. If "flight_vectors" doesn't exist yet, MongoDB will automatically create it on this line.

    
    except PyMongoError as e:
        print(f"❌ MongoDB error while inserting vector: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")





#Most important Line: 

# vector = model.encode(summary).tolist()
# 🔍 What it does at runtime:
# Takes a natural language summary (e.g., "The flight crashed due to bad weather").

# Feeds it into a pretrained transformer model (all-MiniLM-L6-v2).
# Converts the text into a 384-dimensional vector — a dense numeric representation of the meaning of that text.
# Converts the vector (NumPy array) to a Python list, so it can be stored in MongoDB (MongoDB doesn't support NumPy arrays natively).


# .encode() returns a NumPy array.
# .tolist() turns it into a native Python list, which is:
# JSON-serializable ✅
# MongoDB-safe ✅
# Easy to store and transfer


#What does the vector (array -> list) look like after .encode runs? 
# [
#   -0.0198, 0.4032, 0.1983, ..., 0.1029
# ]  # (length = 384)
# You can't interpret each number directly, but together they represent the position of the sentence in semantic space.
# Similar sentences → similar vectors → close in vector space.


#Key MongoDB operation 
# 🧠 What is insert_one()?
# It's a method from MongoDB's async driver (motor).
# Inserts exactly one document into the collection.
# Returns an InsertOneResult object containing metadata like the new _id.

