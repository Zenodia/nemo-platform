# UI Package Agent Instructions

## About This Package

- Main React frontend application for NeMo Studio
- Built with React 18, TypeScript, Vite
- Handles user interfaces for model customization, evaluation, and deployment
- Integrates with backend APIs through generated SDK clients

## Design System

- **Use NVIDIA Foundations React as the primary design system** — preferred over custom components
- NVIDIA Foundations React provides consistent styling, accessibility, and user experience patterns
- Follow NVIDIA Foundations React's design tokens and theming system for consistent visual design
- Leverage NVIDIA Foundations React's built-in accessibility features and ARIA patterns

## Key Dependencies

- **NVIDIA Foundations React** (@nvidia/foundations-react-core) — Primary component library
- **TanStack Query** — Data fetching and caching
- **React Hook Form + Zod** — Form handling and validation
- **React Router 6** — Client-side routing

## Import Path Rules

- **Never use relative imports** — always use absolute imports
- Import path mappings:
  - `@studio/` → `packages/studio/src/`
  - `@e2e-tests/` → `packages/studio/e2e-tests/`
- Other local packages are imported via pnpm workspaces
