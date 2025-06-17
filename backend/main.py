# backend/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from database import flight_data_collection
from models import FlightData
from pymongo.errors import PyMongoError
from bson import ObjectId

from langchain_utils import emergency_advisor_chain, risk_explanation_chain, copilot_chat_chain, format_flight_data_for_llm, status_update_chain, get_emergency_advisor_chain_with_validation, get_risk_explanation_chain_with_validation

from typing import Dict, Any
from datetime import datetime

from search_utils import search_similar_flights, store_crash_flight_data
from router_utils import classify_intent, get_flight_specific_chain, get_fallback_message

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
async def advise_pilot(flight_data: FlightData = None, flight_id: str = None):
    """
    Provides real-time emergency advice to the pilot based on current flight data.
    Can work with provided flight data or fetch latest data for a specific flight ID.
    """
    try:
        if flight_data:
            # Use provided flight data
            flight_data_dict = flight_data.model_dump()
        elif flight_id:
            # Fetch latest flight data from MongoDB for the given flight ID
            cursor = flight_data_collection.find({"flight_id": flight_id}).sort("timestamp", -1).limit(1)
            data_list = []
            async for doc in cursor:
                data_list.append(doc)
            
            if not data_list:
                raise HTTPException(status_code=404, detail=f"No flight data found for flight ID: {flight_id}")
            
            flight_data_dict = data_list[0]
        else:
            raise HTTPException(status_code=400, detail="Either flight_data or flight_id must be provided")

        # Format the nested data for the LLM prompt
        formatted_input = format_flight_data_for_llm(flight_data_dict)

        # 🛑 Use KAL801-specific chain with validation if flight_id is KAL801
        flight_id_for_chain = flight_data_dict.get("flight_id", flight_id)
        if flight_id_for_chain == "KAL801":
            # Use KAL801-specific emergency advisor with grounded context
            emergency_chain = get_emergency_advisor_chain_with_validation("KAL801")
            advice = await emergency_chain(formatted_input)
        else:
            # Use standard emergency advisor chain
            advice = await emergency_advisor_chain.ainvoke(formatted_input)

        return {"advice": advice}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating advice: {e}")

# NEW ENDPOINT: Chat Interface for Flight Simulation
@app.post("/chat/status_update/")
async def chat_status_update(request: Dict[str, str]):
    """
    Handles AI Copilot chat interaction for specific flight and message.
    Now includes intent classification and flight-specific chain routing.
    """
    try:
        #these are sent via front end in ChatPage.jsx
        flight_id = request.get("flight_id", "Unknown")
        message = request.get("message", "")

        print(f"Received chat request for flight_id: {flight_id}, message: {message}")

        # Classify the intent of the message
        intent = classify_intent(message)
        print(f"Classified intent: {intent}")

        # Get the appropriate chain based on flight ID and intent
        chain = get_flight_specific_chain(flight_id, intent)

        # Add timeout for Ollama response (15 seconds)
        import asyncio
        try:
            # Pass to the LangChain chain with timeout
            response = await asyncio.wait_for(
                chain.ainvoke({
                    "flight_id": flight_id,
                    "message": message
                }),
                timeout=15.0  # 15 second timeout for faster fallback
            )
            print(f"Generated response for intent '{intent}': {response}")
            return {"advice": response, "flight_id": flight_id, "intent": intent}
            
        except asyncio.TimeoutError:
            print(f"Ollama Gemma response timed out after 15 seconds for intent: {intent}")
            timeout_response = {
                "advice": get_fallback_message(flight_id, intent),
                "flight_id": flight_id,
                "intent": intent
            }
            return timeout_response

    except Exception as e:
        print(f"Error in chat_status_update: {e}")
        
        # Use the new fallback system
        fallback_response = {
            "advice": get_fallback_message(flight_id, "status_update"),
            "flight_id": flight_id if 'flight_id' in locals() else "unknown",
            "intent": "status_update"
        }
        return fallback_response


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

        # 🛑 Use KAL801-specific chain with validation if flight_id is KAL801
        flight_id_for_chain = formatted_input.get("flight_id", "Unknown")
        if flight_id_for_chain == "KAL801":
            # Use KAL801-specific risk explanation with grounded context
            risk_chain = get_risk_explanation_chain_with_validation("KAL801")
            explanation = await risk_chain(formatted_input)
        else:
            # Use standard risk explanation chain
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

# NEW ENDPOINT: Store Crash Flight Data
@app.post("/store_crash_data/")
async def store_crash_data(crash_data: Dict[str, Any]):
    """
    Stores historical crash flight data with vector embedding for similarity search.
    """
    try:
        success = await store_crash_flight_data(crash_data)
        if success:
            return {"message": f"Crash data stored successfully for {crash_data.get('flight_id', 'Unknown')}"}
        else:
            raise HTTPException(status_code=500, detail="Failed to store crash data")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error storing crash data: {e}")

