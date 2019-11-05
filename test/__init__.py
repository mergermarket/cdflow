from hypothesis import settings, HealthCheck


settings.register_profile(
    "default",
    deadline=None,
    suppress_health_check=(HealthCheck.too_slow,))
settings.load_profile("default")
