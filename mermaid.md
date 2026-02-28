# MAGI SYSTEM DIAGRAMS

All system diagrams in one file. Each chart shows one concept.

---

## DIAGRAM 1: MAIN FLOW (SIMPLE)

Question goes in. Three AIs think. Answer comes out.

```mermaid
flowchart LR
    subgraph IN["IN"]
        Q[Question]
    end

    subgraph THINK["THINK"]
        Q --> M[MELCHIOR]
        Q --> B[BALTHASAR]
        Q --> C[CASPER]
        M --> D{Agree?}
        B --> D
        C --> D
        D -->|No| R[Debate]
        R --> D
        D -->|Yes| F[Final Answer]
    end

    subgraph OUT["OUT"]
        F --> T[Terminal]
        F --> S[Speak]
        F --> DB[(Memory)]
    end
```

---

## DIAGRAM 2: MAIN FLOW (DETAILED)

Full system with voice input, memory retrieval, tool use.

```mermaid
flowchart TB
    subgraph INPUT["INPUT"]
        voice[Voice] --> transcribe[Transcribe]
        text[Text] --> question
        transcribe --> question[Question]
    end

    subgraph MAGI["MAGI SYSTEM"]
        question --> parallel

        subgraph parallel["PARALLEL QUERY"]
            direction LR
            M[MELCHIOR]
            B[BALTHASAR]
            C[CASPER]
        end

        parallel --> consensus{Agree?}
        consensus -->|Yes| synthesize
        consensus -->|No| debate[Debate Round]
        debate --> consensus
        synthesize[MELCHIOR Synthesizes]
    end

    subgraph OUTPUT["OUTPUT"]
        synthesize --> terminal[Terminal Display]
        synthesize --> speak[TTS Speak]
        synthesize --> store[Store to Memory]
    end

    subgraph SUPPORT["SUPPORT SYSTEMS"]
        direction LR
        memory[(Memory DB)]
        tools[Web Search]
    end

    question -.-> memory
    memory -.-> parallel
    parallel -.-> tools
    tools -.-> parallel
```

---

## DIAGRAM 3: LLM ARCHITECTURE

One model loaded. Three separate API calls. No cross-contamination.

```mermaid
flowchart TB
    subgraph PYTHON["PYTHON CODE"]
        direction LR
        MH[melchior_history]
        BH[balthasar_history]
        CH[casper_history]
    end

    subgraph API["API CALLS"]
        direction TB
        A1[Call 1: MELCHIOR_PROMPT]
        A2[Call 2: BALTHASAR_PROMPT]
        A3[Call 3: CASPER_PROMPT]
    end

    subgraph LMSTUDIO["LM STUDIO"]
        MODEL[Qwen3.5-35B-A3B]
    end

    MH --> A1
    BH --> A2
    CH --> A3
    
    A1 --> MODEL
    A2 --> MODEL
    A3 --> MODEL

    MODEL --> R1[Response 1]
    MODEL --> R2[Response 2]
    MODEL --> R3[Response 3]
```

---

## DIAGRAM 4: FILE STRUCTURE

Modular design. Like with like. Each box is a folder.

```mermaid
flowchart TB
    subgraph ENTRY["ENTRY"]
        main[main.py]
        config[config.txt]
    end

    subgraph CORE["CORE"]
        personalities[personalities.py]
        orchestrator[orchestrator.py]
        consensus[consensus.py]
        addressing[addressing.py]
    end

    subgraph LLM["LLM"]
        client[client.py]
        streaming[streaming.py]
        messages[messages.py]
        fallback[fallback.py]
    end

    subgraph MEMORY["MEMORY"]
        db[db.py]
        store[store.py]
        retrieve[retrieve.py]
        search[search.py]
    end

    subgraph VOICE["VOICE"]
        input[input.py]
        output[output.py]
        audio[audio.py]
    end

    subgraph UI["UI"]
        app[app.py]
        layout[layout.py]
        magi_panel[magi_panel.py]
        terminal[terminal_panel.py]
        vacant[vacant_panel.py]
        indicators[indicators.py]
        animations[animations.py]
    end

    subgraph TOOLS["TOOLS"]
        websearch[web_search.py]
        urlfetch[url_fetch.py]
    end

    main --> CORE
    main --> UI
    CORE --> LLM
    CORE --> MEMORY
    CORE --> TOOLS
    UI --> VOICE
```

---

## DIAGRAM 5: GUI LAYOUT

1200x700 fixed window. MAGI left (60%). Terminal and Vacant stacked right.

```mermaid
flowchart TB
    subgraph WINDOW["1200 x 700"]
        direction LR
        
        subgraph MAGI["MAGI 720x700"]
            direction TB
            MEL[MELCHIOR]
            HUB[MAGI HUB]
            CAS[CASPER]
            BAL[BALTHASAR]
            CTRL[Controls]
            
            MEL --> HUB
            HUB --> CAS
            HUB --> BAL
            CAS --> CTRL
            BAL --> CTRL
        end
        
        subgraph RIGHT["480x700"]
            direction TB
            TERM[TERMINAL 480x525]
            VAC[VACANT 480x175]
            
            TERM --> VAC
        end
        
        MAGI --> RIGHT
    end
```

---

## QUICK REFERENCE

| Diagram | Purpose |
|---------|---------|
| 1. Main Flow Simple | Overview of question-to-answer flow |
| 2. Main Flow Detailed | Full system with all components |
| 3. LLM Architecture | How one model serves three personalities |
| 4. File Structure | Modular code organization |
| 5. GUI Layout | Window layout and proportions |
