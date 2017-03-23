from collections import deque
import abc

from pyknow import watchers
from pyknow.activation import Activation


class Matcher(metaclass=abc.ABCMeta):
    def __init__(self, engine):
        self.engine = engine

    @abc.abstractmethod
    def changes(adding=None, deleting=None):
        """
        Main interface with the matcher.

        Called by the knowledge engine when changes are made in the
        working memory and return a set of activations.

        """
        pass


class Strategy(metaclass=abc.ABCMeta):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.resolved = dict()

    @abc.abstractmethod
    def _update_agenda(self, agenda, added, removed):
        pass

    def update_agenda(self, agenda, added, removed):
        for act in removed:
            if act in agenda.activations:
                watchers.ACTIVATIONS.debug(
                    "<== %r: %r",
                    getattr(act.rule, '__name__', None),
                    sorted(act.facts, key=lambda x: hash(x.__class__)))

        for act in added:
            watchers.ACTIVATIONS.debug(
                "==> %r: %r",
                getattr(act.rule, '__name__', None),
                sorted(act.facts, key=lambda x: hash(x.__class__)))

        # Resolve conflicts using the appropiate strategy.
        new_activations = deque(self._update_agenda(agenda, added, removed))
        if new_activations != agenda.activations:
            agenda.activations = new_activations
