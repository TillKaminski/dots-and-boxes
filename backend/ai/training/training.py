"""Handles command-line input and initiates the training process."""

import argparse

from ai.training.trainer import ModelTrainer


def main():
    """Parses command-line arguments and starts the model training."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--it",
        type=int,
        default=0,
        help="Number of epochs for training. Default: Uses the number defined in the configuration files.",
    )
    parser.add_argument("--src", type=str, default="", help="Source file of Training Data.")

    args = parser.parse_args()

    iterations = args.it if args.it > 0 else None

    if len(args.src) > 0:
        model = ModelTrainer(args.src)
    else:
        model = ModelTrainer()
    print(
        f"\n### Start Training ({iterations if iterations is not None else 'default'} Iterations) ###\n"
    )
    model.train(iterations)
    print("Training finished.")


if __name__ == "__main__":  # pragma: no cover
    main()
