# 📐 System Diagrams for SynTwin Project

This document contains comprehensive system diagrams using Mermaid syntax for the SynTwin project.

## System Architecture Diagram

```mermaid
graph TB
    subgraph "Frontend Layer"
        A[React UI] --> B[WebSocket Client]
        A --> C[HTTP Client]
        A --> D[Chart.js Visualization]
    end
    
    subgraph "API Gateway"
        E[FastAPI Server] --> F[REST Endpoints]
        E --> G[WebSocket Handler]
        E --> H[CORS Middleware]
    end
    
    subgraph "Service Layer"
        I[Detection Service]
        J[NLP Service]
        K[Analytics Service]
        L[State Service]
        M[Stream Service]
    end
    
    subgraph "Business Logic Layer"
        N[Combined Detector]
        O[Emotion Detector]
        P[Posture Detector]
        Q[Eye Tracker]
        R[Smile Detector]
        
        S[Sentiment Analyzer]
        T[Task Recommender]
        U[Intent Recognizer]
        
        V[State Classifier]
        W[Mood Classifier]
        
        X[Data Analyzer]
        Y[Plotter]
    end
    
    subgraph "Data Layer"
        Z[SQLAlchemy ORM]
        AA[Database Logger]
        AB[CSV Logger]
        AC[SQLite/PostgreSQL]
        AD[CSV Files]
    end
    
    subgraph "External Resources"
        AE[OpenCV Haar Cascades]
        AF[MediaPipe Models]
        AG[DistilBERT Model]
        AH[Webcam Input]
    end
    
    %% Frontend to API
    B --> G
    C --> F
    
    %% API to Services
    F --> I
    F --> J
    F --> K
    F --> L
    G --> M
    
    %% Services to Business Logic
    I --> N
    N --> O
    N --> P
    N --> Q
    N --> R
    
    J --> S
    J --> T
    J --> U
    
    L --> V
    L --> W
    
    K --> X
    K --> Y
    
    %% Business Logic to Data
    N --> AA
    N --> AB
    X --> Z
    Y --> Z
    
    %% Data to Storage
    Z --> AC
    AA --> AC
    AB --> AD
    
    %% External Resources
    O --> AE
    P --> AF
    Q --> AE
    R --> AE
    S --> AG
    O --> AH
    P --> AH
    Q --> AH
    R --> AH
    
    %% Styling
    classDef frontend fill:#e1f5ff,stroke:#01579b,stroke-width:2px
    classDef api fill:#fff9c4,stroke:#f57f17,stroke-width:2px
    classDef service fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef logic fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px
    classDef data fill:#fce4ec,stroke:#880e4f,stroke-width:2px
    classDef external fill:#ffebee,stroke:#b71c1c,stroke-width:2px
    
    class A,B,C,D frontend
    class E,F,G,H api
    class I,J,K,L,M service
    class N,O,P,Q,R,S,T,U,V,W,X,Y logic
    class Z,AA,AB,AC,AD data
    class AE,AF,AG,AH external
```

## Data Flow Diagrams (Leveled)

### Level 0 – Context
```mermaid
flowchart TD
    User([User]) -->|Webcam + UI| System[SynTwin System]
    System -->|Real-time feedback| User
    System -->|Tasks & insights| User

    subgraph External Inputs
        Webcam[Webcam Video]
    end

    Webcam --> System
```

### Level 1 – Major Subsystems
```mermaid
flowchart TD
    User([User]) --> UI[Frontend UI]
    UI -->|WebSocket/HTTP| API[FastAPI Gateway]
    API --> DetectSvc[Detection Service]
    API --> NLPSvc[NLP Service]
    API --> AnalyticsSvc[Analytics Service]
    API --> StreamSvc[Stream Service]

    DetectSvc --> Detectors[Combined Detector]
    Detectors --> DataStores[(DB/CSV Logs)]
    Detectors --> WS[WebSocket Broadcast]
    Detectors --> StateClass[State Classifier]

    NLPSvc --> Recommender[Task Recommender]
    Recommender --> UI

    AnalyticsSvc --> Charts[Chart Data]
    Charts --> UI

    WS --> UI
    DataStores --> AnalyticsSvc
```

