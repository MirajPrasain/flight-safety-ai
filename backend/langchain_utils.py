# backend/langchain_utils.py
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.llms import Ollama
from langchain_core.output_parsers import StrOutputParser

# Load your local model from Ollama
# Switched from "mistral" to "gemma:2b" for performance optimization in demo environment
llm = Ollama(model="gemma:2b")

# 🛑 KAL801 Hallucination Prevention System
# ✅ Hardcoded grounded context for Korean Air Flight 801
KAL801_CONTEXT = """
CRITICAL FLIGHT CONTEXT - KAL801:
Flight ID: KAL801
Location: Guam, Mariana Islands, Pacific Ocean
Airport: Guam International Airport (GUM)
Date: August 6, 1997
Situation: Night approach with non-functional ILS glideslope
Critical Warnings: Terrain alert near Nimitz Hill, descent below minimum safe altitude
⚠️ RESTRICTION: Only suggest airports within Mariana Islands region. Do not hallucinate airports like San Francisco, Los Angeles, Oakland, San Jose, Sacramento, or any mainland US airports.
✅ VALID AIRPORTS (Mariana Islands only):
- Andersen AFB (PGUA) - 8 NM from GUM, Ceiling: 800ft, Visibility: 2 miles
- Rota International (ROP) - 45 NM from GUM, Ceiling: 1200ft, Visibility: 3 miles  
- Saipan International (SPN) - 120 NM from GUM, Ceiling: 1500ft, Visibility: 4 miles
🚫 BLOCKED: Any airport > 200 NM from Guam or outside Mariana Islands
"""

# ✅ Airport whitelist for KAL801 to prevent hallucination (Mariana Islands only)
VALID_KAL801_AIRPORTS = [
    "Andersen AFB (PGUA)",
    "Rota International Airport (ROP)", 
    "Saipan International Airport (SPN)"
]

# 🛑 Enhanced airport data with realistic ceiling/visibility
KAL801_AIRPORT_DATA = {
    "Andersen AFB (PGUA)": {
        "distance": "8 NM from GUM",
        "ceiling": "800ft",
        "visibility": "2 miles",
        "approach": "ILS RWY 06L",
        "minimums": "800/2"
    },
    "Rota International (ROP)": {
        "distance": "45 NM from GUM", 
        "ceiling": "1200ft",
        "visibility": "3 miles",
        "approach": "VOR RWY 08",
        "minimums": "1200/3"
    },
    "Saipan International (SPN)": {
        "distance": "120 NM from GUM",
        "ceiling": "1500ft", 
        "visibility": "4 miles",
        "approach": "ILS RWY 07",
        "minimums": "1500/4"
    }
}

def validate_kal801_airport_suggestion(response: str) -> str:
    """
    🛑 Validates KAL801 responses to prevent hallucinated airport suggestions
    ⚠️ Blocks fallback to mainland US airports and enforces Mariana Islands only
    """
    if "KAL801" not in response:
        return response
    
    # Check for invalid airport suggestions (mainland US and other regions)
    invalid_airports = [
        "San Francisco", "SFO", "Los Angeles", "LAX", "Seattle", "SEA",
        "New York", "JFK", "Chicago", "ORD", "Miami", "MIA",
        "Dallas", "DFW", "Denver", "DEN", "Atlanta", "ATL",
        "Oakland", "OAK", "San Jose", "SJC", "Sacramento", "SMF",
        "Honolulu", "HNL", "Phoenix", "PHX", "Las Vegas", "LAS"
    ]
    
    response_lower = response.lower()
    for invalid_airport in invalid_airports:
        if invalid_airport.lower() in response_lower:
            return f"""⚠️ UNABLE TO RECOMMEND ALTERNATE AIRPORT DUE TO LOCATION CONFLICT

Aircraft KAL801 is operating in Guam, Mariana Islands and cannot divert to mainland US airports.

VALID MARIANA ISLANDS OPTIONS:
• Andersen AFB (PGUA) - 8 NM from GUM, Ceiling: 800ft, Visibility: 2 miles
• Rota International (ROP) - 45 NM from GUM, Ceiling: 1200ft, Visibility: 3 miles  
• Saipan International (SPN) - 120 NM from GUM, Ceiling: 1500ft, Visibility: 4 miles

Please contact Guam ATC for local diversion assistance within Mariana Islands region."""
    
    return response

