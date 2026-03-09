# Archive Requirement Documents

## Prerequisites

- Read the direct subdirectories under `.iasospec/changes`, each subdirectory is a change, the directory name is the change-id
- User must specify change-id, user can optionally specify Task number
- If user does not specify change-id, list all changes and prompt user to select, cannot continue until change-id is confirmed

## Execution Flow

1. Determine the change ID to archive
2. Use `mv` command to move `.iasospec/changes/<change-id>` directory to `.iasospec/archive/<date>.<change-id>`
3. `<date>` is the date, incrementally, e.g., `2026-01-01`
