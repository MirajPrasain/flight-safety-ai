# backend/main.py
from fastapi import FastAPI, HTTPException
from database import flight_data_collection
from models import FlightData
from pymongo.errors import PyMongoError
from bson import ObjectId
from langchain_utils import emergency_advisor_chain, risk_explanation_chain, copilot_chat_chain, format_flight_data_for_llm
from typing import Dict, Any
from datetime import datetime

from search_utils import search_similar_flights 

app = FastAPI()

#data =  {"_id" : ObjectId("64f5d0a6e234f1463be9ab12") }
# Helper to convert ObjectId to str for JSON serialization
def serialize_object_id(data):
    if isinstance(data, dict):

        if "_id" in data and isinstance(data["_id"], ObjectId):
            data["_id"] = str(data["_id"])
            # {"_id": ObjectId("64f5...")} → {"_id": "64f5..."}

        #for nested dictionaries
        for key, value in data.items():
            data[key] = serialize_object_id(value)

    #for dictionaries inside a list
    elif isinstance(data, list):
        data = [serialize_object_id(item) for item in data]
    return data


#Routes with End Points. 
@app.get("/")
async def root():
    return {"message": "Welcome to the AI Aircraft Crash Prevention API!"}


@app.post("/flight_data/")
#flight_data is a json received from the simulated front end, that is validated/converted to a pydantic object of schema FlightData
async def create_flight_data(flight_data: FlightData):
    try:
        #convert the Pydantic object to python dictionary, to make some changes in the data. 
        flight_data_dict = flight_data.model_dump()

        # Ensure timestamp is stored as datetime object for MongoDB
        if isinstance(flight_data_dict.get("timestamp"), str):
            flight_data_dict["timestamp"] = datetime.fromisoformat(flight_data_dict["timestamp"].replace('Z', '+00:00'))


        #flight_data_collection is the database accessed in database.py. Here, we are inserting the flight data dictionary directly into the MongoDB collection. 
        result = await flight_data_collection.insert_one(flight_data_dict)

        # result.inserted_id is the ObjectId MongoDB generates.
        return {"id": str(result.inserted_id), "message": "Flight data recorded successfully"}
    
    except PyMongoError as e: 
        #If insertion fails due to DB connection, schema mismatch, etc., raise a 500 Internal Server Error.
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    
    except Exception as e:
        # Catches other issues like datetime parsing or missing fields.
        raise HTTPException(status_code=400, detail=f"Invalid data: {e}")



@app.get("/flight_data/{flight_id}")
async def get_flight_data_by_flight_id(flight_id: str):
    cursor = flight_data_collection.find({"flight_id": flight_id}).sort("timestamp", -1).limit(1) # Get only the latest data point

    data_list = []
    async for doc in cursor:
        data_list.append(serialize_object_id(doc))

    if not data_list:
        raise HTTPException(status_code=404, detail="Flight data not found")

    return data_list[0] # Return just the latest data point


# NEW ENDPOINT: Emergency Advisor Chain
@app.post("/advise_pilot/")
async def advise_pilot(flight_data: FlightData):
    """
    Provides real-time emergency advice to the pilot based on current flight data.
    """
    try:
        # Convert Pydantic model to a dictionary for LLM input
        flight_data_dict = flight_data.model_dump()

        # Format the nested data for the LLM prompt
        formatted_input = format_flight_data_for_llm(flight_data_dict)

        # Invoke the LangChain emergency advisor chain
        advice = await emergency_advisor_chain.ainvoke(formatted_input)

        return {"advice": advice}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating advice: {e}")
    

# NEW ENDPOINT: Risk Explanation Chain
@app.post("/explain_risk/")
async def explain_risk(flight_data: FlightData, anomaly_description: str):
    """
    Explains why a flight situation is unsafe, given flight data and a detected anomaly.
    """
    try:
        flight_data_dict = flight_data.model_dump()
        formatted_input = format_flight_data_for_llm(flight_data_dict)
        # Format function converts the dictionary to flat, having single key value pairs. This is needed because the LangChain prompt expects a flat input, not deeply nested structures.


        # Add the anomaly description to the input for the risk explanation chain
        formatted_input["anomaly_description"] = anomaly_description


        explanation = await risk_explanation_chain.ainvoke(formatted_input)

        return {"explanation": explanation}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error explaining risk: {e}")

# NEW ENDPOINT: Pilot Copilot Chat (Basic)
@app.post("/copilot_chat/")
async def copilot_chat(question: str):
    """
    Allows pilots to ask natural language questions to an AI copilot.
    """
    try:
        answer = await copilot_chat_chain.ainvoke({"question": question})
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in copilot chat: {e}")
    

# LESSON 6: Search Similar Crashes
@app.get("/similar_crashes/")
async def similar_crashes(query: str, top_k: int = 3):
    try:
        results = await search_similar_flights(query_summary=query, top_k=top_k)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error finding similar crashes: {e}")
