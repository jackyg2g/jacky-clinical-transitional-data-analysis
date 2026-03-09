# T-001 Create Project Detail Page Route and Placeholder Page

## Requirement Description

**Infrastructure: Create Route and Placeholder Page**

Create route configuration and placeholder page components for project detail functionality, establishing the basic framework for subsequent feature development.

**Requirement Type**: Infrastructure

**Involved Domain**: Frontend

### 1. Route Configuration

Use TanStack Router to configure routing with path `/projects/:id`, where `:id` is a UUID format project ID.

**Route Parameter Validation Rules**:
- Project ID must be valid UUID v4 format (e.g., `123e4567-e89b-12d3-a456-426614174000`)
- Invalid format IDs should be rejected at route level, redirected to 404 page

### 2. Placeholder Page Layout

Create placeholder page component with the following layout structure:

```
┌─────────────────────────────────────────────────────────────┐
│  [← Return to List]                              Page Title  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│                    Page Content Area (Centered)             │
│                                                             │
│              ┌─────────────────────────┐                    │
│              │   🏗️ Page Under Construction... │                    │
│              │   Project ID: {projectId}   │                    │
│              └─────────────────────────┘                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Layout Requirements**:
- Page width: Maximum 1200px, centered display
- Top navigation area: Height 64px, contains back button and page title
- Content area: Vertically centered placeholder information
- Overall style consistent with existing pages (e.g., project list page)

### 3. Component Structure

```
project-detail/
├── route.tsx                    # Route configuration file
├── page/
│   └── ProjectDetailPage.tsx    # Page entry component
└── component/
    └── PagePlaceholder.tsx      # Placeholder content component
```

## Relevant Guidelines

**Frontend Rules:**
- Project Architecture Documentation - Understand route configuration and page component structure
- Directory Structure Documentation - Understand feature directory organization specifications

**Frontend Code Points:**
- `router/` - Route configuration file location
- `feature/project-detail/` - Project detail page code location (to be created)

**Frontend Routes:**
- `/projects/:id` - Project detail route

## Notes

- Route parameters need to be configured correctly to support project ID (UUID format)
- Placeholder page should include basic layout structure, consistent with existing pages
- Need to consider route validation and error handling (e.g., when project doesn't exist)

## Scenario

### Scenario 1: User Accesses Project Detail Page via URL

    **Scenario Description:**
    - **Precondition**: User is logged in, knows project ID
    - **Operation Steps**:
      1. User enters `/projects/123e4567-e89b-12d3-a456-426614174000` in browser address bar
      2. System parses route parameter, extracts project ID
      3. Renders project detail placeholder page
    - **Expected Result**:
      - Page loads successfully, displays basic layout
      - Project ID in URL is correctly parsed
      - Page displays placeholder content (e.g., "Project Detail Page")

## Checklist

- [ ] C-001 Route configuration correct, can access project detail page via URL
- [ ] C-002 Placeholder page component created, includes basic layout structure
- [ ] C-003 Page can correctly receive and parse route parameters (project ID)
- [ ] C-004 Route validation correct, invalid project ID format will be rejected
- [ ] C-005 Page layout consistent with existing page style

---

# T-002 Implement Project Detail Page Navigation Feature (deps: T-001)

## Requirement Description

**Feature: Implement Page Navigation**

Add navigation from project list page to project detail page functionality, supporting multiple trigger methods and complete browser history support.

**Requirement Type**: Feature

**Involved Domain**: Frontend

### 1. Navigation Trigger Methods

Support the following navigation methods on each project card/row in project list:

| Trigger Method | Behavior | Notes |
|---------|------|------|
| Click project card | Navigate to project detail page | Entire card area is clickable |
| Click "View Details" button | Navigate to project detail page | Button located at bottom right of card |
| Right-click menu → "Open in new tab" | Open detail page in new tab | Optional feature |

### 2. Project Card UI Update

```
┌──────────────────────────────────────────────────────────┐
│  Project Card (Clickable Area)                           │
│ ┌─────────────────────────────────────────────────────┐ │
│ │  📁 Project Name                         [Status Tag]  │ │
│ │  Project description text, max 2 lines, overflow... │ │
│ │                                                     │ │
│ │  Created: 2024-01-15        [View Details →] ← Button│ │
│ └─────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────┘
         ↑ Hover effect on mouse hover (background change + cursor: pointer)
