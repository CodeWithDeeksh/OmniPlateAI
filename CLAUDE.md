# SIH26127 — Development Rules

## Project

SIH26127 is a city-wide vehicle movement and traffic intelligence platform.

The system converts vehicle/ANPR detections from multiple cameras into:

- searchable vehicle trajectories
- traffic density
- congestion analysis
- origin-destination analysis
- alerts
- GIS-based visualization

---

## Team Ownership

### Lead
- Backend architecture
- Database
- Shared schemas
- Trajectory reconstruction
- API integration
- Final integration and testing

### ANPR Module
- Vehicle detection
- License plate detection
- Image preprocessing
- OCR
- DetectionEvent generation

### Analytics & Alerts
- Traffic density
- Congestion
- Origin-Destination analysis
- Blacklist detection
- Route anomaly detection
- Alert generation

### Frontend & GIS
- Dashboard
- Map
- Vehicle search
- Trajectory visualization
- Traffic heatmap
- Analytics charts
- Alerts UI

---

## Development Rules

1. Never push directly to `main`.
2. Never push directly to `develop`.
3. Every person works on their own feature branch.
4. Only modify files belonging to your assigned module unless explicitly approved.
5. Do not change shared contracts without informing the lead.
6. Do not change the database schema without informing the lead.
7. Read the relevant files in `/docs` before implementing a module.
8. Do not commit secrets, API keys, `.env` files or large raw datasets.
9. Run tests before creating a Pull Request.
10. Keep changes modular and avoid unnecessary rewrites.
11. Do not introduce new dependencies without justification.
12. Claude Code must follow these rules and must not modify unrelated modules.

---

## Shared Contract Rule

The `DetectionEvent` structure defined in:

`docs/data_contract.md`

is the common interface between modules.

ANPR produces DetectionEvents.

Backend stores and processes DetectionEvents.

Trajectory uses DetectionEvents.

Analytics uses DetectionEvents.

Frontend consumes backend API responses.

Do not create alternative versions of the same shared data structure.

---

## Git Workflow

1. Start from `develop`.
2. Create a feature branch.
3. Work only on your assigned module.
4. Commit changes with clear commit messages.
5. Push the feature branch.
6. Create a Pull Request to `develop`.
7. Lead reviews and merges the Pull Request.
8. Do not merge your own Pull Request.

---

## Before Using Claude Code

Always:

1. Read `CLAUDE.md`.
2. Read the relevant files inside `/docs`.
3. Understand the module ownership.
4. Inspect the existing code before changing anything.
5. Ask Claude to modify only the required files.

---

## Integration Principle

The system follows:

Camera
↓
ANPR Detection
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

Modules must communicate through defined contracts rather than directly depending on another person's implementation.

## Shared File Rule

The following are shared/protected areas:

- docs/
- backend/models/
- backend/api/
- backend/main.py
- data/
- docker-compose.yml

Do not modify these casually.

If a task requires changing a shared file or contract:
1. Explain why the change is necessary.
2. Inform the lead.
3. Make the smallest compatible change.