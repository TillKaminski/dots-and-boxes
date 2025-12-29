"""Class is responsible for Data Generation."""

import argparse
import logging
import os
import random

from matplotlib.pylab import Enum
from ai.bots.basic_bot import BasicBot
from ai.bots.ffn_bot import FFNBot
from ai.bots.rule_based_bot import RuleBasedBot
from ai.data.data_storage import DataStorage
from game.game_service import GameService
from ai.bots.random_bot import RandomBot, Move

logger = logging.getLogger(__name__)

BOT_CLASSES: dict[str, BasicBot] = {
    "random": RandomBot,
    "rule": RuleBasedBot,
    "ffn": FFNBot,
    # TODO: Add more Bots.
}


class SimulationMode(Enum):
    """Represents the Player Order during the Simulation."""

    FIXED = "fixed"
    RANDOM = "random"
    ALTERNATE = "alternate"


class DataGenerator:
    """Simulates games between two bots and collects training data."""

    def __init__(self, service: GameService, board_size: int = 2):
        """Data Generator Constructor."""
        self.service = service
        self.board_size = board_size

    def simulate_game(
        self,
        game_id: str,
        bot1: BasicBot,
        bot2: BasicBot,
        starting_player: int = 1,
        save_moves: bool = True,
        log: bool = False,
    ):
        """Simulate a single Game between bot1 and bot2.

        Returns:
            state_list: List of dicts representing state before and after move. Move logging available.
        """
        if game_id in self.service.games:
            self.service.restart_game(game_id, starting_player=starting_player)
        else:
            self.service.create_game(
                game_id, size=self.board_size, starting_player=starting_player
            )

        # Setup Bots
        bot1.reset()
        bot2.reset()

        state_list = []
        if starting_player == 1:
            current_bot = bot1
        else:
            # starting_player == 2:
            current_bot = bot2

        while not self.service.games[game_id].game_finished:
            if current_bot.game_state_required():
                state = self.service.get_state_object(game_id)
                current_bot.update_state(state)

            move: Move = current_bot.move(log_move=log, return_dictionary=False)

            state_before = self.service.get_state(game_id=game_id)

            # Execute Move
            current_player = state_before["current_player"]
            result = self.service.make_move(
                game_id=game_id,
                player_id=current_player,
                x=move.x,
                y=move.y,
                orientation=move.orientation,
            )

            if "error" in result and result["error"]:
                if log:
                    logger.warning(f"Move rejected: {result['error']}")
                # Remove invalid Move from list
                current_bot.update(move.x, move.y, move.orientation)
                continue

            bot1.update(move.x, move.y, move.orientation)
            bot2.update(move.x, move.y, move.orientation)

            entry = {}

            if save_moves:
                move_data = {
                    "x": move.x,
                    "y": move.y,
                    "orientation": move.orientation.name,
                    "player": 1 if current_bot == bot1 else 2,
                    "bot_type": current_bot.name(),
                    "scores": result["scores"],
                }
                entry["move"] = move_data
            entry["state_before"] = state_before.copy()
            entry["state"] = result.copy()

            state_list.append(entry)

            # Get Bot for next Turn (result always
            # contains the current player, no matter
            # if a box was closed or not)
            next_player = result["current_player"]
            current_bot = bot1 if next_player == 1 else bot2
        return state_list

    def simulate_multiple_games(
        self,
        n_games: int,
        bot1: BasicBot,
        bot2: BasicBot,
        start_mode: SimulationMode = SimulationMode.FIXED,
        prefix: str = "game",
        log: bool = False,
    ):
        """Simulate multiple games."""
        all_games = {}
        for i in range(n_games):
            game_id = f"{prefix}_{i+1}"
            starting_player = self._set_starting_player(start_mode, i)
            states = self.simulate_game(
                game_id, bot1, bot2, starting_player=starting_player, log=log
            )
            all_games[game_id] = states
            if (i + 1) % 100 == 0:
                print(f"Simulated {i+1}/{n_games}...")

        if log:
            logger.info(f"Simulated {n_games} games.")
        return all_games

    def _set_starting_player(self, mode: SimulationMode, game_index: int) -> int:
        """Sets the Starting Player for different Simulation Modes [`random`, `fixed`, `alternate`]."""
        if mode not in SimulationMode:
            logger.warning("Unknown Simulation Mode, use 'fixed' as default.")
        if mode == SimulationMode.ALTERNATE:
            return 1 if game_index % 2 == 0 else 2
        elif mode == SimulationMode.RANDOM:
            return random.choice([1, 2])
        # Default: SimulationMode.FIXED
        return 1


