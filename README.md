# 🏓 Pickleball Tournament Management System

A robust, service-oriented web application built with Python and Flask for managing local Pickleball tournaments. This system handles everything from player registration and automated team pairing to complex match generation (Round Robin & Knockout) and Best-of-3 (BO3) score tracking.

## ✨ Key Features

- **Player & Team Management:** Register players, track their Elo ratings, and automatically generate fair match-ups (Mixed Doubles, Men's/Women's Doubles) or allow manual pairings.
- **Dynamic Tournament Formats:** Support for multiple formats including Group Stage + Knockout and single Round Robin.
- **Automated Scheduling:** Automatically generates matches based on the selected format and distributes teams into distinct groups (e.g., Group A and Group B).
- **BO3 Scoring System:** Specialized tracking for Best-of-3 matches, enforcing rule validation, and automatically determining winners to advance them to the next bracket.
- **Real-time Leaderboards:** Instantly calculates standings based on win rates and point differentials.

## 🏗 Architecture & Refactoring

This project was intentionally refactored from a monolithic structure (a single "God Object" managing all database interactions) into a clean, **Modular Service-Oriented Architecture**. This approach significantly improves scalability, debugging, and code maintainability.

### Core Modules:
- `database.py`: Centralized SQLite database connection management.
- `player_manager.py`: Handles player CRUD operations and tournament enrollment.
- `team_manager.py`: Contains algorithms for randomized team pairings and bracket seeding.
- `match_manager.py`: The core algorithmic engine responsible for stage transitions (Semi-finals, Third Place, Finals) and complex query execution (e.g., handling tie-breakers and BO3 score validation).

## 🛠 Tech Stack

- **Backend:** Python 3, Flask
- **Database:** SQLite3 (Custom relational schema with strict UNIQUE constraints and automated indexing)
- **Frontend:** HTML5, CSS3, Jinja2 (Dynamic templating)

## 🚀 Getting Started

### Prerequisites
Make sure you have Python 3.x installed on your machine.

### Installation

1. **Clone the repository**
   ```bash
   git clone [https://github.com/ngbinhminhdev-blip/pickleball-tournament-management]
   cd pickleball-tournament-app