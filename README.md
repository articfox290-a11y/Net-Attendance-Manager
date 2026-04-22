Net Attendance Manager

A Windows-native Python application for managing radio net attendance, tracking participants, and maintaining structured roster data using a lightweight CSV-based system.

Built with Tkinter + ttk, designed for operational use during live net sessions.

Overview

Net Attendance Manager provides a real-time interface for:

Tracking attendance during net sessions
Managing sweepers and participant roles
Recording traffic and relays
Generating and maintaining structured roster data
Producing session statistics automatically

The system is optimized for live use, not post-processing.

Core behavior and UI flow derived from the official user guide

Core Features
Live Net Control
Start / Stop roll call sessions
Open new net sessions
Integrated stopwatch + time tracking
Multi-format clock (24h / 12h / UTC toggle)
Attendance Tracking
Status control: Present / Absent / Excused
Relayed check-ins
Traffic logging per participant
Monthly attendance tracking
Data Table (TreeView)
Editable grid-based interface
Click-based status updates
Double-click inline editing
Right-click context actions (insert, delete, modify)
Sweepers Management
Mark and track sweepers dynamically
Dedicated sweeper view panel
Region-based organization support
Statistics Engine

Real-time session metrics:

Total roster count
Present / Excused / Visitors
Traffic + relays
Session duration
Start / End timestamps
Architecture
Application Model

Monolithic, class-driven structure (typical pattern: TableApp-style controller)

UI, state, and logic are tightly integrated
Event-driven updates tied to Tkinter widgets
CSV acts as persistent storage layer
UI Layout
Menu Bar → File / Options / Help
Top Frame → Controls, clock, session state
TreeView → Main data grid
Stats View → Live metrics
Sweepers View → Filtered role view
Data Layer (CSV-Based)

The system uses structured CSV files as a lightweight database.

Core Fields
Call Sign
QTH (Location)
Name
Status
Relayed
Traffic
Sweep Flag
Monthly Count
Session Metadata Header
Time Start,Time End,Total Present,Current Net Name,Total Excused,Net Control

Example:

2024-12-14 18:00:05,2024-12-14 18:25:53,0,Sample Roll Call Net,0,NL7PA

Detailed behavior documented in DB utility guide

Data Base Utility (DBU)

A companion tool for deeper data control and preprocessing.

Capabilities
CSV editing and validation
Monthly roster creation
Archiving previous nets
Reset + normalization operations
Search + insert workflows
Additional Features
Preamble management (Roll Call / Open Net)
Net type selection
Automated sorting + recalculation

Full functionality described here:

System Requirements
Platform
Windows 10 or later (required for ctypes + subprocess integration)
Python Environment
Python 3.7+
Built-in libraries:
tkinter / ttk
csv
datetime
ctypes
subprocess
re
webbrowser
Hardware
4 GB RAM minimum (8 GB recommended)
50 MB disk space
1024×768 display or higher
External Files
regions.csv
preamble.csv
PreambleRollCallNet.csv
PreambleOpenNet.csv
Zipper.py

Full breakdown:

Installation
pip install -r requirements.txt

Run the application:

python NetAttendanceManager.py
Directory Structure (Expected)
Net Attendance Manager/
│
├── NetAttendanceManager.py
├── DataBaseUtility.py
├── regions.csv
├── preamble.csv
├── PreambleRollCallNet.csv
├── PreambleOpenNet.csv
├── Zipper.py
│
├── Emergency/
├── Past Rosters/
├── UserGuide_files/

The application auto-sets its working directory on launch

Typical Workflow
Roll Call Net
Load CSV roster
Reset table
Select "Roll Call Net"
Enter net name
Start session
Mark attendance live
Save results
Open Net

Same flow, but select Open Net instead

Detailed step flows documented in DBU guide

UI Controls Summary
Menu
File → Open / Save / Data Management
Options → Font Size / Dark Mode
Help → Docs / Requirements
Toolbar / Top Frame
Start / Stop Roll Call
Open Net
Search
Refresh
Stopwatch
Advanced Features
Dark Mode toggle
Dynamic font scaling
Real-time recalculation engine
CSV-driven configuration
External script execution (via subprocess)
Troubleshooting
Common Issues
File not loading → invalid CSV format
No data warnings → load file before editing
Missing directories → verify required structure
Performance issues → reduce concurrent apps
Design Philosophy
No heavy database → CSV-first simplicity
UI-driven workflow → minimal friction during live use
Windows-native control via ctypes
Single-process architecture → predictable behavior
Disclaimer

Provided as-is. No guarantees against data loss or misuse.

Support

Contact: NL7PA