### Level 2 – Detailed Flow (Final)
```mermaid
flowchart TD
    Start([User at Desk]) --> Webcam[Webcam Captures Frame]
    Webcam --> CombinedDet{Combined Detector}

    CombinedDet --> FaceDetect[Face Detection<br/>Haar]
    CombinedDet --> EmotionAnalysis[Emotion Analysis<br/>Features]
    CombinedDet --> PostureEst[Posture Estimation<br/>MediaPipe]
    CombinedDet --> EyeTrack[Eye Tracking<br/>EAR]
    CombinedDet --> SmileDetect[Smile Detection<br/>Mouth]

    FaceDetect --> Merge{Merge Results}
    EmotionAnalysis --> Merge
    PostureEst --> Merge
    EyeTrack --> Merge
    SmileDetect --> Merge

    Merge --> DetectionResult[DetectionResult<br/>emotion, posture, eyes, smile, ts]
    DetectionResult --> Parallel{Parallel Processing}

    Parallel --> DBLogger[(DB Logger)]
    Parallel --> CSVLogger[(CSV Logger)]
    Parallel --> WSStream[WebSocket Stream]
    Parallel --> StateClass[State Classifier]

    DBLogger --> Storage1[(SQLite/PostgreSQL)]
    CSVLogger --> Storage2[(logs/syntwin_log.csv)]

    WSStream --> Frontend1[Frontend Receives Update]
    Frontend1 --> UIUpdate1[UI Updates in Real-Time]

    StateClass --> SentimentAnalyzer[Sentiment Analyzer<br/>DistilBERT]
    SentimentAnalyzer --> NLPEngine[NLP Engine<br/>State Summary]
    NLPEngine --> TaskRec[Task Recommender<br/>Random Forest]
    TaskRec --> TaskDB[(Task Database)]
    TaskDB --> RankTasks[Rank & Score Tasks]
    RankTasks --> TopTasks[Top 5 Tasks]
    TopTasks --> Frontend2[Task Suggestions UI]

    Storage1 --> Analytics[Analytics Service]
    Analytics --> Charts[Charts Data]
    Charts --> Frontend3[Analytics Dashboard]

    %% Styling
    classDef input fill:#e1f5ff,stroke:#01579b,stroke-width:2px
    classDef process fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px
    classDef storage fill:#fce4ec,stroke:#880e4f,stroke-width:2px
    classDef output fill:#fff9c4,stroke:#f57f17,stroke-width:2px
    classDef decision fill:#f3e5f5,stroke:#4a148c,stroke-width:2px

    class Start,Webcam input
    class CombinedDet,Merge,Parallel decision
    class FaceDetect,EmotionAnalysis,PostureEst,EyeTrack,SmileDetect,DetectionResult,StateClass,SentimentAnalyzer,NLPEngine,TaskRec,RankTasks,TopTasks,Analytics,Charts process
    class DBLogger,CSVLogger,Storage1,Storage2,TaskDB storage
    class WSStream,Frontend1,UIUpdate1,Frontend2,Frontend3 output
```

## Use Case Diagram

