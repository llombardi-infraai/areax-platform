# Area X Frontend

React + TypeScript frontend for the Area X platform.

## Tech Stack

- React 18
- TypeScript
- Vite
- Tailwind CSS
- React Router 6
- TanStack Query (React Query)
- Zustand (state management)
- Radix UI
- Axios

## Development

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Environment Variables

Create a `.env` file:

```env
VITE_CONTROL_API_URL=http://localhost:8080/v1
VITE_TENANT_API_URL=http://localhost:8081/v1
```

## Features

- Authentication with MFA
- Workspace & Project management
- AI Advisor (Chat + Blueprint Builder)
- Security Center
- Data Control
- Knowledge Base
- Connector management
- Notifications

## Docker

```bash
docker build -t areax-frontend .
docker run -p 5173:80 areax-frontend
```
