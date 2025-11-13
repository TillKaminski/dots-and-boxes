"""Handles Terminal Input and initiates Training Process."""

import argparse

from ai.training.trainer import ModelTrainer


def main(it: int = 100):
    """Handles User Input."""
    model = ModelTrainer()
    print("TODO: Implement Training.")
    print(f"\n### Start Training ({it} Iterations) ###\n")
    model.train()
    print("Training finished.")


if __name__ == "__main__":  # pragma: no cover

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--it", type=int, default=100, help="Train Model. Default: 100 Iterations."
    )
    args = parser.parse_args()

    main(args.it)
