from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegisterForm, UserLoginForm
from core.repositories.item_repository import LostItemRepository, FoundItemRepository
from .models import Category, LostItem, FoundItem, Message, MatchNotification, User
from core.services.report_service import ReportService
from django.shortcuts import get_object_or_404
from core.patterns.matching import CategoryAreaKeywordStrategy
from django.db.models import Q
from .models import Message
from .forms import MessageForm
from .models import MatchNotification
from .forms import ProfileUpdateForm
from django.contrib.admin.views.decorators import staff_member_required
from .models import User


def home_view(request):
    return render(request, 'core/home.html')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='core.backends.EmailBackend')
            messages.success(request, "Account created successfully. Welcome!")
            return redirect('dashboard')
    else:
        form = UserRegisterForm()

    return render(request, 'core/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
            else:
                messages.error(request, "Invalid email or password.")
    else:
        form = UserLoginForm()

    return render(request, 'core/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('home')


@login_required
def dashboard_view(request):
    return render(request, 'core/dashboard.html')
from .forms import UserRegisterForm, UserLoginForm, LostItemForm, FoundItemForm
from core.patterns.factories import ItemReportFactory


@login_required
def report_lost_view(request):
    if request.method == 'POST':
        form = LostItemForm(request.POST, request.FILES)
        if form.is_valid():
            item, matches = ReportService().submit_lost_item(request.user, form)
            if matches:
                messages.success(request, f"Lost item reported. {len(matches)} potential match(es) found!")
            else:
                messages.success(request, "Lost item reported successfully.")
            return redirect('dashboard')
    else:
        form = LostItemForm()

    return render(request, 'core/report_lost.html', {'form': form})


@login_required
def report_found_view(request):
    if request.method == 'POST':
        form = FoundItemForm(request.POST, request.FILES)
        if form.is_valid():
            item, matches = ReportService().submit_found_item(request.user, form)
            if matches:
                messages.success(request, f"Found item reported. {len(matches)} potential match(es) found!")
            else:
                messages.success(request, "Found item reported successfully.")
            return redirect('dashboard')
    else:
        form = FoundItemForm()

    return render(request, 'core/report_found.html', {'form': form})
def browse_lost_view(request):
    keyword = request.GET.get('keyword', '')
    category = request.GET.get('category', '')
    area = request.GET.get('area', '')
    status = request.GET.get('status', '')

    items = LostItemRepository.search(
        keyword=keyword or None,
        category=category or None,
        area=area or None,
        status=status or None,
    )
    categories = Category.objects.all()

    return render(request, 'core/browse_lost.html', {
        'items': items,
        'categories': categories,
        'keyword': keyword,
        'selected_category': category,
        'area': area,
        'status': status,
    })


def browse_found_view(request):
    keyword = request.GET.get('keyword', '')
    category = request.GET.get('category', '')
    area = request.GET.get('area', '')
    status = request.GET.get('status', '')

    items = FoundItemRepository.search(
        keyword=keyword or None,
        category=category or None,
        area=area or None,
        status=status or None,
    )
    categories = Category.objects.all()

    return render(request, 'core/browse_found.html', {
        'items': items,
        'categories': categories,
        'keyword': keyword,
        'selected_category': category,
        'area': area,
        'status': status,
    })
def lost_item_detail_view(request, item_id):
    item = get_object_or_404(LostItem, id=item_id)
    return render(request, 'core/item_detail.html', {
        'item': item,
        'item_kind': 'Lost',
    })


def found_item_detail_view(request, item_id):
    item = get_object_or_404(FoundItem, id=item_id)
    return render(request, 'core/item_detail.html', {
        'item': item,
        'item_kind': 'Found',
    })
@login_required
def inbox_view(request):
    # Get every user this person has exchanged messages with
    conversations = Message.objects.filter(
        Q(sender=request.user) | Q(receiver=request.user)
    ).order_by('-timestamp')

    # Build a unique list of "other users" with their latest message
    seen_users = {}
    for msg in conversations:
        other_user = msg.receiver if msg.sender == request.user else msg.sender
        if other_user.id not in seen_users:
            seen_users[other_user.id] = {
                'user': other_user,
                'last_message': msg,
                'unread': Message.objects.filter(sender=other_user, receiver=request.user, is_read=False).count(),
            }

    return render(request, 'core/inbox.html', {'conversations': seen_users.values()})


@login_required
def conversation_view(request, user_id):
    from .models import User
    other_user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.sender = request.user
            msg.receiver = other_user
            msg.save()
            return redirect('conversation', user_id=other_user.id)
    else:
        form = MessageForm()

    # Mark incoming messages from this user as read
    Message.objects.filter(sender=other_user, receiver=request.user, is_read=False).update(is_read=True)

    thread = Message.objects.filter(
        Q(sender=request.user, receiver=other_user) | Q(sender=other_user, receiver=request.user)
    ).order_by('timestamp')

    return render(request, 'core/conversation.html', {
        'other_user': other_user,
        'thread': thread,
        'form': form,
    })


@login_required
def start_conversation_view(request, item_type, item_id):
    """
    Entry point from an item detail page's "Contact" button.
    Redirects straight into a conversation with that item's owner.
    """
    if item_type == 'lost':
        item = get_object_or_404(LostItem, id=item_id)
    else:
        item = get_object_or_404(FoundItem, id=item_id)

    if item.user == request.user:
        messages.error(request, "You can't message yourself about your own report.")
        return redirect('dashboard')

    return redirect('conversation', user_id=item.user.id)

@login_required
def dashboard_view(request):
    my_lost = LostItemRepository.get_by_user(request.user)
    my_found = FoundItemRepository.get_by_user(request.user)

    recovered_lost = my_lost.filter(status='recovered')
    recovered_found = my_found.filter(status='recovered')

    match_notifications = MatchNotification.objects.filter(
        Q(lost_item__user=request.user) | Q(found_item__user=request.user)
    ).select_related(
        'lost_item', 'found_item', 'lost_item__category', 'found_item__category'
    ).order_by('-created_at')[:5]

    my_matches = []
    for match in match_notifications:
        if match.lost_item.user == request.user:
            my_matches.append({
                'my_item': match.lost_item,
                'my_item_type': 'lost',
                'other_item': match.found_item,
                'other_item_type': 'found',
            })
        else:
            my_matches.append({
                'my_item': match.found_item,
                'my_item_type': 'found',
                'other_item': match.lost_item,
                'other_item_type': 'lost',
            })

    return render(request, 'core/dashboard.html', {
        'my_lost': my_lost,
        'my_found': my_found,
        'recovered_count': recovered_lost.count() + recovered_found.count(),
        'my_matches': my_matches,
    })


@login_required
def my_lost_reports_view(request):
    items = LostItemRepository.get_by_user(request.user)
    return render(request, 'core/my_lost_reports.html', {'items': items})


@login_required
def my_found_reports_view(request):
    items = FoundItemRepository.get_by_user(request.user)
    return render(request, 'core/my_found_reports.html', {'items': items})


@login_required
def mark_lost_recovered_view(request, item_id):
    item = get_object_or_404(LostItem, id=item_id, user=request.user)
    item.status = 'recovered'
    item.save()
    messages.success(request, f"'{item.title}' marked as recovered.")
    return redirect('my_lost_reports')


@login_required
def mark_found_recovered_view(request, item_id):
    item = get_object_or_404(FoundItem, id=item_id, user=request.user)
    item.status = 'recovered'
    item.save()
    messages.success(request, f"'{item.title}' marked as recovered.")
    return redirect('my_found_reports')


@login_required
def profile_view(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=request.user)

    reports_submitted = request.user.lost_items.count() + request.user.found_items.count()
    recovered = request.user.lost_items.filter(status='recovered').count() + \
                request.user.found_items.filter(status='recovered').count()

    return render(request, 'core/profile.html', {
        'form': form,
        'reports_submitted': reports_submitted,
        'recovered': recovered,
    })
@staff_member_required
def admin_statistics_view(request):
    stats = {
        'total_users': User.objects.count(),
        'active_users': User.objects.filter(is_active=True).count(),
        'suspended_users': User.objects.filter(is_active=False).count(),
        'total_lost': LostItem.objects.count(),
        'total_found': FoundItem.objects.count(),
        'lost_searching': LostItem.objects.filter(status='searching').count(),
        'lost_recovered': LostItem.objects.filter(status='recovered').count(),
        'found_waiting': FoundItem.objects.filter(status='waiting').count(),
        'found_recovered': FoundItem.objects.filter(status='recovered').count(),
        'total_matches': MatchNotification.objects.count(),
        'total_messages': Message.objects.count(),
    }
    return render(request, 'core/admin_statistics.html', {'stats': stats})