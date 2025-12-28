"""Generates Metics to compare different Bot Models."""

import random
from ai.bots.basic_bot import BasicBot
from ai.data.data_generator import DataGenerator, SimulationMode
from game.game_service import GameService


class BotEvaluator:
    """Evaluates two Bots against each other."""

    def __init__(self, service: GameService, board_size: int = 2):
        """Bot Evaluator Constructor."""
        self.service = service
        self.board_size = board_size
        self.generator = DataGenerator(service, board_size)

    def evaluate(
        self,
        bot1: BasicBot,
        bot2: BasicBot,
        n_games: int = 100,
        start_mode: SimulationMode = SimulationMode.ALTERNATE,
        save_moves: bool = True,
    ):
        """Evaluate Bot Performance.

        start_mode:
        - 'alternate': Alternates between Player 1 and Player 2
        - 'random'   : Coin Toss for Starting Player
        - 'fixed'    : Player 1 always starts
        """
        # Define Result Structure
        results = {
            "games": 0,
            "wins_bot1": 0,
            "wins_bot2": 0,
            "draws": 0,
            "avg_score_bot1": 0,
            "avg_score_bot2": 0,
        }

        total_score_1 = 0
        total_score_2 = 0

        for i in range(n_games):
            game_id = f"eval_{i+1}"
            start_player = self.generator._set_starting_player(start_mode, i)

            states = self.generator.simulate_game(
                game_id=game_id, bot1=bot1, bot2=bot2, starting_player=start_player, save_moves=save_moves
            )

            final_scores = states[-1]["state"]["scores"]
            score_p1, score_p2 = final_scores[1], final_scores[2]

            total_score_1 += score_p1
            total_score_2 += score_p2
            if score_p1 > score_p2:
                results["wins_bot1"] += 1
            elif score_p2 > score_p1:
                results["wins_bot2"] += 1
            else:
                results["draws"] += 1

            results["games"] += 1

        self._get_metrics(bot1, bot2, n_games, results, total_score_1, total_score_2)

        return results

    def _get_metrics(self, bot1, bot2, n_games, results, total_score_1, total_score_2):
        """Calculate Game Metrics."""
        results["avg_score_bot1"] = total_score_1 / n_games
        results["avg_score_bot2"] = total_score_2 / n_games
        results["win_rate_bot1"] = results["wins_bot1"] / n_games
        results["win_rate_bot2"] = results["wins_bot2"] / n_games
        results["bot1_name"] = bot1.name()
        results["bot2_name"] = bot2.name()
