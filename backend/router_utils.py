# backend/router_utils.py
from typing import Dict, Any, Optional
import re
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.llms import Ollama
from langchain_core.output_parsers import StrOutputParser

# Load the LLM model
llm = Ollama(model="gemma:2b")

def classify_intent(message: str) -> str:
    """
    Classifies the intent of a pilot message to route to appropriate handlers.
    
    Args:
        message: The pilot's message text
        
    Returns:
        str: Intent classification (status_update, divert_airport, similar_crashes, system_status, emergency)
    """
    message_lower = message.lower().strip()
    
    # Emergency keywords - highest priority
    emergency_keywords = [
        "emergency", "mayday", "pan pan", "crash", "impact", "terrain", "pull up",
        "warning", "alert", "failure", "malfunction", "system down", "engine out"
    ]
    
    if any(keyword in message_lower for keyword in emergency_keywords):
        return "emergency"
    
    # Intent-specific keywords
    intent_patterns = {
        "divert_airport": [
            "divert", "alternate", "nearest airport", "emergency landing", "landing gear",
            "runway", "approach", "landing", "touchdown"
        ],
        "similar_crashes": [
            "similar", "past incidents", "historical", "previous crash", "like this",
            "same situation", "what happened", "case study", "reference"
        ],
        "system_status": [
            "system status", "check systems", "instruments", "readings", "altitude",
            "speed", "fuel", "engine", "autopilot", "navigation", "radar", "weather"
        ],
        "status_update": [
            "update", "current", "situation", "what's happening", "status",
            "how are we", "current flight", "position", "location"
        ]
    }
    
    # Check each intent pattern
    for intent, patterns in intent_patterns.items():
        if any(pattern in message_lower for pattern in patterns):
            return intent
    
    # Default to status_update if no specific intent detected
    return "status_update"

def get_flight_specific_chain(flight_id: str, intent: str = "status_update") -> Any:
    """
    Returns the appropriate LangChain chain based on flight ID and intent.
    
    Args:
        flight_id: The flight identifier
        intent: The classified intent
        
    Returns:
        LangChain chain for the specific flight and intent
    """
    
    # Flight-specific emergency chains
    if intent == "emergency":
        return get_emergency_chain(flight_id)
    elif intent == "divert_airport":
        return get_divert_airport_chain(flight_id)
    elif intent == "similar_crashes":
        return get_similar_crashes_chain(flight_id)
    elif intent == "system_status":
        return get_system_status_chain(flight_id)
    else:
        return get_status_update_chain(flight_id)

def get_emergency_chain(flight_id: str) -> Any:
    """Emergency-specific chain with highest priority responses."""
    
    emergency_prompt = ChatPromptTemplate.from_messages([
        ("system", f"""
You are an AI copilot in a CRITICAL EMERGENCY situation for flight {flight_id}.
Respond with URGENT, IMMEDIATE actions only. Use CAPS for critical warnings.

## Flight-Specific Emergency Context:
- **KAL801/CRASH_KAL801**: Terrain proximity, glide slope failure, Guam approach
- **CRASH_THY1951**: Turkish Airlines Flight 1951 (2009) - Faulty radio altimeter triggered autothrottle to cut engine power to idle, resulting in aerodynamic stall on approach to Amsterdam. 9 fatalities, 126 survivors.
- **CRASH_AAR214**: Asiana Airlines Flight 214 (2013) - Low-speed approach due to autothrottle disengagement and inadequate pilot monitoring during visual approach to San Francisco. 3 fatalities, 304 survivors.
- **TURKISH1951**: Radio altimeter failure, autopilot mismanagement, approach speed issues
- **ASIANA214**: Low-speed manual approach failure, poor pilot monitoring, landing gear issues

## Emergency Response Format:
CRITICAL EMERGENCY
IMMEDIATE ACTION REQUIRED:
[Specific action in CAPS]

EMERGENCY PROCEDURES:
1. [Step 1]
2. [Step 2]
3. [Step 3]

CONTACT ATC IMMEDIATELY
"""),
        ("human", "Flight ID: {flight_id}\nEmergency Message: {message}")
    ])
    
    return emergency_prompt | llm | StrOutputParser()