# NEW ENDPOINT: Divert Airport Chat
@app.post("/chat/divert_airport/")
async def chat_divert_airport(request: Dict[str, str]):
    """
    Handles AI Copilot chat interaction specifically for airport diversion scenarios.
    """
    try:
        flight_id = request.get("flight_id", "Unknown")
        message = request.get("message", "")

        print(f"Received divert airport request for flight_id: {flight_id}, message: {message}")

        # Get the divert airport chain
        chain = get_flight_specific_chain(flight_id, "divert_airport")

        # Add timeout for Ollama response
        import asyncio
        try:
            response = await asyncio.wait_for(
                chain.ainvoke({
                    "flight_id": flight_id,
                    "message": message
                }),
                timeout=15.0
            )
            print(f"Generated divert airport response: {response}")
            return {"advice": response, "flight_id": flight_id, "intent": "divert_airport"}
            
        except asyncio.TimeoutError:
            print("Ollama Gemma response timed out for divert airport request")
            timeout_response = {
                "advice": get_fallback_message(flight_id, "divert_airport"),
                "flight_id": flight_id,
                "intent": "divert_airport"
            }
            return timeout_response

    except Exception as e:
        print(f"Error in chat_divert_airport: {e}")
        
        fallback_response = {
            "advice": get_fallback_message(flight_id, "divert_airport"),
            "flight_id": flight_id if 'flight_id' in locals() else "unknown",
            "intent": "divert_airport"
        }
        return fallback_response


# NEW ENDPOINT: System Status Chat
@app.post("/chat/system_status/")
async def chat_system_status(request: Dict[str, str]):
    """
    Handles AI Copilot chat interaction specifically for system status and instrument checks.
    """
    try:
        flight_id = request.get("flight_id", "Unknown")
        message = request.get("message", "")

        print(f"Received system status request for flight_id: {flight_id}, message: {message}")

        # Get the system status chain
        chain = get_flight_specific_chain(flight_id, "system_status")

        # Add timeout for Ollama response
        import asyncio
        try:
            response = await asyncio.wait_for(
                chain.ainvoke({
                    "flight_id": flight_id,
                    "message": message
                }),
                timeout=15.0
            )
            print(f"Generated system status response: {response}")
            return {"advice": response, "flight_id": flight_id, "intent": "system_status"}
            
        except asyncio.TimeoutError:
            print("Ollama Gemma response timed out for system status request")
            timeout_response = {
                "advice": get_fallback_message(flight_id, "system_status"),
                "flight_id": flight_id,
                "intent": "system_status"
            }
            return timeout_response

    except Exception as e:
        print(f"Error in chat_system_status: {e}")
        
        fallback_response = {
            "advice": get_fallback_message(flight_id, "system_status"),
            "flight_id": flight_id if 'flight_id' in locals() else "unknown",
            "intent": "system_status"
        }
        return fallback_response

fallback_messages = {
    "KAL801": (
        "CRITICAL TERRAIN ALERT\n"
        "Flight KAL801 is descending below glide slope near Guam. "
        "Initiate an immediate go-around. Monitor altitude closely and cross-check terrain avoidance systems."
    ),
    "CRASH_KAL801": (
        "HISTORICAL KAL801 REFERENCE\n"
        "This flight pattern matches Korean Air Flight 801 (1997 Guam crash). "
        "Immediate terrain pull-up required. Verify glideslope status and initiate missed approach procedures."
    ),
    "CRASH_THY1951": (
        "STALL ALERT: Faulty altitude reading detected. Add thrust immediately and prepare for go-around! "
        "Cross-check radio altimeters and monitor airspeed closely."
    ),
    "CRASH_AAR214": (
        "LOW SPEED APPROACH WARNING\n"
        "Flight 214 is approaching SFO at dangerously low speed. Check autothrottle status and increase thrust immediately. "
        "Visual approach monitoring required."
    ),
    "CRASH_COLGAN3407": (
        "STALL WARNING: Airspeed monitoring critical! "
        "Flight 3407 pattern matches Colgan Air crash (2009 Buffalo). "
        "Monitor airspeed during approach, maintain sterile cockpit, and be prepared for immediate stall recovery procedures."
    ),
    "CRASH_AF447": (
        "PITOT TUBE WARNING: Unreliable airspeed detected! "
        "Flight 447 pattern matches Air France crash (2009 Atlantic). "
        "Follow unreliable airspeed procedures, maintain pitch and thrust, and be alert for high-altitude stall conditions."
    ),
    "TURKISH1951": (
        "AUTOPILOT MALFUNCTION\n"
        "Flight 1951 shows radio altimeter discrepancies. Disengage autopilot, manually stabilize descent, and confirm altitude using backup instruments."
    ),
    "ASIANA214": (
        "LOW SPEED APPROACH WARNING\n"
        "Flight 214 is approaching SFO at dangerously low speed. Increase thrust and adjust pitch angle immediately. Visual confirmation advised."
    )
}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
