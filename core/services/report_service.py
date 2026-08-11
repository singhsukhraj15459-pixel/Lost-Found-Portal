"""
Facade Pattern
---------------
Provides one simple entry point for "submit a report" that internally
coordinates the Factory (creation), Strategy (matching), and Observer
(notification) patterns. Views call this single method instead of
knowing about any of the three.
"""
from core.patterns.factories import ItemReportFactory
from core.patterns.matching import CategoryAreaKeywordStrategy
from core.patterns.observers import MatchSubject, NotificationObserver


class ReportService:
    def __init__(self):
        self.strategy = CategoryAreaKeywordStrategy()
        self.subject = MatchSubject()
        self.subject.subscribe(NotificationObserver())

    def submit_lost_item(self, user, form):
        item = ItemReportFactory.create_report('lost', user, form)
        matches = self.strategy.find_matches(item)
        self.subject.notify_all(item, matches)
        return item, matches

    def submit_found_item(self, user, form):
        item = ItemReportFactory.create_report('found', user, form)
        matches = self.strategy.find_matches(item)
        self.subject.notify_all(item, matches)
        return item, matches