# FarmVoice

An agentic AI assistant for agricultural extension officers in Africa. An officer sends a request (voice note or text in the field), the agent gathers evidence (rainfall, market prices, plot history) and drafts a citation-backed advisory. Nothing reaches the farmer until a named officer approves it.

## Problem statement

Across much of Sub-Saharan Africa one extension officer covers thousands of farming households. Advice is slow, generic and rarely grounded in current data, while rainfall and market prices change weekly. Farmers act on guesswork; officers have no time to gather evidence per case.

## Solution overview

FarmVoice turns each officer request into a multi-step agentic workflow: plan, gather evidence from real open data sources, draft, human approval, send. The officer stays the decision point by design.

## Target users

Agricultural extension officers and the farming households they serve, starting in Nigeria.

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md). LangGraph orchestrates a planning agent that calls MCP tools; a mandatory interrupt node holds the advisory until an officer approval token is supplied.

## Setup

```
pip install -r requirements.txt
python data/seed_households.py        # consent-gated synthetic demo data
python -m mcp_server.server           # runs the MCP server on stdio
```

## Usage

Call the MCP tools `get_rainfall`, `get_prices`, `get_plot_history`, `draft_advisory` from any MCP client (Claude Desktop, LangGraph, your own client). `draft_advisory` refuses to run without an officer approval token.

## Technology stack

Python, MCP Python SDK (FastMCP), LangGraph, SQLite, Open-Meteo ERA5 archive (rainfall), WFP food prices via the HDX CKAN API. Whisper-class STT planned for the voice-note front end.

## Agent architecture

Planning agent decomposes the officer request into tool calls, executes them with logged results, then drafts. Per-session short-term memory; plot history acts as long-term store. Full detail in ARCHITECTURE.md.

## MCP implementation

One own MCP server (this repo) exposing four tools; one borrowed community MCP server for document parsing (crop calendars, circulars). Tools are exposed over stdio and streamable HTTP; any MCP client can call them.

## MCP tools/servers

- `get_rainfall(lat, lon, days)` - CHIRPS-class open rainfall archive, zone-aware
- `get_prices(commodity, admin1, limit)` - WFP market prices, open data
- `get_plot_history(plot_id, consent)` - consent-gated household plot records
- `draft_advisory(plot_id, officer_id, approval_token, ...)` - refuses without a human approval token, logs inputs/outputs/timestamps

## Human-in-the-loop workflow

Every irreversible step carries an approval gate: the LangGraph interrupt node raises unless a named officer approved, and `draft_advisory` checks the token server-side before generating. All tool calls are logged to `data/tool_log.jsonl`.

## Limitations

Synthetic household data for the demo; CHIRPS/TAMSAT direct feeds pending (Open-Meteo ERA5 stands in, same open-archive class); voice-note transcription not wired in this build; price coverage currently Nigeria only.

## Future improvements

Direct CHIRPS/TAMSAT + WFP datamart ingestion, SMS/USSD fallback, more languages (Pidgin, Yoruba, Igbo, Hausa first), officer dashboard, more countries.

## Licence

MIT. Open source, open data, no keys required to run the demo.
