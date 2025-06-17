import httpx
import asyncio
import json
from datetime import datetime
import traceback

# --- Configuration ---
# Your FastAPI backend URL. Using 127.0.0.1 is often more explicit than localhost.
API_BASE_URL = "http://127.0.0.1:8000"

# --- Mock Flight Data ---
# This data will be sent to your FastAPI backend
mock_flight_data = {
  "flight_id": "CLI_FLIGHT_001",
  "aircraft_type": "Boeing 737",
  "pilot_id": "CLI_PILOT_A",
  "location": {
    "latitude": 34.0522,
    "longitude": -118.2437,
    "altitude_ft": 2500
  },
  "speed": {
    "airspeed_knots": 180,
    "vertical_speed_fpm": -1800 # Rapid descent scenario
  },
  "engine": {
    "engine_1_rpm": 95,
    "engine_2_rpm": 95
  },
  "aircraft_systems": {
    "landing_gear_status": "UP",
    "flap_setting": "FLAPS_0",
    "autopilot_engaged": False,
    "warnings": ["TERRAIN_PULL_UP", "GLIDE_SLOPE_WARNING"] # Active warnings
  },
  "environment": {
    "wind_speed_knots": 15,
    "wind_direction_deg": 270,
    "temperature_c": 20,
    "visibility_miles": 3,
    "precipitation": "LIGHT_RAIN",
    "terrain_proximity_ft": 300 # Close to ground
  },
  "pilot_actions": {
    "throttle_percent": 40,
    "pitch_deg": -5,
    "roll_deg": 0,
    "yaw_deg": 0
  }
}

# **dict = spreads all key-value pairs of a dictionary into another dictionary.
# It's like cloning with selective edits.
# Common for testing, mocking, or modifying configs.

# Another mock data for risk explanation
mock_risky_flight_data = {
    **mock_flight_data, #It copies all the key-value pairs from the dictionary mock_flight_data.

    #"Start with all the fields from mock_flight_data, and then override/add specific ones below."

    #Common Risk factors are location, speed, systems and environment.
    "flight_id": "CLI_FLIGHT_002_RISK",
    "location": {
        **mock_flight_data["location"],
        "altitude_ft": 100 # Extremely low altitude
    },
    "speed": {
        **mock_flight_data["speed"],
        "vertical_speed_fpm": -2500 # Even faster descent
    },
    "aircraft_systems": {
        **mock_flight_data["aircraft_systems"],
        "warnings": ["STALL_WARNING", "TERRAIN_PULL_UP", "LOW_AIRSPEED_FLAPS_UP"]
    },
    "environment": {
        **mock_flight_data["environment"],
        "terrain_proximity_ft": 10 # Dangerously close to terrain
    }
}


