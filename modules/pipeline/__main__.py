"""Pipeline package entrypoint for running the MVP end-to-end."""

from .run import _parse_args, run_pipeline


def main() -> None:
    """Parse CLI arguments and execute the pipeline."""
    run_pipeline(_parse_args())


if __name__ == "__main__":
    main()
