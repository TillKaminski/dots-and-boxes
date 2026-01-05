"""Provides Bot-Evaluation via Terminal."""

import argparse
from ai.bots.bot_service import BotService
from ai.bots.evaluator import BotEvaluator
from game.game_service import GameService


def main():
    """Calculates Bot Performance and prints it to the Terminal."""
    parser = argparse.ArgumentParser(
        description="Evaluate different Bots against each other."
    )
    parser.add_argument("--n", type=int, default=100, help="Number of games to play.")
    parser.add_argument("--size", type=int, default=4, help="Board size.")
    parser.add_argument(
        "--bot1",
        type=str,
        default="rule",
        choices=["random", "rule", "ffn"],
        help="Type of Bot 1",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="Path to the AI model file (if bot type is ai).",
    )
    parser.add_argument("--epsilon", type=float, default=None, help="Epsilon for Bot 1")

    parser.add_argument(
        "--bot2",
        type=str,
        default="random",
        choices=["random", "rule", "ffn"],
        help="Type of Bot 2",
    )
    parser.add_argument("--model2", type=str, default=None, help="Model for Bot 2")
    parser.add_argument(
        "--epsilon2", type=float, default=None, help="Epsilon for Bot 2"
    )

    args = parser.parse_args()

    service = GameService()
    bot_service = BotService()
    evaluator = BotEvaluator(service, args.size)

    mod2 = args.model2 if args.model2 is not None else args.model
    eps2 = args.epsilon2 if args.epsilon2 is not None else args.epsilon

    bot1 = bot_service.create_bot(args.bot1, args.size, args.model, args.epsilon)
    bot2 = bot_service.create_bot(args.bot2, args.size, mod2, eps2)

    print(f"\n### Evaluating {bot1.BOT_NAME} vs {bot2.BOT_NAME} ({args.n} Games) ###\n")

    results = evaluator.evaluate(bot1, bot2, n_games=args.n)

    epsilon_string = ""
    epsilon2_string = ""

    if args.epsilon is not None:
        epsilon_string = f" (epsilon={args.epsilon})"
    if eps2 is not None:
        epsilon2_string = f" (epsilon={eps2})"

    bot1_name: str = f"{results['bot1_name']}"
    bot2_name: str = f"{results['bot2_name']}"

    print("-" * 30)
    print(f"RESULTS for {bot1_name + epsilon_string} vs {bot2_name + epsilon2_string}")
    print(
        f"Wins {bot1_name}: {results['wins_bot1']} ({results['win_rate_bot1']*100:.1f}%)"
    )
    print(
        f"Wins {bot2_name}: {results['wins_bot2']} ({results['win_rate_bot2']*100:.1f}%)"
    )
    print(f"Draws: {results['draws']}")
    print(f"Avg Score {bot1_name}: {results['avg_score_bot1']:.2f}")
    print(f"Avg Score {bot2_name}: {results['avg_score_bot2']:.2f}")
    print("-" * 30)


if __name__ == "__main__":
    main()
