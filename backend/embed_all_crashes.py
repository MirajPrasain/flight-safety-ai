# backend/embed_all_crashes.py => Batch Embedding Pipeline, a standalone script to batch embed and store 5 historic crash summaries into MongoDB using your embed_and_store_flight_summary() function.

import asyncio #Gives you access to Python's event loop system — required to run asynchronous functions like await.
from embedding_utils import embed_and_store_flight_summary

crashes = [
    {
        "flight_id": "CRASH_KAL801",
        "summary": (
            "Korean Air Flight 801 crashed due to Controlled Flight Into Terrain (CFIT) during approach "
            "in poor weather. Terrain warnings were triggered: TERRAIN_PULL_UP, GLIDE_SLOPE_WARNING, and SINK_RATE. "
            "The aircraft descended below the glide slope despite alerts, indicating ineffective terrain advisory usage."
        ),
        "causal_tags": ["Terrain", "CFIT", "Advisory Ignored"]
    },
    {
        "flight_id": "CRASH_ASIANA214",
        "summary": (
            "Asiana Airlines Flight 214 crashed during landing at San Francisco due to a dangerously low approach speed. "
            "Improper flap and thrust configuration combined with poor monitoring of auto-throttle led to a stall. "
            "Warnings such as stick shaker and configuration alerts were ineffective in prompting recovery."
        ),
        "causal_tags": ["Low Speed", "Landing Config", "Auto-throttle", "Stall"]
    },
    {
        "flight_id": "CRASH_COLGAN3407",
        "summary": (
            "Colgan Air Flight 3407 entered an aerodynamic stall on approach due to improper pilot response. "
            "The pilot pulled up aggressively instead of following stall recovery procedures. The stick shaker and pusher were active, "
            "but pilot override led to loss of control."
        ),
        "causal_tags": ["Stall Recovery", "Pilot Error", "Stick Shaker"]
    },
    {
        "flight_id": "CRASH_TURKISH1951",
        "summary": (
            "Turkish Airlines Flight 1951 crashed on final approach due to a faulty radio altimeter causing auto-throttle "
            "to reduce thrust. The aircraft slowed excessively without pilot correction. Despite warnings, no recovery action was taken in time."
        ),
        "causal_tags": ["Auto-throttle", "Sensor Error", "Low Thrust"]
    },
    {
        "flight_id": "CRASH_TENERIFE1977",
        "summary": (
            "Tenerife disaster involved two 747s colliding on the runway in fog. KLM aircraft began takeoff without clearance, "
            "despite ATC and Pan Am still taxiing. Miscommunication and poor visibility led to the deadliest crash in aviation history. "
            "Voice alert to abort was insufficient or delayed."
        ),
        "causal_tags": ["Runway Incursion", "Communication Error", "Fog", "Voice Warning Ignored"]
    }
]

async def embed_all():
    for crash in crashes:
        await embed_and_store_flight_summary(crash["flight_id"], crash["summary"])

# ✅ After this runs, MongoDB will contain 5 documents, each with:
# {
#   "flight_id": "CRASH_...",
#   "summary": "...",
#   "vector": [0.34, -0.12, ..., 0.01]  // 384 floats
# }

if __name__ == "__main__":
    asyncio.run(embed_all())
