# Execute Development Requirements

## Prerequisites

- Read the direct subdirectories under `.iasospec/changes`, each subdirectory is a change, the directory name is the change-id
- User must specify change-id, user can optionally specify Task number
- If user does not specify change-id, list all changes and prompt user to select, cannot continue until change-id is confirmed
- User can specify Task numbers while specifying change-id (e.g., `T-001`, `T-001, T-002`), if not specified then all tasks

## Execution Flow

### Step 1: Read and Parse Requirements

1. **Read Task Files**
   - Read `proposal.md`, `task.md` and `design.md` (if exists) under `.iasospec/changes/<change-id>`
   - `proposal.md` provides the overall context of the change (requirement summary, goals, scope, user scenarios, etc.), helpful for understanding task background
   - If the above files do not exist, prompt user to use specify command to create requirement documents first

2. **Parse User Specified Requirements**
   - Identify requirement numbers (T-XXX) in user input
   - Support single requirement (e.g., `T-001`) or multiple requirements (e.g., `T-001, T-002` or `T-001 T-002`)
   - Find corresponding requirement sections in the document

3. **Extract Requirement Information**
   - Identify dependencies, if different requirements have dependencies, ensure execution order does not violate dependency relationships
   - Read all guidance files (frontend rules, backend rules, Code Points, routes, etc.) and notes mentioned in specific requirements

### Step 2: Execute Development Tasks

1. **Read Relevant Guidelines**
   - Read guidance documents, images, PRs mentioned in requirements (if links are provided, use gh cli)
   - Understand relevant code modules and architecture
   - If additional conventions or explanations are needed, refer to `.iasospec/project.md` (located in `.iasospec/` directory - if not visible, run `ls .iasospec`).

2. **Implement Features**
   - Implement according to requirement description and Checklist items
   - Follow project architecture and code conventions

### Step 3: Check Task Completion Status

1. **Check Scenarios**

- Check from code level if all `Scenario` of the Task are correct

2. **Complete Checklist Items**
   - After completing each Checklist item, update status in `.iasospec/changes/<change-id>/task.md`: `- [x]`
   - Keep incomplete items as: `- [ ]`

3. **Confirm Completion**
   - After all Checklist items are completed, mark the requirement as completed