```mermaid
graph LR
    subgraph "Actors"
        User((User))
        System((System/AI))
        Admin((Administrator))
    end
    
    subgraph "Detection Use Cases"
        UC1[Start Webcam Detection]
        UC2[Stop Detection]
        UC3[View Real-Time Emotions]
        UC4[Monitor Posture]
        UC5[Track Eye Status]
        UC6[Detect Fatigue]
    end
    
    subgraph "Task Management Use Cases"
        UC7[Request Task Suggestions]
        UC8[View Personalized Tasks]
        UC9[Filter Tasks by Category]
        UC10[Mark Task Complete]
        UC11[Add Custom Tasks]
    end
    
    subgraph "Analytics Use Cases"
        UC12[View Emotion Trends]
        UC13[Analyze Posture Quality]
        UC14[Check Sentiment History]
        UC15[Generate Reports]
        UC16[Export Data to CSV]
        UC17[View Productivity Patterns]
    end
    
    subgraph "State Analysis Use Cases"
        UC18[Classify Current State]
        UC19[Assess Mood Category]
        UC20[Calculate Energy Level]
        UC21[Determine Focus Quality]
        UC22[Predict Optimal Work Times]
    end
    
    subgraph "Configuration Use Cases"
        UC23[Configure Detection Settings]
        UC24[Manage Database]
        UC25[Clear Detection History]
        UC26[Adjust Alert Thresholds]
        UC27[Update AI Models]
    end
    
    %% User interactions
    User --> UC1
    User --> UC2
    User --> UC3
    User --> UC4
    User --> UC5
    User --> UC7
    User --> UC8
    User --> UC9
    User --> UC10
    User --> UC11
    User --> UC12
    User --> UC13
    User --> UC14
    User --> UC15
    User --> UC16
    User --> UC17
    
    %% System automatic processes
    System --> UC6
    System --> UC18
    System --> UC19
    System --> UC20
    System --> UC21
    System --> UC22
    
    %% Admin operations
    Admin --> UC23
    Admin --> UC24
    Admin --> UC25
    Admin --> UC26
    Admin --> UC27
    
    %% Dependencies (extends/includes)
    UC1 -.->|extends| UC3
    UC1 -.->|extends| UC4
    UC1 -.->|extends| UC5
    UC7 -.->|includes| UC18
    UC7 -.->|includes| UC19
    UC8 -.->|includes| UC20
    UC12 -.->|requires| UC1
    UC15 -.->|includes| UC12
    UC15 -.->|includes| UC13
    UC15 -.->|includes| UC14
    
    %% Styling
    classDef actor fill:#ffeb3b,stroke:#f57f00,stroke-width:3px
    classDef detection fill:#e1f5ff,stroke:#01579b,stroke-width:2px
    classDef task fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px
    classDef analytics fill:#fce4ec,stroke:#880e4f,stroke-width:2px
    classDef state fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef config fill:#fff9c4,stroke:#f57f17,stroke-width:2px
    
    class User,System,Admin actor
    class UC1,UC2,UC3,UC4,UC5,UC6 detection
    class UC7,UC8,UC9,UC10,UC11 task
    class UC12,UC13,UC14,UC15,UC16,UC17 analytics
    class UC18,UC19,UC20,UC21,UC22 state
    class UC23,UC24,UC25,UC26,UC27 config
```

## Sequence Diagram - Real-Time Detection Flow

```mermaid
sequenceDiagram
    actor User
    participant Frontend
    participant WebSocket
    participant FastAPI
    participant CombinedDetector
    participant Webcam
    participant DBLogger
    participant StateClassifier
    
    User->>Frontend: Click "Start Detection"
    Frontend->>WebSocket: Connect to ws://localhost:8000/ws/detection
    WebSocket-->>Frontend: Connection Established
    
    Frontend->>FastAPI: POST /api/detection/start
    FastAPI->>CombinedDetector: Initialize Detectors
    CombinedDetector->>Webcam: Open Camera (cv2.VideoCapture)
    Webcam-->>CombinedDetector: Camera Ready
    
    loop Every Frame (30 FPS)
        CombinedDetector->>Webcam: Read Frame
        Webcam-->>CombinedDetector: Frame Data
        
        par Parallel Detection
            CombinedDetector->>CombinedDetector: Face Detection (Haar)
            CombinedDetector->>CombinedDetector: Emotion Analysis
            CombinedDetector->>CombinedDetector: Posture Detection (MediaPipe)
            CombinedDetector->>CombinedDetector: Eye Tracking
            CombinedDetector->>CombinedDetector: Smile Detection
        end
        
        CombinedDetector->>CombinedDetector: Merge Results
        CombinedDetector->>FastAPI: DetectionResult Object
        
        par Parallel Processing
            FastAPI->>DBLogger: Async Log to Database
            DBLogger->>DBLogger: Insert Detection Record
            
            FastAPI->>StateClassifier: Classify State
            StateClassifier-->>FastAPI: State Analysis Result
            
            FastAPI->>WebSocket: Broadcast Detection Update
        end
        
        WebSocket-->>Frontend: {emotion, posture, eyes, smile, sentiment}
        Frontend->>Frontend: Update UI Components
        Frontend-->>User: Display Real-Time Data
    end
    
    User->>Frontend: Click "Stop Detection"
    Frontend->>FastAPI: POST /api/detection/stop
    FastAPI->>CombinedDetector: Stop Detection
    CombinedDetector->>Webcam: Release Camera
    WebSocket->>Frontend: Close Connection
    Frontend-->>User: Detection Stopped
```

