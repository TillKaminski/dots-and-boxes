"""Generates Metics to compare different Bot Models."""

import random
from ai.bots.basic_bot import BasicBot
from ai.data.data_generator import DataGenerator
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
        start_mode: str = "alternate",
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
            start_player = self._set_starting_player(start_mode, i)
            p1, p2 = self._set_bots(bot1, bot2, start_player)

            game_id = f"eval_{i+1}"

            states = self.generator.simulate_game(
                game_id=game_id, bot1=p1, bot2=p2, save_moves=save_moves
            )

            total_score_1, total_score_2 = self._update_scores(
                bot1,
                results,
                p1,
                p2,
                states,
                total_score_1,
                total_score_2,
            )

        self._get_metrics(bot1, bot2, n_games, results, total_score_1, total_score_2)

        return results

    def _update_scores(
        self,
        bot1,
        results,
        p1,
        p2,
        states,
        total_score_1,
        total_score_2,
    ):
        """Update Player Scores."""
        final_scores = states[-1]["state"]["scores"]
        s1, s2 = final_scores[1], final_scores[2]

        if p1 == bot1:
            total_score_1 += s1
            total_score_2 += s2
        else:
            total_score_1 += s2
            total_score_2 += s1

            # Get Winner
        if s1 > s2:
            winner = 1
        elif s2 > s1:
            winner = 2
        else:
            # Draw
            winner = 0

            # Match Scores and Bots
        if winner == 1:
            if p1 == bot1:
                results["wins_bot1"] += 1
            else:
                results["wins_bot2"] += 1
        elif winner == 2:
            if p2 == bot1:
                results["wins_bot1"] += 1
            else:
                results["wins_bot2"] += 1
        else:
            results["draws"] += 1

        results["games"] += 1

        return total_score_1, total_score_2

    def _get_metrics(self, bot1, bot2, n_games, results, total_score_1, total_score_2):
        """Calculate Game Metrics."""
        results["avg_score_bot1"] = total_score_1 / n_games
        results["avg_score_bot2"] = total_score_2 / n_games
        results["win_rate_bot1"] = results["wins_bot1"] / n_games
        results["win_rate_bot2"] = results["wins_bot2"] / n_games
        results["bot1_name"] = bot1.name()
        results["bot2_name"] = bot2.name()

    def _set_bots(self, bot1, bot2, start_player):
        """Set Bot Order to represent Starting Player."""
        if start_player == 1:
            p1, p2 = bot1, bot2
        else:
            p1, p2 = bot2, bot1
        return p1, p2

    def _set_starting_player(self, start_mode, i):
        """Get the starting Player for different Simulation Modes."""
        if start_mode == "alternate":
            start_player = 1 if i % 2 == 0 else 2
        elif start_mode == "random":
            start_player = random.choice([1, 2])
        else:
            # start_mode == fixed
            start_player = 1
        return start_player
