def test_sentry_disabled_does_not_open_network(monkeypatch):
    import src.observability as observability

    monkeypatch.setenv("SENTRY_DSN", "")

    def fail_socket(*args, **kwargs):
        raise AssertionError("network access should be disabled")

    monkeypatch.setattr("socket.socket", fail_socket)
    observability.init_sentry()
    with observability.span("disabled"):
        pass