def get_divert_airport_chain(flight_id: str) -> Any:
    """Divert airport chain for landing/approach scenarios."""
    
    divert_prompt = ChatPromptTemplate.from_messages([
        ("system", f"""
You are an AI copilot assisting with airport diversion for flight {flight_id}.
Provide specific airport recommendations and approach procedures.

## Flight-Specific Diversion Context:
- **KAL801/CRASH_KAL801**: Guam area - consider Andersen AFB, Saipan International
- **CRASH_AAR214**: San Francisco area - consider Oakland, San Jose, Sacramento
- **TURKISH1951**: Amsterdam area - consider Rotterdam, Eindhoven, Brussels
- **ASIANA214**: San Francisco area - consider Oakland, San Jose, Sacramento

## Response Format:
DIVERSION RECOMMENDATION:
[Recommended airport with distance and approach type]

APPROACH PROCEDURES:
- Runway: [specific runway]
- Approach: [ILS/VOR/Visual]
- Minimums: [ceiling/visibility]

ALTERNATIVES:
[List of backup airports]
"""),
        ("human", "Flight ID: {flight_id}\nDiversion Request: {message}")
    ])
    
    return divert_prompt | llm | StrOutputParser()

def get_similar_crashes_chain(flight_id: str) -> Any:
    """Similar crashes chain for historical reference."""
    
    similar_prompt = ChatPromptTemplate.from_messages([
        ("system", f"""
You are an AI copilot providing historical crash analysis for flight {flight_id}.
Reference relevant past incidents and lessons learned.

## Flight-Specific Historical Context:
- **KAL801/CRASH_KAL801**: 1997 Guam crash - terrain proximity, glide slope failure
- **CRASH_AAR214**: 2013 San Francisco crash - low-speed approach, autothrottle disengagement
- **TURKISH1951**: 2009 Amsterdam crash - radio altimeter, autopilot issues
- **ASIANA214**: 2013 San Francisco crash - low-speed approach, crew monitoring

## Response Format:
HISTORICAL REFERENCE:
[Relevant past incident with key factors]

LESSONS LEARNED:
- [Lesson 1]
- [Lesson 2]
- [Lesson 3]

APPLICABLE PROCEDURES:
[Specific procedures from historical incident]
"""),
        ("human", "Flight ID: {flight_id}\nHistorical Query: {message}")
    ])
    
    return similar_prompt | llm | StrOutputParser()

def get_system_status_chain(flight_id: str) -> Any:
    """System status chain for instrument/system checks."""
    
    system_prompt = ChatPromptTemplate.from_messages([
        ("system", f"""
You are an AI copilot providing system status analysis for flight {flight_id}.
Focus on instrument readings, system health, and operational status.

## Flight-Specific System Context:
- **KAL801/CRASH_KAL801**: Monitor glide slope, altimeter, terrain warning systems
- **CRASH_AAR214**: Check autothrottle status, airspeed indicators, approach configuration
- **TURKISH1951**: Check radio altimeter, autopilot, approach systems
- **ASIANA214**: Verify speed indicators, landing gear, auto-throttle

## Response Format:
SYSTEM STATUS:
- Altitude: [current reading]
- Speed: [current reading]
- Navigation: [status]
- Engines: [status]

INSTRUMENT CHECKLIST:
- [ ] Primary instruments
- [ ] Backup instruments
- [ ] Warning systems
- [ ] Communication systems

RECOMMENDATIONS:
[Specific system-related actions]
"""),
        ("human", "Flight ID: {flight_id}\nSystem Query: {message}")
    ])
    
    return system_prompt | llm | StrOutputParser()

