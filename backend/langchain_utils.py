# backend/langchain_utils.py
import os
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
# Option 1: Use Ollama for local LLM (recommended for hackathon simplicity without API keys)
from langchain_community.llms import Ollama

# Initialize LLM
# If using Ollama:
# Ensure Ollama server is running and a model like `llama3` is pulled:
#   1. Download Ollama from ollama.com
#   2. Run `ollama serve` in your terminal
#   3. Run `ollama pull llama3` (or mistral, or gemma)
llm = Ollama(model="llama3")  # Or "mistral", "gemma"

# 1. Emergency Advisor Chain
emergency_advisor_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an expert AI flight advisor for pilots, providing concise, immediate, and actionable advice during critical flight situations. Your goal is to prevent crashes by recommending precise pilot actions based on real-time aircraft data.
    Focus on specific, numerical instructions when possible (e.g., "Reduce throttle to 70%", "Maintain pitch +5 degrees").
    If a warning is present, specifically address it.
    Output only the actionable advice, no conversational filler."""),
    ("user", """Given the following real-time flight data, what should the pilot do?

    Aircraft Type: {aircraft_type}
    Flight ID: {flight_id}
    Timestamp: {timestamp}
    Location: Altitude {altitude_ft} ft, Latitude {latitude}, Longitude {longitude}
    Speed: Airspeed {airspeed_knots} knots, Vertical Speed {vertical_speed_fpm} fpm
    Engine: Engine 1 RPM {engine_1_rpm}%, Engine 2 RPM {engine_2_rpm}%
    Systems: Landing Gear {landing_gear_status}, Flaps {flap_setting}, Autopilot {autopilot_engaged}
    Warnings: {warnings}
    Environment: Wind {wind_speed_knots} knots from {wind_direction_deg} deg, Temperature {temperature_c}°C, Visibility {visibility_miles} miles, Precipitation {precipitation}, Terrain Proximity {terrain_proximity_ft} ft
    Pilot Actions (Current): Throttle {throttle_percent}%, Pitch {pitch_deg} deg, Roll {roll_deg} deg, Yaw {yaw_deg} deg

    Provide only the direct pilot advice, no preamble.""")
])

emergency_advisor_chain = emergency_advisor_prompt | llm | StrOutputParser()

# 2. Risk Explanation Chain
risk_explanation_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an expert AI aviation safety analyst. Your task is to explain clearly and concisely why a given flight situation is unsafe or has high risk. Refer to standard aviation safety principles, common crash causes, and the provided data.
    Explain the risk in plain aviation English, avoiding jargon where possible.
    Focus on specific data points that contribute to the unsafe condition."""),
    ("user", """Explain why this flight situation is considered unsafe based on the following data and any detected anomalies:

    Aircraft Type: {aircraft_type}
    Flight ID: {flight_id}
    Timestamp: {timestamp}
    Location: Altitude {altitude_ft} ft, Latitude {latitude}, Longitude {longitude}
    Speed: Airspeed {airspeed_knots} knots, Vertical Speed {vertical_speed_fpm} fpm
    Engine: Engine 1 RPM {engine_1_rpm}%, Engine 2 RPM {engine_2_rpm}%
    Systems: Landing Gear {landing_gear_status}, Flaps {flap_setting}, Autopilot {autopilot_engaged}
    Warnings: {warnings}
    Environment: Wind {wind_speed_knots} knots from {wind_direction_deg} deg, Temperature {temperature_c}°C, Visibility {visibility_miles} miles, Precipitation {precipitation}, Terrain Proximity {terrain_proximity_ft} ft

    Anomaly Detected: {anomaly_description}

    Provide the explanation clearly and concisely.""")
])

risk_explanation_chain = risk_explanation_prompt | llm | StrOutputParser()

# 3. Pilot Copilot Chat Agent (Basic setup for later)
copilot_chat_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an AI co-pilot, providing helpful, factual, and concise answers to pilot questions in plain aviation English. If you don't know, state that you don't know."),
    ("user", "{question}")
])

copilot_chat_chain = copilot_chat_prompt | llm | StrOutputParser()

# Helper function to prepare flight data for LLM
def format_flight_data_for_llm(flight_data_dict: dict) -> dict:
    """
    Formats the flight data dictionary into a flat dictionary suitable for LLM prompts.
    Handles missing keys by assigning "N/A" or "None" as appropriate.
    """
    # Extract nested dictionaries once for efficiency
    location = flight_data_dict.get("location", {})
    speed = flight_data_dict.get("speed", {})
    engine = flight_data_dict.get("engine", {})
    aircraft_systems = flight_data_dict.get("aircraft_systems", {})
    environment = flight_data_dict.get("environment", {})
    pilot_actions = flight_data_dict.get("pilot_actions", {})

    # Flatten the data
    formatted_data = {
        "aircraft_type": flight_data_dict.get("aircraft_type", "N/A"),
        "flight_id": flight_data_dict.get("flight_id", "N/A"),
        "timestamp": flight_data_dict.get("timestamp", "N/A"),
        "altitude_ft": location.get("altitude_ft", "N/A"),
        "latitude": location.get("latitude", "N/A"),
        "longitude": location.get("longitude", "N/A"),
        "airspeed_knots": speed.get("airspeed_knots", "N/A"),
        "vertical_speed_fpm": speed.get("vertical_speed_fpm", "N/A"),
        "engine_1_rpm": engine.get("engine_1_rpm", "N/A"),
        "engine_2_rpm": engine.get("engine_2_rpm", "N/A"),
        "landing_gear_status": aircraft_systems.get("landing_gear_status", "N/A"),
        "flap_setting": aircraft_systems.get("flap_setting", "N/A"),
        "autopilot_engaged": aircraft_systems.get("autopilot_engaged", "N/A"),
        "warnings": ", ".join(aircraft_systems.get("warnings", [])) if aircraft_systems.get("warnings") else "None",
        "wind_speed_knots": environment.get("wind_speed_knots", "N/A"),
        "wind_direction_deg": environment.get("wind_direction_deg", "N/A"),
        "temperature_c": environment.get("temperature_c", "N/A"),
        "visibility_miles": environment.get("visibility_miles", "N/A"),
        "precipitation": environment.get("precipitation", "N/A"),
        "terrain_proximity_ft": environment.get("terrain_proximity_ft", "N/A"),
        "throttle_percent": pilot_actions.get("throttle_percent", "N/A"),
        "pitch_deg": pilot_actions.get("pitch_deg", "N/A"),
        "roll_deg": pilot_actions.get("roll_deg", "N/A"),
        "yaw_deg": pilot_actions.get("yaw_deg", "N/A")
    }
    return formatted_data