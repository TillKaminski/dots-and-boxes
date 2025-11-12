"""Handles Terminal Input and initiates Training Process."""

import argparse

from ai.training.trainer import ModelTrainer


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--it", type=int, default=100, help="Train Model. Default: 100 Iterations."
    )
    args = parser.parse_args()

    model = ModelTrainer()

    print("TODO: Implement Training.")
    print(f"\n### Start Training ({args.it} Iterations) ###\n")

    model.train()

    print("Training finished.")
