__all__ = ["PipelineConfig", "run_pipeline"]


def __getattr__(name: str):
    if name in __all__:
        from . import run as _run  # lazy import to avoid runpy warnings

        return getattr(_run, name)
    raise AttributeError(f"module 'modules.pipeline' has no attribute {name!r}")
