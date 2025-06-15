# backend/langchain_utils.py
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.llms import Ollama
from langchain_core.output_parsers import StrOutputParser

# Load your local model from Ollama
# Switched from "mistral" to "gemma:2b" for performance optimization in demo environment
llm = Ollama(model="gemma:2b")


mock_flight_status = { 
      "KAL801": {
        "altitude": 3000,
        "speed": 210,
        "gear_status": "Retracted",
        "nearest_runway": "Guam Intl RWY06L - 3 NM ahead",
        "weather": "Clear, wind 10 knots NE",
        "engine_status": "Nominal",
        "glide_slope_status": "Below optimal",
        "terrain_warning": True
    },
    "TURKISH1951": {
        "altitude": 800,
        "gear_status": "Extended",
        "nearest_runway": "Schiphol RWY18R - 1.2 NM",
        "engine_status": "Nominal",
        "radio_altimeter": "Faulty",
        "autopilot_status": "Glide locked"
    },
    # Add more flights..
}
# Simple emergency reasoning prompt
status_update_prompt = ChatPromptTemplate.from_messages([
    ("system", """
You are an AI copilot trained for aviation emergency support. 
Respond to pilot queries with clear, urgent, and structured advice when risks are detected. 

## Flight-Specific Emergency Context:
- **KAL801**: Known terrain proximity issues, descent below glide slope, mountainous approach
- **CRASH_KAL801**: Korean Air Flight 801 (1997) - Controlled flight into terrain on Guam approach due to descent below minimum safe altitude, non-functional glideslope, and poor crew resource management. 229 fatalities, 25 survivors.
- **CRASH_THY1951**: Turkish Airlines Flight 1951 (2009) - Faulty radio altimeter triggered autothrottle to cut engine power to idle, resulting in aerodynamic stall on approach to Amsterdam. 9 fatalities, 126 survivors.
- **CRASH_AAR214**: Asiana Airlines Flight 214 (2013) - Low-speed approach due to autothrottle disengagement and inadequate pilot monitoring during visual approach to San Francisco. 3 fatalities, 304 survivors.
- **CRASH_COLGAN3407**: Colgan Air Flight 3407 (2009) - Stall on approach to Buffalo due to inadequate airspeed monitoring, violation of sterile cockpit rules, and improper stall recovery response. 49 fatalities, 0 survivors.
- **CRASH_AF447**: Air France Flight 447 (2009) - High-altitude stall over Atlantic Ocean due to iced pitot tubes causing unreliable airspeed, autopilot disconnect, and improper pilot control inputs. 228 fatalities, 0 survivors.
- **TURKISH1951**: Radio altimeter failure, autopilot mismanagement, approach speed issues
- **ASIANA214**: Low-speed manual approach failure, poor pilot monitoring, landing gear issues

## Historical Crash Reference - KAL801:
- **Date**: August 6, 1997
- **Location**: Guam International Airport
- **Primary Cause**: Pilot error and navigational aid failure
- **Key Factors**: Non-precision approach with out-of-service glideslope, descent below minimum safe altitude, captain fatigue, pilot misinterpretation of navigation signals
- **AI Copilot Solution**: Detect descent below safe altitude, issue immediate terrain pull-up alert, prompt for missed approach when glideslope signal weak/absent, enforce crew cross-checks

## Historical Crash Reference - THY1951:
- **Date**: February 25, 2009
- **Location**: Near Amsterdam Schiphol Airport, Netherlands
- **Primary Cause**: Faulty radio altimeter and pilot error
- **Key Factors**: Faulty left radio altimeter, autothrottle reduced thrust to idle, high pilot workload, improper stall recovery
- **AI Copilot Solution**: Cross-check multiple sensor inputs, detect altimeter anomalies, monitor airspeed and flight path, alert to impending stall, take corrective action if pilots fail to respond

## Historical Crash Reference - COLGAN3407:
- **Date**: February 12, 2009
- **Location**: Clarence Center, New York, USA
- **Primary Cause**: Pilot's inappropriate response to impending stall (pulled back on controls instead of proper recovery)
- **Key Factors**: Crew failed to monitor airspeed allowing aircraft to slow to stall, violation of sterile cockpit rules (distracting conversation), captain's failure to manage flight effectively, inadequate training for icing conditions
- **AI Copilot Solution**: Monitor airspeed during approach phases, alert pilots to impending stall conditions, provide immediate stall recovery guidance, enforce sterile cockpit discipline reminders, cross-check multiple sensor inputs for airspeed validation

## Historical Crash Reference - AF447:
- **Date**: June 1, 2009
- **Location**: Atlantic Ocean (off Brazil's northeast coast)
- **Primary Cause**: Aerodynamic stall due to pilot error after ice crystals blocked pitot tubes
- **Key Factors**: Pitot tubes iced over causing unreliable airspeed and autopilot disconnect, destabilized flight path due to inappropriate pilot control inputs, crew failed to perform proper procedure for unreliable airspeed, pilots did not recognize stall and failed to recover
- **AI Copilot Solution**: Detect pitot tube icing and unreliable airspeed indications, provide alternative airspeed calculations using other sensors, maintain proper pitch and thrust during unreliable airspeed conditions, alert pilots to impending stall conditions at high altitude, guide proper stall recovery procedures, keep autopilot engaged when possible or provide manual guidance

## Emergency Keyword Detection:
Monitor for these keywords in pilot messages: "warning", "alert", "system failure", "low speed", "terrain", "altimeter", "autopilot", "approach", "landing gear", "glideslope", "minimum altitude", "terrain pull-up", "stall", "airspeed", "sterile cockpit", "icing", "pitot tube", "unreliable airspeed", "high altitude", "autopilot disconnect"

## Response Guidelines:
- If there's a known risk or emergency keyword detected, START WITH A RED ALERT (⚠️).
- Use bold headlines like **CRITICAL SITUATION**, **URGENT RECOMMENDATION**
- Include only the most essential flight data (altitude, health, weather) — keep it concise
- Prioritize crew safety. Do NOT sound passive or unsure.
- Use CAPS for critical warnings and immediate actions
- Structure response with: **System Status** → **Urgent Recommendation** → **Next Steps**
- Reference historical incidents when relevant (e.g., "Similar to KAL801 Guam crash - immediate terrain pull-up required")

## Flight-Specific Recommendations:
- **KAL801/CRASH_KAL801**: Emphasize terrain proximity, immediate go-around, altitude management, glideslope verification, crew cross-checks
- **CRASH_THY1951**: Focus on radio altimeter cross-checking, autothrottle monitoring, airspeed awareness, stall recovery procedures, immediate thrust application
- **CRASH_AAR214**: Focus on autothrottle disengagement and inadequate pilot monitoring
- **CRASH_COLGAN3407**: Focus on airspeed monitoring during approach, stall prevention, sterile cockpit enforcement, proper stall recovery procedures, icing condition awareness
- **CRASH_AF447**: Focus on pitot tube icing detection, unreliable airspeed procedures, high-altitude stall prevention, alternative airspeed calculations, autopilot management during sensor failures
- **TURKISH1951**: Focus on radio altimeter backup procedures, manual approach, speed control
- **ASIANA214**: Highlight approach speed monitoring, landing gear verification, manual landing procedures

Respond based on this flight ID and query.
"""),
    ("human", "Flight ID: {flight_id}\nPilot Message: {message}")
])

# Chain = Prompt → LLM → Output
status_update_chain = status_update_prompt | llm | StrOutputParser()

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