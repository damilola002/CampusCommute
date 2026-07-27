import math
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.contrib import messages
from .models import RideOrder, Notification
from .forms import RideOrderForm


def haversine(lat1, lng1, lat2, lng2):
    """Return distance in miles between two lat/lng points."""
    R = 3958.8
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi    = math.radians(lat2 - lat1)
    dlambda = math.radians(lng2 - lng1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))


@login_required
def create_order(request):
    if request.method == 'POST':
        form = RideOrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.rider = request.user
            order.save()

            # Notify all drivers within 10 miles of the pickup point
            User = get_user_model()
            for driver in User.objects.filter(role='driver', driver_lat__isnull=False, driver_lng__isnull=False):
                dist = haversine(driver.driver_lat, driver.driver_lng, order.pickup_lat, order.pickup_lng)
                if dist <= 10:
                    Notification.objects.create(
                        recipient=driver,
                        ride_order=order,
                        message=f"New ride request near you: {order.pickup_location} → {order.dropoff_location}",
                    )

            messages.success(request, "Your ride request has been posted!")
            return redirect('community_board')
    else:
        form = RideOrderForm()

    return render(request, 'ordering_service/create_order.html', {'form': form})


def community_board(request):
    """Public board — everyone can see all requests and their status."""
    orders = RideOrder.objects.select_related('rider', 'driver').all()
    return render(request, 'ordering_service/community_board.html', {'orders': orders})


@login_required
def driver_board(request):
    """Driver view — shows only pending orders within 10 miles."""
    driver = request.user
    all_pending = RideOrder.objects.filter(status='pending').select_related('rider')

    nearby_orders = []
    if driver.driver_lat is not None and driver.driver_lng is not None:
        for order in all_pending:
            dist = haversine(driver.driver_lat, driver.driver_lng, order.pickup_lat, order.pickup_lng)
            if dist <= 10:
                nearby_orders.append({'order': order, 'distance': round(dist, 1)})
    else:
        # Driver has no location set — show all pending with no distance
        nearby_orders = [{'order': o, 'distance': None} for o in all_pending]

    # Mark this driver's notifications as read when they open the board
    driver.notifications.filter(is_read=False).update(is_read=True)

    return render(request, 'ordering_service/driver_board.html', {'nearby_orders': nearby_orders})


@login_required
@require_POST
def accept_order(request, order_id):
    order = get_object_or_404(RideOrder, id=order_id, status='pending')
    order.driver = request.user
    order.status = 'accepted'
    order.save()

    # Notify the rider their request was accepted
    Notification.objects.create(
        recipient=order.rider,
        ride_order=order,
        message=f"Your ride from {order.pickup_location} to {order.dropoff_location} was accepted by {request.user.full_name}!",
    )

    messages.success(request, "Ride accepted! The rider has been notified.")
    return redirect('driver_board')


@login_required
@require_POST
def update_driver_location(request):
    """AJAX endpoint — driver's browser pushes live GPS on dashboard open (Option B)."""
    try:
        lat = float(request.POST.get('lat'))
        lng = float(request.POST.get('lng'))
        request.user.driver_lat = lat
        request.user.driver_lng = lng
        request.user.save(update_fields=['driver_lat', 'driver_lng'])
        return JsonResponse({'status': 'ok'})
    except (TypeError, ValueError):
        return JsonResponse({'status': 'error', 'message': 'Invalid coordinates'}, status=400)


@login_required
def notifications_list(request):
    notifs = request.user.notifications.select_related('ride_order').all()
    return render(request, 'ordering_service/notifications.html', {'notifications': notifs})

from .models import RideReview, CommunityPost, PostComment

@login_required
def ride_history(request):
    if request.user.is_driver():
        rides = request.user.accepted_rides.exclude(status='pending').order_by('-created_at')
    else:
        rides = request.user.ride_orders.order_by('-created_at')
    if request.method == 'POST':
        ride_id = request.POST.get('ride_id')
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        ride = RideOrder.objects.get(id=ride_id)
        if ride.rider == request.user and ride.driver:
            RideReview.objects.create(ride=ride, rider=request.user, driver=ride.driver, rating=rating, comment=comment)
        return redirect('ordering_service:ride_history')
    return render(request, 'ordering_service/ride_history.html', {'rides': rides})

@login_required
def discussions(request):
    if request.method == 'POST':
        if 'new_post' in request.POST:
            content = request.POST.get('content')
            CommunityPost.objects.create(author=request.user, content=content)
        elif 'new_comment' in request.POST:
            post_id = request.POST.get('post_id')
            content = request.POST.get('content')
            post = CommunityPost.objects.get(id=post_id)
            PostComment.objects.create(post=post, author=request.user, content=content)
        return redirect('ordering_service:discussions')
    posts = CommunityPost.objects.all().prefetch_related('comments')
    return render(request, 'ordering_service/discussions.html', {'posts': posts})
