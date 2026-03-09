# Proposal: Add Project Detail Page

## Requirement Summary

Support entering project detail page from project list, centrally display basic information of a single project (name, description, status, time, etc.), and maintain consistency with existing layout.

## Background and Motivation

- Users can currently only see project cards on the list page, unable to view complete information, need a separate detail entry point.
- The project management system has list pages and project data, but lacks detail pages and routes, making it necessary to rely on other entry points or subsequent features to view details.
- This change fills the "from list to detail" loop, providing a page foundation for subsequent features like project members and settings.

## Goals and Success Criteria

- Provide a centralized project detail page within the project context.
- Users can enter the detail page from the list and see complete basic project information on one screen.
- Detail page layout is consistent with existing pages (e.g., asset page), reusing top bar and sidebar.

**Success Criteria**:

- Users can navigate from list to detail page with project ID in URL.
- Detail page correctly displays name, description, creation time, update time, status and other fields.
- When project doesn't exist or user lacks permission, there are clear prompts and return entry points.

## Scope and Boundaries

### In Scope (Included This Time)

- Project detail route and placeholder page (e.g., `/projects/:id`).
- Navigation from project list to detail page (click to enter, browser forward/back).
- Project basic information display (name, description, creation/update time, status, etc.), data from existing API.

### Out of Scope (Not Included This Time)

- Project member management, project settings — future features.
- Mobile adaptation — future optimization.
- Edit, delete and other operations within project detail — future features.

## User/System Scenarios

### Scenario 1: Enter and View Project Detail from List

- **Who**: Logged-in users with access to project list.
- **When/Condition**: On project list page, project list has loaded.
- **What**: Click "View Details" or card of a project to enter that project's detail page.
- **Result**: See the project's name, description, status, creation/update time and other information, layout consistent with existing system.

### Scenario 2: Access Project Detail via Direct URL

- **Who**: Logged-in user (knows project ID, e.g., from email/shared link).
- **When/Condition**: Enter or open detail URL containing project ID in browser.
- **What**: Open detail page, system fetches and displays project information based on ID.
- **Result**: Same detail display as Scenario 1; if ID is invalid or lacks permission, see clear prompt and return entry point.

### Scenario 3: Project Doesn't Exist or Load Failed

- **Who**: Same as above.
- **When/Condition**: Access non-existent project ID, or API reports error/timeout.
- **What**: System displays error state (e.g., 404, no permission, network error).
- **Result**: Friendly prompt text, retry or return to list entry point, without exposing technical details.

## Constraints and Assumptions

### Constraints

- Detail page needs to be consistent with existing page layout (shared top bar, sidebar), not a separate layout.
- Routes and frontend tech stack need to be consistent with existing project specifications (e.g., TanStack Router).
- Data source is existing project API, no new backend data model; if API doesn't have detail endpoint yet, needs to be clarified and included in implementation scope within this requirement.

### Assumptions

- Project list and detail use the same permission model, visible in list means can enter detail.
- Project "basic information" refers to: name, description, status, creation time, update time and other existing model fields; doesn't include members, settings, etc.
- Currently only considering desktop layout; mobile is future optimization.

## Terms and Terminology

| Term/Abbreviation | Meaning | Notes |
|----------|------|------|
| Project Detail Page | Display page with single project as main subject, showing basic project info | Corresponding route e.g., `/projects/:id` |
| Project List Page | Page displaying multiple project cards | Corresponding route e.g., `/projects` |
| Basic Information | Name, description, status, creation/update time, etc. | From existing Project model, doesn't include members, settings, etc. |

## References and Links

- Existing project list and routes: Route `/projects`.
- Layout reference: Consistent with asset page, etc. (e.g., `/mushroom/project/asset`).
- Design files or screenshots can be placed in `.iasospec/changes/<change-id>/images` and referenced here.
