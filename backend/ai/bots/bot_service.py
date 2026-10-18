"""Service Class that handles Bot Management."""

import inspect
from backend.ai.bots.basic_bot import BasicBot
from backend.ai.bots.ffn_bot import FFNBot
from backend.ai.bots.move import Move
from backend.ai.bots.random_bot import RandomBot
from backend.ai.bots.rule_based_bot import RuleBasedBot
from backend.game.game_board import Orientation
from backend.game.game_state import GameState

BOT_MODEL: dict[str, BasicBot] = {
    "random": RandomBot,
    "rule": RuleBasedBot,
    "ffn": FFNBot,
    "pvn": FFNBot,  # Placeholder, TODO: Implement PVN Bot
}

ACTIVE_BOTS: dict[str, BasicBot] = {}


class BotService:
    """Manages different Bot Models."""

    def create_bot(
        self,
        bot_name: str,
        size: int,
        model: str | None = None,
        epsilon: float | None = None,
    ) -> BasicBot:
        """Function to create a bot based on its name."""
        BotClass = BOT_MODEL.get(bot_name.lower())
        if BotClass is None:
            raise ValueError(f"Unknown bot type: {bot_name}")

        potential_params = {
            "size": size,
            "model_path": self._set_path(model),
            "epsilon": epsilon,
        }

        sig = inspect.signature(BotClass.__init__)
        valid_params = {
            k: v
            for k, v in potential_params.items()
            if k in sig.parameters and v is not None
        }

        return BotClass(**valid_params)

    def _set_path(self, model):
        """Helper Methods to create the Model-Path."""
        if model is not None:
            return "outputs/model/" + model
        return None

    def get_bot_models(self) -> set[str]:
        """Returns available Bot Models."""
        return BOT_MODEL.keys()

    def get_bot_model(self, model: str) -> BasicBot:
        """Returns the Bot Object."""
        model_lower = model.lower()
        if model_lower in BOT_MODEL.keys():
            return BOT_MODEL.get(model_lower)
        raise ValueError("Bot Model not found.")

    def game_state_required(self, bot_model: str | BasicBot) -> bool:
        """Check, if Bot needs a GameState Object for predictions.

        Accepts Model Name as String or Model Object.
        """
        if isinstance(bot_model, str):
            BotClass = self.get_bot_model(bot_model)
            return BotClass.game_state_required()
        elif isinstance(bot_model, BasicBot):
            return bot_model.game_state_required()

    def get_move(self, game_id: str, game_state: GameState | None = None) -> Move:
        """Returns the Bot Move (Model dependent)."""
        bot_model = self.get_bot(game_id)
        if self.game_state_required(bot_model):
            if game_state is None:
                raise ValueError(f"NN Bot '{bot_model.name()}' needs GameState.")
            # Update current Game State
            bot_model.update_state(game_state)
        return bot_model.move()

    def update_possible_moves(
        self, game_id: str, x: int, y: int, orientation: Orientation
    ):
        """Updates possible Moves Array."""
        bot_model = self.get_bot(game_id)
        bot_model.update(x, y, orientation)

    def register_bot(self, game_id: str, size: int, bot_model: str):
        """Registers Bot Model by Game ID."""
        if game_id in ACTIVE_BOTS.keys():
            raise ValueError(
                f"Bot ({ACTIVE_BOTS[game_id].name()}) already registered (Game-ID: {game_id})"
            )
        bot = self.get_bot_model(bot_model)
        bot_obj = bot(size)
        ACTIVE_BOTS[game_id] = bot_obj

    def delete_bot(self, game_id: str):
        """Deletes Bot from the List of active Bots."""
        if game_id not in ACTIVE_BOTS.keys():
            raise ValueError(f"No Bot found for Game-ID {game_id}")
        deleted_bot = ACTIVE_BOTS.pop(game_id)
        return f"Deleted Bot: {deleted_bot.name()}: ({game_id})"

    def get_bot(self, game_id: str) -> BasicBot:
        """Returns Bot Model in dependency of GameID."""
        if game_id in ACTIVE_BOTS.keys():
            return ACTIVE_BOTS[game_id]
        raise ValueError(f"No Bot-Registration found for Game: {game_id}")
