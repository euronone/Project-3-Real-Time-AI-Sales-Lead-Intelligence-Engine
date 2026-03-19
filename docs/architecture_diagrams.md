# SalesIQ Architecture Diagrams

This document contains Mermaid diagrams illustrating the architecture of the SalesIQ Real-Time AI Sales & Lead Intelligence Engine, based on the project documentation.

## 1. High-Level System Architecture

This diagram shows the major components of the system and how they interact.

```mermaid
flowchart TD
    %% Define Styles
    classDef frontend fill:#3b82f6,stroke:#1d4ed8,stroke-width:2px,color:#fff
    classDef backend fill:#10b981,stroke:#047857,stroke-width:2px,color:#fff
    classDef database fill:#f59e0b,stroke:#b45309,stroke-width:2px,color:#fff
    classDef external fill:#8b5cf6,stroke:#5b21b6,stroke-width:2px,color:#fff

    subgraph User Interface
        UI["Next.js Frontend<br/>(Admin + Agent UI)"]:::frontend
    end

    subgraph Backend Services
        API["FastAPI Server<br/>(REST + Auth)"]:::backend
        WS["Socket.IO Server<br/>(Real-Time Events)"]:::backend
        Workers["Celery Workers<br/>(AI Jobs)"]:::backend
    end

    subgraph Data & Message Broker
        DB[("PostgreSQL<br/>(Transactional Data)")]:::database
        Redis[("Redis<br/>(Cache & Pub/Sub)")]:::database
        S3[("AWS S3<br/>(Recording Storage)")]:::database
    end

    subgraph External APIs
        OpenAI["OpenAI API<br/>(GPT-4o & Whisper)"]:::external
        Twilio["Twilio Voice<br/>(Telephony & Streams)"]:::external
    end

    %% Connections
    UI <-->|REST API| API
    UI <-->|WebSocket| WS
    UI <-.->|Client SDK| Twilio

    API <-->|Read/Write| DB
    API <-->|Cache| Redis
    API -->|Enqueue Jobs| Redis
    
    WS <-->|Pub/Sub| Redis

    Redis -->|Dequeue Jobs| Workers
    Workers <-->|Read/Write| DB
    Workers -->|Save Files| S3

    API <-->|Analyze/Transcribe| OpenAI
    Workers <-->|Deep Analysis| OpenAI

    API <-->|Manage Calls| Twilio
    Twilio -->|Webhooks| API
    Twilio -->|Media Streams| WS
    Twilio -->|Audio Files| S3
```

## 2. Real-Time Call Flow

This sequence diagram illustrates the step-by-step data flow during a live sales call, highlighting the real-time AI guidance pipeline.

```mermaid
sequenceDiagram
    actor Agent
    participant UI as Next.js Frontend
    participant Twilio
    participant Backend as FastAPI / Socket.IO
    participant Redis as Redis Pub/Sub
    participant OpenAI
    
    Agent->>UI: Clicks "Call" on dashboard
    UI->>Twilio: Initiates outbound call (Twilio Client SDK)
    Twilio-->>Agent: Connects call to Customer
    
    activate Twilio
    note right of Twilio: Call is Active
    
    Twilio->>Backend: Starts Media Stream (Raw Audio via WebSocket)
    activate Backend
    
    loop Every Audio Chunk
        Backend->>OpenAI: Send audio chunk to Whisper API
        OpenAI-->>Backend: Return transcript chunk
        Backend->>OpenAI: Send transcript context to GPT-4o
        OpenAI-->>Backend: Return streaming analysis (sentiment, guidance)
        Backend->>Redis: Publish AI Guidance & Transcript
        Redis->>Backend: Route via Socket.IO
        Backend-->>UI: Push live updates (WebSocket)
        UI-->>Agent: Displays live transcript & AI suggestions
    end
    
    Agent->>UI: Ends Call
    UI->>Twilio: Hangs up
    deactivate Twilio
    
    Twilio->>Backend: Call Ended Webhook & Recording URL
    Backend->>Backend: Enqueue Celery Job for deep analysis
    deactivate Backend
```

## 3. Post-Call Analysis & Deal Prediction Flow

This diagram shows how offline Celery workers process the completed call recording and generate deal predictions.

```mermaid
flowchart LR
    classDef process fill:#f472b6,stroke:#be185d,stroke-width:2px,color:#fff
    classDef data fill:#6ee7b7,stroke:#059669,stroke-width:2px,color:#000
    classDef llm fill:#a78bfa,stroke:#4c1d95,stroke-width:2px,color:#fff

    Start([Call Ends]) --> Webhook[Twilio Webhook Received]

    subgraph Celery Task Pipeline
        direction TB
        Webhook --> Download[Download Recording from S3]:::process
        Download --> Transcribe[Full Batch Transcription<br/>(Whisper API)]:::process
        Transcribe --> Analyze[Deep Text Analysis<br/>(GPT-4o)]:::process
        
        Analyze --> Predict[Calculate Deal Prediction<br/>(GPT-4o)]:::process
    end

    subgraph Data Sources
        CRM[(Lead History &<br/>CRM Data)]:::data
        Transcript[(Full Call<br/>Transcript)]:::data
    end

    subgraph Final Outputs
        Summary[Call Summary<br/>& Scorecard]:::data
        Prediction[Win Probability %<br/>& Next Steps]:::data
    end

    Transcribe --> Transcript
    Transcript --> Analyze
    CRM --> Predict
    Analyze --> Predict
    
    Analyze --> Summary
    Predict --> Prediction
    
    Summary --> DB[(PostgreSQL)]
    Prediction --> DB
```