def get_kal801_grounded_prompt(base_prompt: str) -> str:
    """
    ✅ Injects fixed location metadata for Guam into KAL801 prompts
    """
    return f"{KAL801_CONTEXT}\n\n{base_prompt}"

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
- If there's a known risk or emergency keyword detected, START WITH A CRITICAL ALERT.
- Use clear headlines like CRITICAL SITUATION, URGENT RECOMMENDATION (no markdown formatting)
- Include only the most essential flight data (altitude, health, weather) — keep it concise
- Prioritize crew safety. Do NOT sound passive or unsure.
- Use CAPS for critical warnings and immediate actions
- Structure response with: System Status → Urgent Recommendation → Next Steps
- Reference historical incidents when relevant (e.g., "Similar to KAL801 Guam crash - immediate terrain pull-up required")
- Avoid using ** or * markdown formatting - use plain text instead

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

# 🛑 KAL801-specific emergency advisor with grounded context
def get_emergency_advisor_chain_with_validation(flight_id: str):
    """
    ✅ Returns emergency advisor chain with KAL801-specific validation
    """
    if flight_id == "KAL801":
        # Use KAL801 grounded context
        kal801_system_prompt = get_kal801_grounded_prompt("""You are an expert AI flight advisor for pilots, providing concise, immediate, and actionable advice during critical flight situations. Your goal is to prevent crashes by recommending precise pilot actions based on real-time aircraft data.
        Focus on specific, numerical instructions when possible (e.g., "Reduce throttle to 70%", "Maintain pitch +5 degrees").
        If a warning is present, specifically address it.
        Output only the actionable advice, no conversational filler.
        
        CRITICAL FOR KAL801: Focus on terrain proximity, immediate go-around, altitude management, and Guam-specific procedures.
        
        DIVERSION AIRPORTS (Mariana Islands only):
        • Andersen AFB (PGUA) - 8 NM from GUM, Ceiling: 800ft, Visibility: 2 miles
        • Rota International (ROP) - 45 NM from GUM, Ceiling: 1200ft, Visibility: 3 miles  
        • Saipan International (SPN) - 120 NM from GUM, Ceiling: 1500ft, Visibility: 4 miles
        
        NEVER suggest airports outside Mariana Islands region.""")
        
        kal801_prompt = ChatPromptTemplate.from_messages([
            ("system", kal801_system_prompt),
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
        
        # Create chain with validation
        chain = kal801_prompt | llm | StrOutputParser()
        
        # Add validation wrapper
        async def validated_chain(input_data):
            response = await chain.ainvoke(input_data)
            return validate_kal801_airport_suggestion(response)
        
        return validated_chain
    else:
        # Standard chain for other flights
        return emergency_advisor_prompt | llm | StrOutputParser()

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

# 🛑 KAL801-specific risk explanation with grounded context
def get_risk_explanation_chain_with_validation(flight_id: str):
    """
    ✅ Returns risk explanation chain with KAL801-specific validation
    """
    if flight_id == "KAL801":
        # Use KAL801 grounded context
        kal801_system_prompt = get_kal801_grounded_prompt("""You are an expert AI aviation safety analyst. Your task is to explain clearly and concisely why a given flight situation is unsafe or has high risk. Refer to standard aviation safety principles, common crash causes, and the provided data.
        Explain the risk in plain aviation English, avoiding jargon where possible.
        Focus on specific data points that contribute to the unsafe condition.
        
        CRITICAL FOR KAL801: Focus on Guam terrain proximity, non-functional ILS, night approach risks, and historical KAL801 crash factors.""")
        
        kal801_prompt = ChatPromptTemplate.from_messages([
            ("system", kal801_system_prompt),
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
        
        # Create chain with validation
        chain = kal801_prompt | llm | StrOutputParser()
        
        # Add validation wrapper
        async def validated_chain(input_data):
            response = await chain.ainvoke(input_data)
            return validate_kal801_airport_suggestion(response)
        
        return validated_chain
    else:
        # Standard chain for other flights
        return risk_explanation_prompt | llm | StrOutputParser()

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