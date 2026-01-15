# Dinneroo Data Types - Quick Reference

## How to read this diagram

```mermaid
flowchart TB
    subgraph SOURCES["📥 DATA SOURCES"]
        direction TB
        
        subgraph INTERNAL["🔵 INTERNAL (from our systems)"]
            direction LR
            A1["<b>Supply / Ground Truth</b><br/>anna_slides/*.csv<br/><i>What we HAVE</i><br/>✅ Quant"]
            A2["<b>Order History</b><br/>Snowflake 805K orders<br/><i>What customers DO</i><br/>✅ Quant"]
            A3["<b>Ratings + Comments</b><br/>Snowflake 10K ratings<br/><i>How they FEEL</i><br/>🟣 Mixed"]
            A4["<b>Menu Catalog</b><br/>Snowflake 65K items<br/><i>What's AVAILABLE</i><br/>✅ Quant"]
        end
        
        subgraph RESEARCH["🟠 RESEARCH (from surveys/interviews)"]
            direction LR
            B1["<b>Post-order Survey</b><br/>n=1,599 responses<br/><i>Satisfaction + open-text</i><br/>🟣 Mixed"]
            B2["<b>Dropoff Survey</b><br/>n=838 responses<br/><i>Barriers + unmet demand</i><br/>🟣 Mixed"]
            B3["<b>Customer Transcripts</b><br/>n=88 interviews<br/><i>The 'WHY' behind behavior</i><br/>🟡 Qual"]
        end
        
        subgraph LLM["🩷 LLM-DERIVED (AI-processed)"]
            L1["<b>Gemini Extraction</b><br/>transcript_mentions.json<br/><i>Structured mentions from qual</i><br/>🩷 Derived"]
        end
    end
    
    subgraph OUTPUTS["📤 WHAT YOU CAN DO WITH IT"]
        direction TB
        O1["Zone MVP status<br/><i>(which zones are ready?)</i>"]
        O2["Dish prioritization<br/><i>(what to recruit?)</i>"]
        O3["Gap analysis<br/><i>(what's missing?)</i>"]
        O4["Latent demand<br/><i>(what do customers want?)</i>"]
    end
    
    INTERNAL --> O1
    INTERNAL --> O2
    RESEARCH --> O3
    RESEARCH --> O4
    LLM --> O4

    classDef internal fill:#1e3a5f,stroke:#3b82f6,color:#fff
    classDef research fill:#4a3000,stroke:#f59e0b,color:#fff
    classDef llm fill:#4a1942,stroke:#ec4899,color:#fff
    classDef output fill:#1a2e1a,stroke:#22c55e,color:#fff
    
    class A1,A2,A3,A4 internal
    class B1,B2,B3 research
    class L1 llm
    class O1,O2,O3,O4 output
```

---

## Quick Legend

| Symbol | Meaning |
|--------|---------|
| ✅ **Quant** | Numbers, counts, metrics (can aggregate) |
| 🟡 **Qual** | Text, transcripts, context (rich but not countable) |
| 🟣 **Mixed** | Has both (e.g. survey with ratings + open-text) |
| 🩷 **Derived** | LLM turned qual into structured data |

| Source | What it means |
|--------|---------------|
| 🔵 **Internal** | From Deliveroo systems (Snowflake, Anna exports) |
| 🟠 **Research** | From surveys or customer interviews |
| 🩷 **LLM** | AI-processed (Gemini extraction with audit trail) |

---

## Key Rules

1. **Supply ≠ Performance** — Anna tells you what EXISTS, Snowflake tells you how it PERFORMS
2. **Never use OG Survey alone** — always triangulate with other sources
3. **LLM outputs are assistive** — use the audit trail, don't treat as ground truth
4. **Open-text is gold** — surveys have quant scores AND qual insights

---

## Common Questions → Which Data to Use

| Question | Primary Source | Why |
|----------|---------------|-----|
| "How many partners in Zone X?" | Anna supply data | Ground truth for supply |
| "What's the repeat rate?" | Snowflake orders | Revealed behavior |
| "Why do families drop off?" | Dropoff survey | Direct barrier questions |
| "What dishes do families want?" | Transcripts + LLM extraction | Unprompted mentions |
| "Is Zone X ready for launch?" | Zone MVP status (derived) | Combines multiple sources |