def create_bot(bot_name: str, size: int) -> BasicBot:
    """Helper function to create a bot based on its name."""
    BotClass = BOT_CLASSES.get(bot_name.lower())
    if BotClass is None:
        raise ValueError(f"Unknown bot type: {bot_name}")
    return BotClass(size)


def main():
    """Method that handles Terminal Input."""
    parser = argparse.ArgumentParser(description="Generates Training-Data.")
    parser.add_argument(
        "--view",
        type=int,
        default=0,
        help="Print Data Summary for the first 'n' Games. Other Parameters are ignored.",
    )

    parser.add_argument(
        "--states",
        type=int,
        default=10,
        help="Number of States that are printed to console.",
    )

    parser.add_argument(
        "--log", dest="log", action="store_true", help="Enable Terminal Logging."
    )
    parser.set_defaults(log=False)

    parser.add_argument("--games", type=int, default=1000, help="Number of Games.")
    parser.add_argument("--size", type=int, default=4, help="Board-Size.")
    parser.add_argument(
        "--bot1",
        type=str,
        default="random",
        help="Bot-Type Player 1. [random, rule, fnn]",
    )
    parser.add_argument(
        "--bot2",
        type=str,
        default="random",
        help="Bot-Type Player 2. [random, rule, fnn]",
    )

    parser.add_argument(
        "--mode",
        type=str,
        default="fixed",
        help="Set Simulation Mode: [fixed (default), random, alternate]",
    )

    parser.add_argument(
        "--json", type=int, default=2, help="Save the first 'n' Games in JSON-Format."
    )

    parser.add_argument(
        "--no-pt", dest="pt", action="store_false", help="Save Data in .pt-Format."
    )
    parser.set_defaults(pt=True)

    parser.add_argument(
        "--name",
        type=str,
        default="training_data_raw.pt",
        help="Filename for the .pt file.",
    )
    parser.add_argument(
        "--merge",
        action="store_true",
        help="Merge with existing file instead of overwriting.",
    )
    parser.add_argument(
        "--label",
        type=str,
        default="game",
        help="Prefix for the game IDs (e.g. 'rule', 'rand').",
    )

    args = parser.parse_args()

    size = args.size
    bot1 = args.bot1
    bot2 = args.bot2
    number_games = args.games
    log = args.log
    view = args.view
    states = args.states
    json = args.json
    pt = args.pt
    name = args.name
    merge = args.merge
    label = args.label

    try:
        mode_enum = SimulationMode(args.mode)
    except ValueError:
        mode_enum = SimulationMode.FIXED

    if log:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.INFO, filename="./ai/data/testlog.log")

    data_storage = DataStorage(log=log)

    file_path = data_storage.get_path(name)

    if merge and not os.path.exists(file_path):
        logger.error(f"Canceled: --merge set, but no file exists with name {name}!")
        return

    if view > 0:
        data = data_storage.load_from_pt(name)
        data_storage.print_training_data_summary(
            data, limit_games=view, limit_states=states
        )
        return

    try:
        bot1 = create_bot(bot1, size)
        bot2 = create_bot(bot2, size)
    except ValueError as e:
        logger.error(f"Error creating bot: {e}")
        return

    game_service: GameService = GameService()
    data_generator: DataGenerator = DataGenerator(game_service, size)

    data = data_generator.simulate_multiple_games(
        n_games=number_games,
        bot1=bot1,
        bot2=bot2,
        start_mode=mode_enum,
        log=log,
        prefix=label,
    )

    if json > 0:
        data_json = list(data.items())[:json]
        data_storage.save_to_json(data_json)

    if pt:
        if merge:
            data_storage.merge_and_save(data, name, label)
        else:
            data_storage.save_to_pt(data, name)


if __name__ == "__main__":  # pragma: no cover
    main()
