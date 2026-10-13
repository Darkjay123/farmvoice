# FarmVoice Architecture

## Flow

Officer request (WhatsApp voice note or text)
  -> intake (planned: Whisper-class STT; this build: text)
  -> LangGraph planning agent
       -> MCP tools (own server):
            get_rainfall      Open-Meteo ERA5 archive (CHIRPS-class), zone-aware
            get_prices        WFP food prices via HDX CKAN (open data)
            get_plot_history  consent-gated SQLite household store
       -> borrowed MCP server: document parsing (crop calendars, ministry circulars)
  -> draft_advisory (citation-backed draft, structured log entry)
  -> HUMAN APPROVAL GATE (LangGraph interrupt + server-side token check)
  -> officer sends to farmer

## Components

- Agents: one planning agent (LangGraph state graph: plan -> gather -> approval_gate -> send).
- LLMs: any tool-calling LLM; the full task runs on an open-weights model (Qwen-class) with a frontier model optional alongside.
- Memory: per-session scratch state in the graph; plot history in SQLite as the long-term store (consent-gated).
- Tools/MCP: own FastMCP server, four tools, streamable HTTP + stdio; one borrowed community document-parsing MCP server.
- Human-in-the-loop: interrupt node raises unless `officer_approval` is set; `draft_advisory` additionally refuses without an `APPR-` token, so approval survives graph restarts.
- Observability: every tool call and advisory draft logged (tool, args, out, timestamp) to `data/tool_log.jsonl`.

## Data sources

Open-Meteo ERA5 archive (rainfall, no key), WFP food prices on HDX (open data, no key), synthetic consent-gated household records (no personal data). CHIRPS/TAMSAT direct integration on the roadmap.

## Diagram

See farmvoice_architecture.pdf (submitted with the application).
