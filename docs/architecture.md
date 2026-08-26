# SIH26127 — System Architecture

## 1. System Objective

SIH26127 is a city-wide vehicle movement and traffic intelligence platform.

The system receives vehicle observations from multiple cameras and converts them into:

- searchable vehicle trajectories
- traffic density information
- congestion analysis
- origin-destination patterns
- blacklist and anomaly alerts
- GIS-based visualization

The prototype represents a smaller simulated camera network while keeping the architecture scalable to larger deployments.

---

# 2. High-Level Architecture

```text
                    CCTV / ANPR Cameras
                           |
                           v
                  Video / Image Streams
                           |
                           v
                  +-------------------+
                  |    ANPR Module    |
                  |                   |
                  | Vehicle Detection |
                  | Plate Detection   |
                  | Preprocessing      |
                  | OCR               |
                  +---------+---------+
                            |
                            v
                    DetectionEvent
                            |
                            v
                  +-------------------+
                  | Backend / Ingest  |
                  +---------+---------+
                            |
                            v
                  +-------------------+
                  |     Database      |
                  +---------+---------+
                            |
             +--------------+--------------+
             |              |              |
             v              v              v
      +------------+  +------------+  +------------+
      | Trajectory |  | Analytics  |  |  Alerts    |
      |   Engine   |  |   Engine   |  |   Engine   |
      +------+-----+  +------+-----+  +------+-----+
             |              |              |
             +--------------+--------------+
                            |
                            v
                    Backend API Layer
                            |
                            v
                  +-------------------+
                  | Frontend / GIS    |
                  |                   |
                  | Command Center    |
                  | Vehicle Search    |
                  | Trajectory Map    |
                  | Heatmap           |
                  | Analytics         |
                  | Alerts            |
                  +-------------------+
```

3. Core Data Flow

The normal system flow is:

Camera
   ↓
Video frame
   ↓
Vehicle detection
   ↓
License plate detection
   ↓
Image preprocessing
   ↓
OCR
   ↓
DetectionEvent
   ↓
Database
   ↓
Trajectory / Analytics / Alerts
   ↓
API
   ↓
Frontend

The key design principle is that the DetectionEvent is the common event shared by downstream modules.

4. ANPR Module
Responsibility

The ANPR module converts video/image input into standardized DetectionEvent objects.

Flow
Video / Image
      ↓
Vehicle Detection
      ↓
License Plate Detection
      ↓
Plate Crop
      ↓
Image Preprocessing
      ↓
OCR
      ↓
Confidence Estimation
      ↓
DetectionEvent
ANPR Input
video
image frames
camera metadata
ANPR Output
DetectionEvent

The ANPR module must follow:

docs/data_contract.md

The ANPR module should not implement:

database management
trajectory reconstruction
traffic analytics
frontend UI
5. Backend / Ingestion Layer
Responsibility

The backend provides the common application layer between modules and the database.

Main responsibilities:

receive DetectionEvents
validate input
store detections
retrieve detections
expose APIs
connect downstream modules
provide data to the frontend
Flow
DetectionEvent
      ↓
Validation
      ↓
Database
      ↓
Services
      ↓
API

The backend owns persistence and API contracts.

6. Database Layer

The database stores the persistent state of the system.

Initial conceptual entities:

Camera
Detection
Blacklist
Alert

Trajectory and analytics results may be derived from stored detections rather than requiring completely separate duplicated datasets.

The final physical database schema will be defined and implemented by the lead.

The database should support:

vehicle detection history
camera metadata
blacklist records
alert records
time-based queries
spatial queries where required
7. Trajectory Engine
Responsibility

The trajectory engine reconstructs the observed movement of a vehicle across cameras.

Input
DetectionEvent[]
Processing
Filter by plate
      ↓
Sort by timestamp
      ↓
Remove invalid / duplicate observations where appropriate
      ↓
Determine camera sequence
      ↓
Calculate movement information
      ↓
VehicleTrajectory
Output
VehicleTrajectory

Example:

KA01AB1234

CAM_01
  ↓
CAM_04
  ↓
CAM_07
  ↓
CAM_11
  ↓
CAM_19

The trajectory engine is implemented by the lead.

8. Analytics Engine

The analytics engine processes detection and trajectory data to produce city-level traffic intelligence.

Input
DetectionEvent[]
VehicleTrajectory[]
Main Functions
Traffic Density

Calculate vehicle volume for cameras or road segments over time.