def get_status_update_chain(flight_id: str) -> Any:
    """Default status update chain for general queries."""
    
    status_prompt = ChatPromptTemplate.from_messages([
        ("system", f"""
You are an AI copilot trained for aviation emergency support. 
Respond to pilot queries with clear, urgent, and structured advice when risks are detected. 

## Flight-Specific Emergency Context:
- **KAL801**: Known terrain proximity issues, descent below glide slope, mountainous approach
- **CRASH_KAL801**: Korean Air Flight 801 (1997) - Controlled flight into terrain on Guam approach due to descent below minimum safe altitude, non-functional glideslope, and poor crew resource management. 229 fatalities, 25 survivors.
- **CRASH_THY1951**: Turkish Airlines Flight 1951 (2009) - Faulty radio altimeter triggered autothrottle to cut engine power to idle, resulting in aerodynamic stall on approach to Amsterdam. 9 fatalities, 126 survivors.
- **CRASH_AAR214**: Asiana Airlines Flight 214 (2013) - Low-speed approach due to autothrottle disengagement and inadequate pilot monitoring during visual approach to San Francisco. 3 fatalities, 304 survivors.
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

## Emergency Keyword Detection:
Monitor for these keywords in pilot messages: "warning", "alert", "system failure", "low speed", "terrain", "altimeter", "autopilot", "approach", "landing gear", "glideslope", "minimum altitude", "terrain pull-up"

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
- **CRASH_AAR214**: Highlight approach speed monitoring, landing gear verification, manual landing procedures
- **TURKISH1951**: Focus on radio altimeter backup procedures, manual approach, speed control
- **ASIANA214**: Highlight approach speed monitoring, landing gear verification, manual landing procedures

Respond based on this flight ID and query.
"""),
        ("human", "Flight ID: {flight_id}\nPilot Message: {message}")
    ])
    
    return status_prompt | llm | StrOutputParser()

# Flight-specific fallback messages
FLIGHT_FALLBACKS = {
    "KAL801": "CRITICAL TERRAIN ALERT\nFlight KAL801 is descending below glide slope near Guam. Initiate an immediate go-around. Monitor altitude closely and cross-check terrain avoidance systems.",
    "CRASH_KAL801": "HISTORICAL KAL801 REFERENCE\nThis flight pattern matches Korean Air Flight 801 (1997 Guam crash). Immediate terrain pull-up required. Verify glideslope status and initiate missed approach procedures.",
    "CRASH_THY1951": "STALL ALERT: Faulty altitude reading detected. Add thrust immediately and prepare for go-around! Cross-check radio altimeters and monitor airspeed closely.",
    "CRASH_AAR214": "LOW SPEED APPROACH WARNING\nFlight 214 is approaching SFO at dangerously low speed. Check autothrottle status and increase thrust immediately. Visual approach monitoring required.",
    "TURKISH1951": "AUTOPILOT MALFUNCTION\nFlight 1951 shows radio altimeter discrepancies. Disengage autopilot, manually stabilize descent, and confirm altitude using backup instruments.",
    "ASIANA214": "LOW SPEED APPROACH WARNING\nFlight 214 is approaching SFO at dangerously low speed. Increase thrust and adjust pitch angle immediately. Visual confirmation advised."
}

def get_fallback_message(flight_id: str, intent: str = "status_update") -> str:
    """
    Returns appropriate fallback message based on flight ID and intent.
    
    Args:
        flight_id: The flight identifier
        intent: The classified intent
        
    Returns:
        str: Fallback message
    """
    base_fallback = FLIGHT_FALLBACKS.get(flight_id, "⚠️ AI Copilot temporarily unavailable. Refer to emergency checklist.")
    
    if intent == "emergency":
        return f"🚨 EMERGENCY FALLBACK: {base_fallback}"
    elif intent == "divert_airport":
        return f"🛬 DIVERSION FALLBACK: {base_fallback} - Contact ATC for nearest suitable airport."
    elif intent == "similar_crashes":
        return f"📚 HISTORICAL FALLBACK: {base_fallback} - Review emergency procedures for similar incidents."
    elif intent == "system_status":
        return f"🔧 SYSTEM FALLBACK: {base_fallback} - Check all primary and backup instruments."
    else:
        return base_fallback 