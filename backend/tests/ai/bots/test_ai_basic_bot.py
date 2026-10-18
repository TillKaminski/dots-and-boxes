"""Test Class for Bot Basic Class (abstract)."""

import unittest
from typing import Any, Dict
from backend.game.game_board import Orientation
from backend.ai.agents.base_agent import BaseAgent


# Create Classes for Inheritance Behavior
class TestBot(BaseAgent):
    """Subclass that calls Superclass Methods."""

    def reset(self) -> None:
        """Call Superclass reset-Method."""
        return super().reset()

    def _select_move(
        self, log_move: bool = False, return_dictionary: bool = False
    ) -> Dict[str, Any]:
        """Call Superclass move-Method."""
        return super()._select_move()

    def update(self, x: int, y: int, orientation: Orientation) -> None:
        """Call Superclass update-Method."""
        return super().update(x, y, orientation)

    def name(self) -> str:
        """Call Superclass name-Method."""
        return super().name()


class MockBot(BaseAgent):
    """Minimal Bot Implementation."""

    def reset(self) -> None:
        """Override of abstract Method reset."""
        self._reset_called = True

    def _select_move(
        self, log_move: bool = False, return_dictionary: bool = False
    ) -> Dict[str, Any]:
        """Override of abstract Method move."""
        return {"x": 0, "y": 0, "orientation": Orientation.HORIZONTAL}

    def update(self, x: int, y: int, orientation: Orientation) -> None:
        """Override of abstract Method update."""
        self._last_update = (x, y, orientation)

    def name(self) -> str:
        """Override of abstract Method name."""
        return "TestBot"


class TestAbstractMethods(unittest.TestCase):
    """Superclass Methods should not be callable."""

    def test_all_abstract_methods_raise(self):
        """Calling Super-Methods throws an 'NotImplementedError'."""
        self.bot = TestBot()

        with self.assertRaises(NotImplementedError):
            self.bot.reset()

        with self.assertRaises(NotImplementedError):
            self.bot.move()

        with self.assertRaises(NotImplementedError):
            self.bot.update(x=0, y=0, orientation=Orientation.HORIZONTAL)

        # Bot Name not set
        assert self.bot.name() == BaseAgent.BOT_NAME


class TestBasicBotImplementation(unittest.TestCase):
    """Test Abstract Class Implementation."""

    def test_call_abstract_class_throws_error(self):
        """Creating an instance of Basic Class throws an error."""
        with self.assertRaises(TypeError):
            BaseAgent()

    def test_subclass_methods(self):
        """Test Subclass Implementations."""
        self.bot = MockBot()

        # Test name()
        self.assertEqual(self.bot.name(), "TestBot")

        # Test reset()
        self.assertIsNone(self.bot.reset())

        # Test move()
        move = self.bot._select_move()
        expect = {"x", "y", "orientation"}
        self.assertEqual(set(move.keys()), expect)
        self.assertIsInstance(move["x"], int)
        self.assertIsInstance(move["y"], int)
        self.assertIsInstance(move["orientation"], Orientation)

        # Test update()
        self.assertIsNone(self.bot.update(3, 4, Orientation.VERTICAL))
        self.assertEqual(self.bot._last_update, (3, 4, Orientation.VERTICAL))
