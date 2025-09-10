# CLI Reference

Entry point: `odintegry`

Common commands
- `odintegry version`: print package version
- `odintegry stability --c-kpa 8 --phi-deg 30 --beta-deg 18 --height-m 15 --gamma-k-n-m3 18.5 --ru 0.15`: compute factor of safety and risk band
- `odintegry visualize --output outputs/dam_surface.png`: render a 3D dam surface image
- `odintegry report`: generate an HTML report in `outputs/`
- `odintegry agent "Summarize current dam stability considerations"`: ask the assistant
- `odintegry agent-status`: print LLM configuration and status without network calls
- `odintegry api --host 0.0.0.0 --port 8000`: run the FastAPI service
- `odintegry smoke`: run a quick end-to-end smoke check

Environment
- Copy `.env.example` to `.env` and set values as needed.
- For LLM-backed features, set `OPENAI_API_KEY`.