```

**Interaction Details**:
- On mouse hover: Card background color changes to `bg-gray-50`, shows shadow effect
- "View Details" button: Shows underline on hover, color changes to theme color
- On click: Button shows loading state (optional, for slow network conditions)

### 3. Navigation Implementation

Use TanStack Router's `useNavigate` hook for programmatic navigation:

```typescript
// Example code
const navigate = useNavigate();
navigate({ to: '/projects/$id', params: { id: project.id } });
```

**Navigation Requirements**:
- Use `push` mode, preserve browser history
- No need to preload data before navigation (target page is responsible)
- Support `Ctrl/Cmd + Click` to open in new tab

### 4. State Preservation

When user returns to list page from detail page:
- List page scroll position should be restored (via TanStack Router's scroll restoration feature)
- Previous filter conditions and search keywords should be preserved (dependent on route state or URL parameters)

## Relevant Guidelines

**Frontend Rules:**
- Project Architecture Documentation - Understand page navigation and route navigation specifications

**Frontend Code Points:**
- `feature/project-list/` - Project list page code
- `feature/project-detail/` - Project detail page code

**Frontend Routes:**
- `/projects` - Project list route
- `/projects/:id` - Project detail route

## Notes

- Need to use correct navigation method during navigation, avoid page refresh
- Need to consider project list page loading state, avoid navigating when data hasn't loaded
- After navigation, need to preserve project list scroll position (if user returns)

## Scenario

### Scenario 1: User Navigates from Project List to Project Detail

    **Scenario Description:**
    - **Precondition**: User is on project list page, project list data has loaded
    - **Operation Steps**:
      1. User clicks "View Details" button of a project
      2. System gets the project's ID
      3. Uses route navigation to go to `/projects/{projectId}`
    - **Expected Result**:
      - Page smoothly navigates to project detail page
      - URL correctly updates to `/projects/{projectId}`
      - Browser history correctly updates, supports back operation

### Scenario 2: User Uses Browser Back Button to Return to List

    **Scenario Description:**
    - **Precondition**: User has navigated from project list to project detail page
    - **Operation Steps**:
      1. User clicks browser's back button
    - **Expected Result**:
      - Page returns to project list
      - Project list scroll position and filter state are preserved (if possible)

## Checklist

- [ ] C-001 Project list page can click to navigate to project detail page
- [ ] C-002 Project ID is correctly passed during navigation
- [ ] C-003 Browser forward/back functions work properly
- [ ] C-004 Appropriate loading state is shown during navigation
- [ ] C-005 Invalid project ID navigation shows error prompt

---

# T-003 Implement Project Basic Information Display Feature (deps: T-001, T-002)

## Requirement Description

**Feature: Project Basic Information Display**

Display complete project basic information on project detail page, including data fetching, UI display, and various state handling.

**Requirement Type**: Feature

**Involved Domain**: Full-stack

### 1. Overall Page Layout

```
┌─────────────────────────────────────────────────────────────────┐
│  Top Navigation Bar                                             │
│  [← Return to Project List]                      [Edit] [Delete]│
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Project Info Card                                       │   │
│  │                                                          │   │
│  │  Project Name                               [Status Tag] │   │
│  │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━      │   │
│  │                                                          │   │
│  │  Project Description                                     │   │
│  │  Here is the detailed description of the project...     │   │
│  │                                                          │   │
│  │  ┌──────────────┬──────────────┬──────────────┐          │   │
│  │  │  📅 Created   │  📅 Updated   │  👤 Creator   │          │   │
│  │  │  2024-01-15  │  2024-01-20  │  John         │          │   │
│  │  └──────────────┴──────────────┴──────────────┘          │   │
│  │                                                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 2. Field Display Specifications

| Field | Position | Style | Formatting Rules |
|-----|------|------|----------|
| Project Name | Top left of card | `text-2xl font-bold text-gray-900` | Display as-is, max 100 characters |
| Status Tag | Top right of card | Rounded tag, different colors for different statuses | See status color table below |
| Project Description | Below name | `text-base text-gray-600 leading-relaxed` | Supports multiple lines, no character limit |
| Created Time | Bottom info area left | `text-sm text-gray-500` | `YYYY-MM-DD HH:mm` format |
| Updated Time | Bottom info area center | `text-sm text-gray-500` | `YYYY-MM-DD HH:mm` format |
| Creator | Bottom info area right | `text-sm text-gray-500` | Display user name |

**Status Tag Color Mapping**:

| Status Value | Display Text | Background Color | Text Color |
|-------|---------|-------|-------|
| `draft` | Draft | `bg-gray-100` | `text-gray-600` |
| `active` | In Progress | `bg-blue-100` | `text-blue-700` |
| `completed` | Completed | `bg-green-100` | `text-green-700` |
| `archived` | Archived | `bg-yellow-100` | `text-yellow-700` |

### 3. Data Loading State Handling

**State Definition**:

