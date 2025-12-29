import argparse
from ai.bots.random_bot import RandomBot
from ai.bots.rule_based_bot import RuleBasedBot
from ai.bots.ffn_bot import FFNBot
from ai.bots.evaluation import BotEvaluator
from game.game_service import GameService

def main():
    parser = argparse.ArgumentParser(description="Evaluate different Bots against each other.")
    parser.add_argument("--n", type=int, default=100, help="Number of games to play.")
    parser.add_argument("--size", type=int, default=4, help="Board size.")
    parser.add_argument("--bot1", type=str, default="rule", choices=["random", "rule", "ffn"], help="Type of Bot 1")
    parser.add_argument("--bot2", type=str, default="random", choices=["random", "rule", "ffn"], help="Type of Bot 2")
    parser.add_argument("--model", type=str, default="", help="Path to the AI model file (if bot type is ai).")

    args = parser.parse_args()

    service = GameService()
    evaluator = BotEvaluator(service, args.size)

    def create_bot(bot_type):
        if bot_type == "random":
            return RandomBot(args.size)
        elif bot_type == "rule":
            return RuleBasedBot(args.size)
        elif bot_type == "ffn":
            if not args.model:
                raise ValueError("Model path must be provided for AI Bot.")

            model_path = "outputs/model/" + args.model
            bot = FFNBot(args.size, model_path)
            return bot

    bot1 = create_bot(args.bot1)
    bot2 = create_bot(args.bot2)

    print(f"\n### Evaluating {bot1.BOT_NAME} vs {bot2.BOT_NAME} ({args.n} Games) ###\n")
    
    results = evaluator.evaluate(bot1, bot2, n_games=args.n)

    print("-" * 30)
    print(f"RESULTS for {results['bot1_name']} vs {results['bot2_name']}")
    print(f"Wins {results['bot1_name']}: {results['wins_bot1']} ({results['win_rate_bot1']*100:.1f}%)")
    print(f"Wins {results['bot2_name']}: {results['wins_bot2']} ({results['win_rate_bot2']*100:.1f}%)")
    print(f"Draws: {results['draws']}")
    print(f"Avg Score {results['bot1_name']}: {results['avg_score_bot1']:.2f}")
    print(f"Avg Score {results['bot2_name']}: {results['avg_score_bot2']:.2f}")
    print("-" * 30)

if __name__ == "__main__":
    main()