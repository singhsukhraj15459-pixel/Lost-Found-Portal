"""
Repository Pattern
--------------------
Wraps all data-access logic for LostItem/FoundItem behind a clean
interface. Views call these methods instead of writing ORM queries
directly — keeps query logic in one place, easier to test/change later.
"""
from core.models import LostItem, FoundItem


class LostItemRepository:
    @staticmethod
    def search(keyword=None, category=None, area=None, status=None):
        qs = LostItem.objects.select_related('category', 'user').all()

        if keyword:
            qs = qs.filter(title__icontains=keyword)
        if category:
            qs = qs.filter(category__id=category)
        if area:
            qs = qs.filter(area__icontains=area)
        if status:
            qs = qs.filter(status=status)

        return qs.order_by('-created_at')

    @staticmethod
    def get_by_user(user):
        return LostItem.objects.filter(user=user).order_by('-created_at')

    @staticmethod
    def get_by_id(item_id):
        return LostItem.objects.select_related('category', 'user').get(id=item_id)


class FoundItemRepository:
    @staticmethod
    def search(keyword=None, category=None, area=None, status=None):
        qs = FoundItem.objects.select_related('category', 'user').all()

        if keyword:
            qs = qs.filter(title__icontains=keyword)
        if category:
            qs = qs.filter(category__id=category)
        if area:
            qs = qs.filter(area__icontains=area)
        if status:
            qs = qs.filter(status=status)

        return qs.order_by('-created_at')

    @staticmethod
    def get_by_user(user):
        return FoundItem.objects.filter(user=user).order_by('-created_at')

    @staticmethod
    def get_by_id(item_id):
        return FoundItem.objects.select_related('category', 'user').get(id=item_id)