## Sequence Diagram - Task Recommendation Flow

```mermaid
sequenceDiagram
    actor User
    participant Frontend
    participant FastAPI
    participant NLPService
    participant Database
    participant SentimentAnalyzer
    participant TaskRecommender
    participant RandomForest
    
    User->>Frontend: Click "Refresh Suggestions"
    Frontend->>FastAPI: GET /api/nlp/suggestions
    
    FastAPI->>NLPService: Request Task Suggestions
    NLPService->>Database: Query Recent Detections (last 10 min)
    Database-->>NLPService: Detection Records []
    
    NLPService->>NLPService: Calculate Statistics
    Note over NLPService: - Dominant emotion<br/>- Average sentiment<br/>- Posture quality %<br/>- Fatigue indicators
    
    NLPService->>SentimentAnalyzer: Analyze Combined State
    SentimentAnalyzer->>SentimentAnalyzer: Load DistilBERT Model
    SentimentAnalyzer->>SentimentAnalyzer: Generate State Text
    Note over SentimentAnalyzer: "User is Happy with<br/>Good posture at 10:45 AM"
    
    SentimentAnalyzer->>SentimentAnalyzer: Tokenize & Process
    SentimentAnalyzer-->>NLPService: Sentiment Score (+0.85)
    
    NLPService->>TaskRecommender: Request Recommendations
    Note over TaskRecommender: Input Features:<br/>- Energy: High<br/>- Mood: Positive<br/>- Focus: Good<br/>- Time: Morning
    
    TaskRecommender->>TaskRecommender: Filter Task Database
    Note over TaskRecommender: 6 Categories:<br/>work, personal, learning,<br/>social, health, creative
    
    TaskRecommender->>RandomForest: Classify & Score Tasks
    RandomForest->>RandomForest: Feature Extraction
    RandomForest->>RandomForest: Tree Voting (100 trees)
    RandomForest-->>TaskRecommender: Task Scores []
    
    TaskRecommender->>TaskRecommender: Rank by Score
    TaskRecommender->>TaskRecommender: Select Top 5
    TaskRecommender-->>NLPService: Recommended Tasks []
    
    NLPService->>NLPService: Generate Context Message
    Note over NLPService: "High energy detected!<br/>Focused work recommended"
    
    NLPService-->>FastAPI: {tasks[], context, state}
    FastAPI-->>Frontend: JSON Response
    
    Frontend->>Frontend: Parse Response
    Frontend->>Frontend: Update Task List UI
    Frontend-->>User: Display 5 Personalized Tasks
    
    alt User Completes Task
        User->>Frontend: Mark Task Complete
        Frontend->>FastAPI: POST /api/tasks/complete
        FastAPI->>Database: Log Task Completion
        Database-->>FastAPI: Success
        FastAPI-->>Frontend: Updated Status
        Frontend-->>User: Task Marked Complete ✓
    end
```

## Component Interaction Diagram

```mermaid
graph TB
    subgraph "Frontend Components"
        A[App.jsx<br/>State Container]
        B[Header]
        C[ServerStatus]
        D[DetectionControl]
        E[VideoFeed]
        F[DetectionInfo]
        G[TaskSuggestions]
        H[StateAnalysis]
        I[AnalyticsDashboard]
        J[Charts]
        K[useWebSocket Hook]
    end
    
    subgraph "Backend Services"
        L[Detection Service]
        M[NLP Service]
        N[Analytics Service]
        O[State Service]
        P[Stream Service]
    end
    
    subgraph "Data Flow"
        Q[(Database)]
        R[CSV Logs]
        S[WebSocket Events]
    end
    
    %% Frontend Internal
    A --> B
    A --> C
    A --> D
    A --> E
    A --> F
    A --> G
    A --> H
    A --> I
    A --> J
    A --> K
    
    %% Frontend to Backend
    D -->|POST /api/detection/start| L
    D -->|POST /api/detection/stop| L
    G -->|GET /api/nlp/suggestions| M
    H -->|GET /api/nlp/state| M
    I -->|GET /api/analytics/summary| N
    J -->|GET /api/analytics/patterns| N
    K <-->|WebSocket| P
    
    %% Backend Services Interaction
    L --> O
    M --> O
    N --> O
    
    %% Backend to Data
    L --> Q
    L --> R
    M --> Q
    N --> Q
    P --> S
    
    %% Data to Frontend
    Q -.-> N
    R -.-> N
    S -.-> K
    
    %% Styling
    classDef frontend fill:#e1f5ff,stroke:#01579b,stroke-width:2px
    classDef backend fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px
    classDef data fill:#fce4ec,stroke:#880e4f,stroke-width:2px
    
    class A,B,C,D,E,F,G,H,I,J,K frontend
    class L,M,N,O,P backend
    class Q,R,S data
```

