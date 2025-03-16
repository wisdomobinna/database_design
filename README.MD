## Purpose

- Demonstration of database application using crime data collected from multiple sources.

## Requirements:

- Docker installed.
- Project tables, in .csv format, placed into /main/data_files directory.

## Setup Instructions

- Unzip the project.
- Go in to the directory and open a command prompt or powershell.
- Run `docker-compose up -d --build`
  - Initial setup of tables will take about 30 seconds.
- In any browser, go to `localhost:8000`
- Interact with the dashboard.

## Procedures

- Raw queries were used instead of ORM as much as possible.
- `create.sql` defines the endgoal table structure.
- Given cleaned up data is .csv file, `staging` table was created to load it to Postgres, then `modify.sql` queries were used to split and load into their respective tables.
- Command added so file upload happens when container starts.
