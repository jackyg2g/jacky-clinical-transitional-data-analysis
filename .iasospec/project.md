# IASO Clinic AI File Processor Project

## Project Overview

IASO Clinic Medical Clinic Management System - AI File Intelligent Processing Extension Module

## Change History

| Change ID | Title | Status | Created |
|-----------|------|------|----------|
| implement-ai-file-processor | Implement AI File Intelligent Processing Platform | In Proposal | 2025-02-09 |

## Active Changes

### implement-ai-file-processor

- **proposal.md**: Requirement proposal document
- **design.md**: Architecture design document
- **tasks.md**: Task breakdown document

**Task List**:
- T-001: Backend Infrastructure Setup
- T-002: Kimi AI Service Wrapper (deps: T-001)
- T-003: File Rename Async Task Implementation (deps: T-001, T-002)
- T-004: Integrity Check Async Task Implementation (deps: T-001, T-002)
- T-005: Frontend Basic Layout Implementation
- T-006: File Rename Page Implementation (deps: T-005)
- T-007: Integrity Check Page Implementation (deps: T-005)
- T-008: Task List Page Implementation (deps: T-005)
- T-009: Integration Testing and Optimization (deps: T-003, T-004, T-006, T-007, T-008)

## Tech Stack

- **Frontend**: React + TypeScript + Vite + TanStack Router + Tailwind CSS v4 + shadcn/ui
- **Backend**: Django REST Framework + MySQL + Redis + Celery
- **AI Service**: Kimi K2.5 API (Moonshot AI)