## State Machine Diagram - User State Transitions

```mermaid
stateDiagram-v2
    [*] --> Neutral: System Start
    
    Neutral --> Focused: High energy + Positive mood + Good posture
    Neutral --> Drowsy: Fatigue signs + Low energy
    Neutral --> Stressed: Negative emotions + Tension
    Neutral --> Energetic: High positivity + Alert
    
    Focused --> Drowsy: Extended focus + Eye fatigue
    Focused --> Stressed: Pressure + Negative emotions
    Focused --> Energetic: Task completion + Positive mood
    Focused --> Neutral: Break taken
    
    Drowsy --> Neutral: Rest + Recovery
    Drowsy --> Stressed: Continued work while fatigued
    Drowsy --> [*]: System Stop
    
    Stressed --> Neutral: Relaxation + Mood improvement
    Stressed --> Drowsy: Mental exhaustion
    Stressed --> Focused: Problem resolution
    
    Energetic --> Focused: Task engagement
    Energetic --> Neutral: Energy decrease
    Energetic --> Stressed: Overexertion
    
    state Focused {
        [*] --> DeepWork
        DeepWork --> FlowState: Sustained concentration
        FlowState --> DeepWork: Brief interruption
    }
    
    state Drowsy {
        [*] --> MildFatigue
        MildFatigue --> Exhausted: Continued strain
        Exhausted --> [*]: Rest required
    }
    
    note right of Focused
        Recommended Actions:
        - Complex problem-solving
        - Creative work
        - Important decisions
    end note
    
    note right of Drowsy
        Recommended Actions:
        - Take a break
        - Light tasks only
        - Physical movement
    end note
    
    note right of Stressed
        Recommended Actions:
        - Breathing exercises
        - Simple routine tasks
        - Social interaction
    end note
    
    note right of Energetic
        Recommended Actions:
        - Physical activities
        - Social engagement
        - Learning new skills
    end note
```

## Deployment Diagram