Camera / Road
      ↓
Detection count
      ↓
Vehicles per hour
Congestion

Compare observed travel time against a normal/baseline travel time.

Camera A
    ↓
Camera B

Observed travel time
        vs
Normal travel time
        ↓
Congestion level
Origin-Destination

Aggregate movement between predefined zones.

Detection / Trajectory
        ↓
Origin Zone
        ↓
Destination Zone
        ↓
Vehicle Count

The analytics module owns the implementation of these calculations.

9. Alert Engine

The alert engine identifies events requiring attention.

Input
DetectionEvent[]
VehicleTrajectory[]
Initial Rules
Blacklisted Vehicle
plate_number ∈ blacklist
        ↓
BLACKLISTED_VEHICLE
Impossible Travel
Camera A
   ↓
Camera B

Observed time
   ↓
Implied speed
   ↓
Speed exceeds threshold
   ↓
IMPOSSIBLE_TRAVEL
Route Anomaly
Expected route
      vs
Observed route
      ↓
ROUTE_ANOMALY
Output
Alert
10. API Layer

The API is the only interface that the frontend should use to obtain system data.

The main API groups are:

Health
  ↓
Detections
  ↓
Vehicles
  ↓
Trajectories
  ↓
Cameras
  ↓
Traffic Analytics
  ↓
Alerts

Detailed endpoint definitions are documented in:

docs/api_contract.md
11. Frontend / GIS Layer

The frontend visualizes the information produced by the backend.

Main Screens
1. Command Center

Displays:

camera network
traffic heatmap
traffic statistics
congestion hotspots
active alerts
2. Vehicle Search

User enters:

KA01AB1234

The system displays:

first seen
last seen
number of detections
cameras visited
trajectory
3. Trajectory View

Displays:

CAM_01
   ↓
CAM_04
   ↓
CAM_07
   ↓
CAM_11

on a GIS map with timestamps.

4. Traffic Analytics

Displays:

traffic density
congestion
traffic trends
origin-destination flows
5. Alerts

Displays:

alert type
vehicle
camera
timestamp
severity
explanation
12. Module Ownership
Module	Owner	Main Responsibility
ANPR	Team Member 2	Vehicle/plate detection and OCR
Backend	Lead	APIs, persistence and integration
Trajectory	Lead	Vehicle movement reconstruction
Analytics	Team Member 3	Density, congestion and OD
Alerts	Team Member 3	Blacklist and anomaly rules
Frontend/GIS	Team Member 4	Dashboard and visualization
13. Dependency Rules

The dependency direction should remain:

ANPR
  ↓
DetectionEvent
  ↓
Backend / Database
  ↓
Trajectory / Analytics / Alerts
  ↓
API
  ↓
Frontend

Avoid direct dependencies such as:

Frontend → Database
Frontend → ANPR internals
Analytics → OCR implementation
Alerts → Frontend code

Modules should communicate through shared contracts and backend interfaces.

14. Prototype Strategy

The SIH prototype will use a simulated city camera network rather than attempting to integrate hundreds of real-world cameras.

The prototype may contain approximately:

8–12 simulated cameras

Each camera has:

camera ID
coordinates
road
direction
video/image source

The same architecture should conceptually support a much larger camera network.

15. Development Strategy

The system will be developed as independent modules.

Phase 1 — Foundation

Lead prepares:

repository
documentation
contracts
database design
mock data
development workflow
Phase 2 — Parallel Module Development

ANPR:

Video → DetectionEvent

Analytics/Alerts:

DetectionEvent[] → Analytics / Alerts

Frontend:

Mock API responses → Dashboard

Lead:

Database
Trajectory
Backend
Phase 3 — Integration
ANPR
  ↓
Backend
  ↓
Database
  ↓
Trajectory
Phase 4 — Analytics and Alerts
Database / Trajectory
        ↓
Analytics
        ↓
Alerts
Phase 5 — Frontend Integration
Backend APIs
      ↓
Frontend / GIS
Phase 6 — End-to-End Validation
Video
 ↓
ANPR
 ↓
DetectionEvent
 ↓
Database
 ↓
Trajectory
 ↓
Analytics
 ↓
Alerts
 ↓
API
 ↓
Dashboard

16. Integration Principle

The project should be treated as one system composed of independent modules.

Each person owns their implementation.

The lead owns:

shared interfaces
database schema
integration
system-level decisions
final testing

The primary principle is:

Everyone owns their module. The lead owns the interfaces.