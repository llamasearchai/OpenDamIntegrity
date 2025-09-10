# Configuration

Environment variables
- `LOG_LEVEL`: logging level (default `INFO`)
- `OPENAI_API_KEY`: enable OpenAI-backed responses
- `OAI_MODEL`: override model id (default `gpt-4o-mini`)
- `OAI_ASSISTANT_ID`: reuse an existing Assistant id
- `OAI_ASSISTANT_INSTRUCTIONS`: custom domain instructions
- `OAI_REQUEST_TIMEOUT_S`: timeout for Assistants polling (default 15.0)
- `ODI_API_KEY`: optional API key for all FastAPI endpoints
- SMTP: `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM`
- Twilio: `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_FROM`

Application config file
- Default at `config/opendamintegry.toml` for stability thresholds and feature toggles.

Data samples
- Found under `data/samples/` for InSAR, inclinometers, piezometers, and settlement plates.

