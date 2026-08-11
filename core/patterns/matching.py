"""
Strategy Pattern
-----------------
Defines an interchangeable matching algorithm. Today it's simple
rule-based matching (category + area + keyword overlap), but a
different strategy (e.g. smarter scoring, or future AI matching)
could be swapped in without touching views or the Facade.
"""
from abc import ABC, abstractmethod
from core.models import FoundItem, LostItem


class MatchingStrategy(ABC):
    @abstractmethod
    def find_matches(self, item):
        """Given a LostItem or FoundItem, return a queryset of possible matches."""
        pass


class CategoryAreaKeywordStrategy(MatchingStrategy):
    """
    Rule-based matching:
    - Same category
    - Same area (case-insensitive)
    - At least one shared keyword from the title
    """

    def find_matches(self, item):
        if isinstance(item, LostItem):
            candidates = FoundItem.objects.filter(
                category=item.category,
                area__iexact=item.area,
                status='waiting',
            )
        elif isinstance(item, FoundItem):
            candidates = LostItem.objects.filter(
                category=item.category,
                area__iexact=item.area,
                status='searching',
            )
        else:
            return []

        item_keywords = set(item.title.lower().split())
        matches = []
        for candidate in candidates:
            candidate_keywords = set(candidate.title.lower().split())
            if item_keywords & candidate_keywords:
                matches.append(candidate)

        return matches