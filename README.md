# AI Research Intelligence Agent

> **One query → comprehensive intelligence report.** Automated deep research powered by CrewAI + LLM, running on the Apify platform.

## What It Does

This Actor turns any research question into a structured, actionable intelligence report. Instead of spending hours searching, reading, and synthesizing, you get:

- **Executive Summary** — TL;DR with key takeaways
- **Key Findings** — Data points, trends, and facts
- **Market Landscape** — Competitors, players, positioning
- **Opportunities** — Actionable gaps and openings
- **Risks** — Threats, regulations, headwinds
- **Recommendations** — Clear next steps
- **Sources** — Every claim backed by a URL

## Perfect For

- 🏢 **Market Research** — Size a market, map competitors, find trends
- 💼 **Due Diligence** — Evaluate a company, technology, or investment
- 📊 **Competitive Intelligence** — Track what rivals are doing
- 📰 **News Monitoring** — Deep-dive into breaking stories
- 🎓 **Academic Research** — Literature review and synthesis
- 🚀 **Product Research** — Validate ideas before building

## How It Works (3-Step Pipeline)

```
1. SEARCH   → Google Search Scraper finds the most relevant sources
2. CRAWL    → Website Content Crawler extracts full text from top pages
3. ANALYZE  → CrewAI agent reads, synthesizes, and writes the report
```

## Input Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `query` | string | ✅ | — | Your research question (e.g., "AI chip market 2025") |
| `modelName` | string | ❌ | `gpt-4o-mini` | LLM model: `gpt-4o` (best quality) or `gpt-4o-mini` (faster/cheaper) |
| `depth` | string | ❌ | `standard` | Research depth: `quick` (light), `standard` (balanced), `deep` (comprehensive) |
| `maxSources` | integer | ❌ | `10` | Max sources to analyze (3–30) |
| `outputFormat` | string | ❌ | `structured` | Output format: `structured` (JSON) or `markdown` (formatted text) |

## Pricing (Pay Per Event)

| Event | Price | When Charged |
|-------|-------|--------------|
| Actor Start | **$0.15** | Every run (initialization + search) |
| Quick Research | **$0.40** | When depth = `quick` (5 results, 3 pages) |
| Standard Research | **$0.60** | When depth = `standard` (10 results, 7 pages) |
| Deep Research | **$0.90** | When depth = `deep` (20 results, 15 pages) |

**Example costs:**
- Quick fact-check: $0.55 (start + quick)
- Market snapshot: $0.75 (start + standard)
- Due diligence memo: $1.05 (start + deep)

## Output Example

```json
{
  "query": "AI chip market 2025",
  "depth": "deep",
  "model_used": "gpt-4o",
  "tokens_used": 4852,
  "report": {
    "executive_summary": "The AI chip market is projected to reach $200B by 2025...",
    "key_findings": [...],
    "market_landscape": [...],
    "opportunities": [...],
    "risks": [...],
    "recommendations": [...],
    "sources": [...]
  }
}
```

## Architecture

- **Framework:** [CrewAI](https://crewai.com) — multi-agent orchestration
- **Search:** [Google Search Scraper](https://apify.com/apify/google-search-scraper) — SERP extraction
- **Crawl:** [Website Content Crawler](https://apify.com/apify/website-content-crawler) — page text extraction
- **LLM:** OpenAI GPT-4o / GPT-4o-mini
- **Platform:** [Apify](https://apify.com) — serverless execution + monetization

## Development

```bash
# Clone and setup
git clone https://github.com/YOUR_USERNAME/ai-research-intelligence-agent.git
cd ai-research-intelligence-agent

# Install dependencies
pip install -r requirements.txt

# Run locally (requires APIFY_TOKEN env var)
APIFY_TOKEN=your_token_here python -m my_actor
```

## License

MIT — open source, free to fork and improve.

---

**Built with ❤️ by a solo developer using AI. Earn passive income on the [Apify Store](https://apify.com/store).**