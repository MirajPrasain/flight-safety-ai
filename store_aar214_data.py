# store_aar214_data.py
# Stores Asiana Airlines Flight 214 crash data with vector embedding for similarity search

import requests
import json

# Asiana Airlines Flight 214 crash data
aar214_data = {
    "flight_id": "CRASH_AAR214",
    "title": "Asiana Airlines Flight 214",
    "date": "2013-07-06",
    "location": "San Francisco International Airport, San Francisco, California, USA",
    "summary": "Investigators concluded that the crash of Asiana Airlines Flight 214 was caused by the flight crew's mismanagement of the final approach, with deficiencies in the autothrottle system's documentation and in pilot training cited as contributing factors.",
    "passengers": 291,
    "fatalities": 3,
    "survivors": 304,
    "primary_cause": "The NTSB found that the pilots failed to monitor airspeed and maintain a proper glide path during the visual approach. The crew inadvertently deactivated the automatic speed control (autothrottle) and did not realize it was no longer maintaining the target speed, resulting in an aerodynamic stall short of the runway.",
    "key_factors": [
        "The ILS glide slope at SFO was out of service, requiring a fully visual approach which added to the pilots' workload and challenge",
        "Autothrottle was left in a mode that did not advance thrust (throttle hold at idle) and the crew was unaware that the system was not actively maintaining airspeed",
        "Pilot flying had only 43 hours of experience in the Boeing 777, was still in training (initial operating experience), and lacked familiarity with the aircraft's automated flight systems",
        "The instructor pilot (pilot-in-command) provided inadequate supervision and failed to intervene timely; additionally, crew fatigue and insufficient training practices contributed to poor performance"
    ],
    "how_ai_copilot_could_help": "An AI co-pilot could continuously monitor critical flight parameters (like airspeed, altitude, and glide path) and alert the crew the moment deviations occur (for example, if airspeed falls below safe threshold on approach). It would cross-check automation status, so if a system like the autothrottle is inadvertently disengaged or not controlling speed as expected, the AI would notify pilots or even adjust throttle to maintain target speed. Furthermore, an AI assistant could provide guidance during a visual approach – highlighting glide path cues and recommending corrections – effectively acting as a vigilant co-instructor. In a scenario with less experienced crew or high workload, the AI would help compensate by ensuring standard operating procedures are followed (e.g., callouts for speed and altitude), and by counteracting human factors like fatigue or confusion about automation, thereby potentially preventing this kind of accident.",
    "embedding_summary": "Asiana Airlines Flight 214, 2013-07-06, at San Francisco International Airport in California – crashed due to the flight crew over-relying on automation and failing to maintain adequate airspeed during a visual approach. Primary cause: the pilots inadvertently disabled the 777's autothrottle and did not realize it wasn't maintaining speed, causing the aircraft to descend below the glidepath and collide with the seawall just short of the runway. Key factors: the runway's ILS glideslope was offline (requiring a manual visual landing), the captain flying had very limited experience on the 777, and deficiencies in crew training, fatigue, and supervision contributed to the mishap.",
    "causal_tags": ["Low Speed", "Auto-throttle", "Visual Approach", "Pilot Training", "Automation Dependency", "Stall"]
}

def store_aar214_data():
    """Store Asiana Airlines Flight 214 crash data via API"""
    url = "http://localhost:8000/store_crash_data/"
    
    try:
        response = requests.post(url, json=aar214_data)
        
        if response.status_code == 200:
            print("✅ Asiana Airlines Flight 214 crash data stored successfully!")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Failed to store data. Status: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error connecting to API: {e}")

if __name__ == "__main__":
    store_aar214_data() 