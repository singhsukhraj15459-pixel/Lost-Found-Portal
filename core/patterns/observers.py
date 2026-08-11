"""
Observer Pattern
-----------------
Decouples "a match was found" from "what happens next". Right now
only one observer exists (saving a MatchNotification record), but
more could be added later (e.g. sending an email) without changing
the matching logic itself.
"""
from abc import ABC, abstractmethod
from core.models import MatchNotification, LostItem, FoundItem


class MatchObserver(ABC):
    @abstractmethod
    def update(self, lost_item, found_item):
        pass


class NotificationObserver(MatchObserver):
    def update(self, lost_item, found_item):
        MatchNotification.objects.get_or_create(
            lost_item=lost_item,
            found_item=found_item,
        )


class MatchSubject:
    """Holds observers and notifies them all when a match occurs."""

    def __init__(self):
        self._observers = []

    def subscribe(self, observer: MatchObserver):
        self._observers.append(observer)

    def notify_all(self, item, matches):
        for match in matches:
            if isinstance(item, LostItem):
                lost_item, found_item = item, match
            else:
                lost_item, found_item = match, item

            for observer in self._observers:
                observer.update(lost_item, found_item)