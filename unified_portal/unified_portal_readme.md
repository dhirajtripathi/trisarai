# Enterprise Unified Portal
**Usecase Name**: `unified_portal`

## 1. Functional Overview
The **Unified Portal** is the central "Launchpad" (Nexus OS) for the entire Agentic AI Suite. It solves the fragmentation problem by aggregating disparate AI tools (SQL Analysis, KYC, Claims, Code Migration) into a single, cohesive, role-based dashboard.

### Key Features
*   **Single Pane of Glass**: Instant access to 10+ AI Agents.
*   **Domain Filtering**: Toggle between Data Intelligence, Financial Services (FSI), and Developer Tools.
*   **Dynamic Routing**: Seamlessly links to locally running micro-frontends (MFEs).
*   **Enterprise Branding**: High-end "Nexus OS" aesthetic using Glassmorphism and Tailwind CSS.

## 2. Technical Architecture
The portal is designed as a **Micro-Frontend Orchestrator**.

### Core Components
1.  **React Host Application**:
    *   Built with `Vite` + `TailwindCSS`.
    *   Manages global routing and user session (future state).
2.  **Service Discovery**:
    *   Maintains a registry of available agents and their active ports (`http://localhost:5173`, etc.).
3.  **UI Component Library**:
    *   Uses `Lucide React` for iconography.
    *   Standardized "Agent Cards" with visual status indicators.

## 3. Implementation Steps

### Prerequisites
*   Node.js 18+

### Setup & Run
1.  **Navigate**: `cd unified_portal`
2.  **Install**: `npm install`
3.  **Start Dev Server**: `npm run dev`
4.  **Access**: `http://localhost:5173` (Port may vary if other apps are running)

### Adding a New Agent
To onboard a new tool to the portal, edit `src/App.jsx`:

```javascript
{
    title: "New Agent Name",
    description: "What it does...",
    icon: IconName,
    color: "color-name",
    domain: "fsi | dev | data",
    url: "http://localhost:PORT"
}
```

## 4. Agentic Considerations
While the portal itself is a UI, it acts as the **Control Plane** for the Agentic Ecosystem.
*   **Discovery**: It visually represents the "Tool Inventory" available to the organization.
*   **Access Control**: Future implementations will integrate SSO (Okta/Entra ID) to restrict agent access based on user role (e.g., only Developers see "Migration Agent").
