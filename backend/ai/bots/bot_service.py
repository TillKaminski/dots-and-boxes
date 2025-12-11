"""Service Class that handles Bot Management."""

from ai.bots.basic_bot import BasicBot
from ai.bots.ffn_bot import FFNBot
from ai.bots.move import Move
from ai.bots.random_bot import RandomBot
from ai.bots.rule_based_bot import RuleBasedBot
from game.game_state import GameState

BOT_MODEL: dict[str, BasicBot] = {
    "random": RandomBot,
    "rule": RuleBasedBot,
    "ffn": FFNBot,
    "pvn": FFNBot,  # Placeholder, TODO: Implement PVN Bot
}

ACTIVE_BOTS: dict[str, BasicBot] = {}

class BotService:
    """Manages different Bot Models."""

    def get_bot_models(self) -> set[str]:
        """Returns available Bot Models."""
        return BOT_MODEL.keys()
    
    def get_bot_model(self, model: str) -> BasicBot:
        """Returns the Bot Object."""
        if model in BOT_MODEL.keys():
            return BOT_MODEL.get(model.lower())
        raise ValueError("Bot Model not found.")
    
    def is_nn_bot(self, bot_model: str | BasicBot) -> bool:
        """Check, if Bot needs a GameState Object for predictions.
        
        Accepts Model Name as String or Model Object.
        """
        if isinstance(bot_model, str):
            return bot_model == "ffn" or bot_model == "pvn"
        elif isinstance(bot_model, BasicBot):
            return bot_model.name() == "ffn-bot" or bot_model.name() == "pvn-bot"
        
    def get_move(self, game_id: str, game_state: GameState | None = None) -> Move:
        """Returns the Bot Move (Model dependent)."""
        bot_model = self.get_bot(game_id)        
        if self.is_nn_bot(bot_model):
            if game_state is None:
                raise ValueError(f"NN Bot '{bot_model.name()}' needs GameState.")
            # Update current Game State
            bot_model.update_state(game_state)
        return bot_model.move()
    
    def register_bot(self, game_id: str, size: int, bot_model: str):
        """Registers Bot Model by Game ID."""
        if game_id in ACTIVE_BOTS.keys():
            raise ValueError(f"Bot ({ACTIVE_BOTS[game_id].name()}) already registered (Game-ID: {game_id})")
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