```mermaid
graph TB
    subgraph "User Device"
        Browser[Web Browser<br/>Chrome/Firefox/Edge]
        Webcam[Webcam Device<br/>Video Input]
    end
    
    subgraph "Development Environment"
        Vite[Vite Dev Server<br/>Port 5173]
        Uvicorn[Uvicorn Server<br/>Port 8000]
        SQLite[(SQLite Database<br/>syntwin.db)]
        CSV[(CSV Logs<br/>logs/syntwin_log.csv)]
    end
    
    subgraph "Production Environment"
        subgraph "Web Server"
            Nginx[Nginx<br/>Reverse Proxy<br/>Port 80/443]
        end
        
        subgraph "Application Server"
            Gunicorn[Gunicorn + Uvicorn<br/>4 Workers<br/>Port 8000]
            
            Worker1[Worker 1<br/>FastAPI Instance]
            Worker2[Worker 2<br/>FastAPI Instance]
            Worker3[Worker 3<br/>FastAPI Instance]
            Worker4[Worker 4<br/>FastAPI Instance]
        end
        
        subgraph "Database Layer"
            PostgreSQL[(PostgreSQL<br/>Production DB<br/>Port 5432)]
            Redis[(Redis Cache<br/>Session Storage<br/>Port 6379)]
        end
        
        subgraph "Storage"
            FileSystem[File System<br/>Logs & Models]
            S3[AWS S3<br/>Backups<br/>Optional]
        end
    end
    
    subgraph "Docker Deployment"
        DockerCompose[Docker Compose<br/>Orchestration]
        
        ContainerFrontend[Frontend Container<br/>Nginx Alpine]
        ContainerBackend[Backend Container<br/>Python 3.12]
        ContainerDB[Database Container<br/>PostgreSQL 15]
    end
    
    subgraph "External Services"
        HuggingFace[Hugging Face<br/>Model Hub<br/>DistilBERT]
        MediaPipe[Google MediaPipe<br/>Pose Models]
    end
    
    %% Development connections
    Browser -->|HTTP/WS| Vite
    Browser -->|API Calls| Uvicorn
    Vite -->|Proxy| Uvicorn
    Uvicorn --> SQLite
    Uvicorn --> CSV
    Browser --> Webcam
    
    %% Production connections
    Browser -->|HTTPS| Nginx
    Nginx -->|Proxy Pass| Gunicorn
    Gunicorn --> Worker1
    Gunicorn --> Worker2
    Gunicorn --> Worker3
    Gunicorn --> Worker4
    
    Worker1 --> PostgreSQL
    Worker2 --> PostgreSQL
    Worker3 --> PostgreSQL
    Worker4 --> PostgreSQL
    
    Worker1 --> Redis
    Worker2 --> Redis
    Worker3 --> Redis
    Worker4 --> Redis
    
    Worker1 --> FileSystem
    FileSystem --> S3
    
    %% Docker connections
    DockerCompose --> ContainerFrontend
    DockerCompose --> ContainerBackend
    DockerCompose --> ContainerDB
    
    ContainerBackend --> ContainerDB
    Browser -->|HTTP| ContainerFrontend
    ContainerFrontend -->|Proxy| ContainerBackend
    
    %% External services
    Uvicorn -.->|Download Models| HuggingFace
    Uvicorn -.->|Download Models| MediaPipe
    Worker1 -.->|Model Updates| HuggingFace
    Worker1 -.->|Model Updates| MediaPipe
    
    %% Styling
    classDef client fill:#e1f5ff,stroke:#01579b,stroke-width:2px
    classDef dev fill:#fff9c4,stroke:#f57f17,stroke-width:2px
    classDef prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px
    classDef docker fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef external fill:#ffebee,stroke:#b71c1c,stroke-width:2px
    classDef storage fill:#fce4ec,stroke:#880e4f,stroke-width:2px
    
    class Browser,Webcam client
    class Vite,Uvicorn,SQLite,CSV dev
    class Nginx,Gunicorn,Worker1,Worker2,Worker3,Worker4 prod
    class PostgreSQL,Redis,FileSystem,S3 storage
    class DockerCompose,ContainerFrontend,ContainerBackend,ContainerDB docker
    class HuggingFace,MediaPipe external
```

---

## 📊 Diagram Legend

### Color Coding

- **Blue** 🔵: Frontend components and user-facing elements
- **Green** 🟢: Backend services and business logic
- **Pink** 🔴: Data storage and persistence layer
- **Yellow** 🟡: API and communication layers
- **Purple** 🟣: Decision points and state management
- **Red** 🔴: External services and dependencies

### Diagram Types Explained

1. **System Architecture Diagram**: Shows the overall structure and how major components interact across all layers
2. **Data Flow Diagram**: Illustrates the complete journey of data from webcam capture to UI display
3. **Use Case Diagram**: Depicts all possible user, system, and admin interactions with the application
4. **Sequence Diagrams**: Detail the step-by-step chronological flow of two critical operations:
   - Real-time detection and WebSocket streaming
   - AI-powered task recommendation generation
5. **Component Interaction Diagram**: Shows the relationships and data flow between frontend React components and backend services
6. **State Machine Diagram**: Represents possible user state transitions based on detected emotions, posture, and fatigue
7. **Deployment Diagram**: Visualizes the complete deployment architecture for development, production, and Docker environments

### How to Use These Diagrams

- **For Development**: Use architecture and component diagrams to understand code organization
- **For Documentation**: Include relevant diagrams in technical specifications
- **For Presentations**: Use data flow and use case diagrams to explain functionality
- **For Onboarding**: Help new developers understand system design with sequence diagrams
- **For DevOps**: Reference deployment diagram for infrastructure setup

---

**Note**: These diagrams are created using Mermaid syntax and will render beautifully in:
- GitHub README files
- GitLab markdown
- VS Code with Mermaid extension
- Documentation sites (MkDocs, Docusaurus, etc.)
- Notion, Confluence, and other modern documentation platforms
