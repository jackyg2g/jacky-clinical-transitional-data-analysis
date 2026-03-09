# Requirement Analysis and Structured Breakdown

## Command Purpose

Build new IasoSpec changes with strict validation

## Guardrail Rules

- If the feature is large, it needs to be broken down into multiple subtasks
- Guidelines provided by the user must be provided in relevant tasks
- Do not write any code during the proposal phase. Strictly only create design documents (proposal.md, tasks.md, design.md). Implementation is done in the apply phase after approval.

## Execution Flow

### Step 1: Understand Requirements

1. **Parse User Input**
   - Identify multiple requirement points in user description (may be separated by numbers, newlines, semicolons, hash signs, etc.)
   - Distinguish requirement types: bugfix, feature change, new feature, refactor, etc.
   - Identify involved domains: frontend, backend, full-stack
   - Identify requirements that can be split: multiple independent functional modules, parts that can be developed in parallel, different business domains, etc.

2. **View Relevant Code**
   - Search for relevant code files (including frontend and backend) based on keywords in requirement description
   - Understand existing implementation logic and architecture, identify potentially affected modules and files

3. **Identify Unclear Business or Process Issues**
   - Check if there is missing information in the requirement description: functional details, edge cases, error handling, UI/UX details, data formats and API interfaces, etc.
   - Business or functionality unclear, implementation issues (such as whether an interface exists, etc.) need to be sorted out by yourself, cannot be considered as unclear points.

### Step 2: Confirm with User

1. **Ask Clarifying Questions**
   - List questions that need confirmation in a clear, structured way
   - Each question should explain why confirmation is needed, provide possible options or suggestions, give recommended answers

2. **Wait for User Response**
   - Update requirement understanding based on user's response
   - If there are still unclear points, continue asking, wait for user response
   - Only proceed to Step 3 after all unclear points have been clearly answered by the user

### Step 3: Break Down Requirements

1. **Evaluate Requirement Complexity**
   - Determine if the requirement needs to be split into multiple **independent requirements** (not subtasks)
   - Consider factors: number of files involved, independence of functional modules, whether they can be developed in parallel, differences in business domains
   - **Key Principle**: If split requirements have dependencies, dependencies must be marked

2. **Split Independent Requirements - Core Principles**
   - Each Task must focus on a single small feature
   - Except for dependencies, each Task should be completely independent and parallelizable, without code conflicts that would be modified simultaneously

- **When Must Split**:
  - Requirement contains multiple independently completable functional modules
  - Requirement contains parts that can be developed in parallel
  - Requirement involves different business domains or technology stacks
  - Requirement contains multiple unrelated bugfixes or feature points
  - Requirement is large in scale and needs to be implemented step by step in development order

- **Split Principles**:
  - Each requirement uses independent T-XXX numbering
  - Has independent Checklist (starting from C-001)
  - If dependencies exist, mark in title `(deps: T-xxx, T-xxx)`, **dependencies are important, please add them**

- **Typical Scenarios for Breakdown by Development Order**:
  - **Basic Approach**:
    Infrastructure (routes, placeholders) → Basic functionality (navigation, data fetching) → Core functionality (feature A, feature B, feature C) → Enhanced functionality (optimization, edge case handling)
  - **New Page/New Feature Module**: First create route and empty placeholder page → Implement page navigation → Implement page basic layout → Implement feature A → Implement feature B → Implement feature C
  - **New API Interface**: First define interface contract and data structure → Implement backend interface → Implement frontend call → Implement error handling → Implement edge cases
  - **Complex Interaction Flow**: First implement basic flow → Add exception handling → Add optimization and enhancement features
  - **Refactoring Task**: First create new structure → Migrate partial functionality → Gradually replace old implementation → Clean up old code

- **Breakdown Granularity Standards**:
  - Each task should be completable within 1-2 days
  - Each task has clear inputs and outputs
  - Each task can be independently tested and verified after completion

- **Cases Not to Split**:
  - Functional modules are tightly coupled, splitting would increase complexity
  - Requirement scale is moderate, can be completed in one task
  - Simple bugfix or small feature adjustment

### Step 4: Generate Structured Documents

1. **Review Project and Create Proposal**
   - Check if `.iasospec` / `.iasospec/changes` / `.iasospec/archive` exist in project directory, if not create them using `mkdir` command
   - Review `.iasospec/project.md` and check relevant code or documents (e.g., via `rg`/`ls`) to base the proposal on current behavior; note any gaps that need clarification.
   - Select a unique verb-starting `change-id`, and create `proposal.md`, `tasks.md`, and `design.md` (when needed) under `.iasospec/changes/<id>/`.
   - Write the structured description of the entire requirement in `proposal.md`, focusing on the overall picture.
   - Capture architectural reasoning in `design.md` when the solution spans multiple systems, introduces new patterns, or needs trade-off discussion before committing to a spec.

2. **Handle Links and Image Resources**
   - Identify links and images in user description, reference them in documents
   - Download images and save to `.iasospec/changes/<id>/images` directory (create if directory doesn't exist when there are image links)
   - Image naming convention: `T-XXX-{descriptive-name}.{extension}`

3. **Determine Relevant Guidelines**
   - Based on task type, determine rule documents and code locations to reference
   - Organize by categories: Frontend Rules, Backend Rules, Frontend Code Points, Frontend Routes, Backend Code Points, Others

4. **Identify Notes**
   - Technical difficulties, edge cases, other functional modules that may be affected, performance considerations, compatibility requirements, etc.

5. **Generate Tasks and Checklists**
   - Each Task is an independent small feature, using numbering format T-001, T-002, T-003, ...
   - Each Task should include basic requirement description, relevant guidelines, notes, checklist, etc.
   - Each Task should have at least one `Scenario` and cross-reference relevant capabilities when appropriate.
   - Each Checklist item should be a verification point for feature completion, with clear acceptance criteria, covering main functionality and edge cases
   - Use numbering format: C-001, C-002, C-003, ...

6. **Strictly Follow Document Templates**
   - Task document template: `.iasospec/template/task.md`
   - Design document template: `.iasospec/template/design.md`
   - Task example: `.iasospec/example/task.md`
   - Design example: `.iasospec/example/design.md`
