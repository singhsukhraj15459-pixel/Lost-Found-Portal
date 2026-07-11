"""
Factory Method Pattern
-----------------------
Centralizes the creation of LostItem and FoundItem records so that
views don't need to know the differing defaults (status values) or
duplicate creation logic. If a new report type were ever added
(e.g. "Handed to Police"), only this factory needs to change.
"""
from core.models import LostItem, FoundItem


class ItemReportFactory:
    @staticmethod
    def create_report(report_type, user, form):
        """
        report_type: 'lost' or 'found'
        user: the logged-in user submitting the report
        form: a validated ModelForm (LostItemForm or FoundItemForm)
        """
        item = form.save(commit=False)
        item.user = user

        if report_type == 'lost':
            item.status = 'searching'
        elif report_type == 'found':
            item.status = 'waiting'
        else:
            raise ValueError(f"Unknown report_type: {report_type}")

        item.save()
        return item