# This function simulates a client (frontend or CLI script) talking to your backend API.
async def run_demo():
  # Client with global follow_redirects=True.
  # This makes the client automatically handle HTTP 3xx redirects.
  # Added timeout=60.0 to handle LLM response times
  async with httpx.AsyncClient(follow_redirects=True, timeout=60.0) as client:

    print("--- AI Aircraft Crash Prevention CLI Demo ---")
    print(f"Connecting to the backend at: {API_BASE_URL} \n") # Corrected typo: "backed" to "backend"

     # --- Demo 1: Get Emergency Advice ---
    print("## Demo 1: Getting Emergency Advice ##")
    print("\n--- Incoming Flight Data (to AI Advisor) ---")

    data_to_send_advice = mock_flight_data.copy()
    data_to_send_advice["timestamp"] = datetime.utcnow().isoformat() + "Z"

    print(json.dumps(data_to_send_advice, indent = 2))

    try:
        print("\n--- Sending Request For Advice ---") # Corrected typo: added space
        response = await client.post( f"{API_BASE_URL}/advise_pilot/", json = data_to_send_advice )
        response.raise_for_status()

        # Backend returns 'advice' key
        advice = response.json().get("advice", "No Advice Received")
        print("\n--- AI Emergency Advisor Response ---")
        print(advice)
        print("-" * 50 + "\n")

    except httpx.HTTPStatusError as e:
        print(f"\nError from API (Status {e.response.status_code}): {e.response.text}")
        traceback.print_exc()
    except httpx.RequestError as e:
        print(f"\nNetwork error or API not reachable: {e}")
        traceback.print_exc()
    except Exception as e: # Catch any other unexpected errors
        print(f"\nAn unexpected error occurred during Demo 1: {e}")
        traceback.print_exc()


     # --- Demo 2: Get Risk Explanation ---
    print("## Demo 2: Getting Risk Explanation ##")
    print("\n--- Incoming Risky Flight Data (to AI Analyst) ---")
    data_to_send_risk = mock_risky_flight_data.copy()
    data_to_send_risk["timestamp"] = datetime.utcnow().isoformat() + "Z"
    print(json.dumps(data_to_send_risk, indent=2))

    anomaly_desc = "Rapid descent with multiple critical warnings near ground at very low altitude."
    print(f"\n--- Detected Anomaly: {anomaly_desc} ---")

    try:
        print("\n--- Sending request for risk explanation... ---")
        # CORRECTED: Use proper query parameter handling with httpx
        response = await client.post(
            f"{API_BASE_URL}/explain_risk/",
            params={"anomaly_description": anomaly_desc},  # Use params for query parameters
            json=data_to_send_risk
        )
        response.raise_for_status()
        # Backend returns 'explanation' key
        explanation = response.json().get("explanation", "No explanation received.")
        print("\n--- AI Risk Explanation Response ---")
        print(explanation)
        print("-" * 50 + "\n")
    except httpx.HTTPStatusError as e:
        print(f"\nError from API (Status {e.response.status_code}): {e.response.text}")
        traceback.print_exc()
    except httpx.RequestError as e:
        print(f"\nNetwork error or API not reachable: {e}")
        traceback.print_exc()
    except Exception as e:
        print(f"\nAn unexpected error occurred during Demo 2: {e}")
        traceback.print_exc()


    # --- Demo 3: Pilot Co-pilot Chat ---
    print("## Demo 3: Pilot Co-pilot Chat ##")
    chat_query = "How do i make sure i am in the right angle with respect to this turbulence?"
    print(f"\n--- Pilot asks: '{chat_query}' ---")

    try:
        print("\n--- Sending Chat Question ---")

        # CORRECTED: Pass query parameters using the 'params' argument
        # This handles URL encoding automatically and is the idiomatic httpx way.
        response = await client.post(
            f"{API_BASE_URL}/copilot_chat/", # Trailing slash added for consistency with FastAPI defaults
            params={"question": chat_query} # Pass a dictionary for query parameters
        )

        response.raise_for_status()

        # CORRECTED: Backend returns 'answer', not 'copilot_answer'
        copilot_answer = response.json().get("answer", "Query Dismissed")

        print("\n--- AI Chat Response ---") # Corrected formatting
        print(copilot_answer)
        print("-" * 50 + "\n")

    except httpx.HTTPStatusError as e:
        print(f"\nError from API (Status {e.response.status_code}): {e.response.text}")
        traceback.print_exc()
    except httpx.RequestError as e:
        print(f"\nNetwork error or API not reachable: {e}")
        traceback.print_exc()
    except Exception as e:
        print(f"\nAn unexpected error occurred during Demo 3: {e}")
        traceback.print_exc()


    print("--- Testing backend connectivity ---")
    try:
        response = await client.get(f"{API_BASE_URL}/docs")
        print("✅ Backend is reachable. Status:", response.status_code)
        print("✅ Response content preview:")
        print(response.text[:200])  # Show first 200 characters of the docs page
    except httpx.RequestError as e:
        print("❌ Cannot reach backend:")
        print(type(e), e)
        traceback.print_exc()
        return


# --- Run the demo ---
if __name__ == "__main__":
    asyncio.run(run_demo())