```typescript
type LoadingState =
  | { status: 'idle' }           // Initial state
  | { status: 'loading' }        // Loading
  | { status: 'success'; data: Project }  // Load success
  | { status: 'error'; error: ErrorType } // Load failed
```

#### 3.1 Loading State UI

When `status === 'loading'`, display skeleton screen instead of loading spinner:

```
┌─────────────────────────────────────────────────────────────┐
│  Project Info Card (Skeleton)                               │
│                                                             │
│  ████████████████████████              [██████]             │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━       │
│                                                             │
│  ████████████████████████████████████████████               │
│  ████████████████████████████████                           │
│                                                             │
│  ┌──────────────┬──────────────┬──────────────┐             │
│  │  ████████    │  ████████    │  ████████    │             │
│  └──────────────┴──────────────┴──────────────┘             │
└─────────────────────────────────────────────────────────────┘
```

**Skeleton Screen Requirements**:
- Use `animate-pulse` animation effect
- Skeleton block color: `bg-gray-200`
- Layout structure consistent with actual content

#### 3.2 Error State Handling

Display different UI based on error type:

**a) Project Not Found (404)**

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│                      📭 Project Not Found                   │
│                                                             │
│           This project may have been deleted or you entered an incorrect link            │
│                                                             │
│                    [Return to Project List]                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**b) Insufficient Permission (403)**

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│                      🔒 No Access Permission                │
│                                                             │
│              You don't have permission to view this project, please contact the project administrator              │
│                                                             │
│                    [Return to Project List]                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**c) Network Error / Server Error (5xx / NetworkError)**

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│                      ⚠️ Loading Failed                      │
│                                                             │
│             Network connection error, please check your network and try again            │
│                                                             │
│                [Retry] ← Primary Button    [Return to List] ← Secondary Button          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Retry Mechanism**:
- After clicking "Retry" button, button shows loading state
- Retry calls API to fetch data again
- Maximum 3 manual retries allowed, after which retry button is hidden

## Relevant Guidelines

**Frontend Rules:**
- Project Architecture Documentation - Understand Manager pattern and data fetching specifications
- Utility Manager Documentation - Understand utility manager usage

**Backend Rules:**
- API Design Specification Documentation - Understand API design specifications

**Frontend Code Points:**
- `feature/project-detail/manager/project-detail-view-controller.tsx` - View controller
- `feature/project-detail/api/project.api.ts` - API client

**Backend Code Points:**
- `api/projects.py` - Project detail API endpoint
- `models/project.py` - Project data model

**Others:**
- Design file link: `/project-detail-basic-info.png`

## Notes

- Need to handle data loading state and failure cases
- API calls need to consider error handling and retry mechanism
- When project doesn't exist (404), need to display friendly error prompt
- Need to consider permission control (whether user has permission to view the project)
- Data format needs to be consistent with backend API response format

## Scenario

### Scenario 1: User Views Project Basic Information

    **Scenario Description:**
    - **Precondition**: User has navigated to project detail page, project ID is valid
    - **Operation Steps**:
      1. Page automatically calls API to get project details on load
      2. Display loading state (loading spinner)
      3. After API returns successfully, display project basic information
    - **Expected Result**:
      - Loading state is shown during loading
      - After data loads successfully, project name, description, creation time and other info are displayed correctly
      - Information display format is aesthetically pleasing, conforms to design specifications

### Scenario 2: Project Doesn't Exist Case

    **Scenario Description:**
    - **Precondition**: User accesses a non-existent project ID
    - **Operation Steps**:
      1. Page calls API on load
      2. API returns 404 error
    - **Expected Result**:
      - Display friendly error prompt: "Project doesn't exist or has been deleted"
      - Provide link to return to project list
      - Don't display technical error information

### Scenario 3: API Call Failure Case

    **Scenario Description:**
    - **Precondition**: Network error or server error
    - **Operation Steps**:
      1. Page calls API on load
      2. API call fails (network error or 500 error)
    - **Expected Result**:
      - Display error prompt: "Failed to load project information, please try again later"
      - Provide retry button
      - Log errors for troubleshooting

## Checklist

- [ ] C-001 Page can correctly fetch project basic information
- [ ] C-002 Project basic information displays correctly (name, description, creation time, status, etc.)
- [ ] C-003 Loading state is shown during data loading
- [ ] C-004 Error prompt is shown when data loading fails
- [ ] C-005 Friendly error prompt is shown when project doesn't exist (404)
- [ ] C-006 Corresponding error prompt is shown when permission is insufficient
- [ ] C-007 API call uses correct authentication token
- [ ] C-008 Data format is consistent with backend API response format
