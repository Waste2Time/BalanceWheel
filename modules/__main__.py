"""Project-level module entrypoint.

Running ``python -m modules`` forwards to the pipeline CLI so users can
invoke the end-to-end MVP without remembering the submodule path.
"""

from modules.pipeline.__main__ import main as pipeline_main


def main() -> None:
    """Dispatch to the pipeline CLI."""
    pipeline_main()


if __name__ == "__main__":
    main()
