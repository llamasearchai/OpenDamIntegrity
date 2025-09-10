from open_dam_integry.llm.agents_service import AgentService


def test_agent_service_status_keys():
    svc = AgentService(api_key=None)
    st = svc.status()
    # Ensure expected keys exist and types are sane
    assert {
        "openai_imported",
        "client_initialized",
        "assistant_id_configured",
        "model",
        "timeout_s",
    }.issubset(st.keys())
    assert isinstance(st["client_initialized"], bool)
