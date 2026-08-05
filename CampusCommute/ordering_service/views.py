import math
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.contrib import messages
from .models import RideOrder, Notification
from .forms import RideOrderForm, OfferRideForm


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
    """Public board — shows ride requests AND offered rides in separate tabs."""
    request_orders = RideOrder.objects.filter(
        ride_type='request', status__in=['pending', 'accepted']
    ).select_related('rider', 'driver').all()
    raw_offers = RideOrder.objects.filter(
        ride_type='offer', status__in=['pending', 'accepted']
    ).select_related('rider', 'driver').all()

    # Attach seat_range, seat_range_available helpers, and user_has_claimed check
    offer_orders = []
    user = request.user
    for ride in raw_offers:
        ride.seat_range = range(1, ride.offered_seats + 1)
        ride.seat_range_available = range(1, ride.available_seats + 1) if ride.available_seats > 0 else range(0)
        ride.user_has_claimed = False
        if user.is_authenticated:
            ride.user_has_claimed = ride.claims.filter(rider=user).exists()
        offer_orders.append(ride)

    return render(request, 'ordering_service/community_board.html', {
        'request_orders': request_orders,
        'offer_orders': offer_orders,
    })


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
    # Mark all as read when user opens the page
    request.user.notifications.filter(is_read=False).update(is_read=True)
    return render(request, 'ordering_service/notifications.html', {'notifications': notifs})


@login_required
def notification_count(request):
    count = request.user.notifications.filter(is_read=False).count()
    return JsonResponse({'count': count})


from .models import RideReview, CommunityPost, PostComment, RideClaim

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
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        if 'new_post' in request.POST:
            content = request.POST.get('content', '').strip()
            if content:
                post = CommunityPost.objects.create(author=request.user, content=content)
                if is_ajax:
                    return JsonResponse({
                        'status': 'ok',
                        'post_id': post.id,
                        'author': request.user.full_name,
                        'role': request.user.role.title(),
                        'content': content,
                        'timesince': 'just now',
                    })
        elif 'new_comment' in request.POST:
            post_id = request.POST.get('post_id')
            content = request.POST.get('content', '').strip()
            if content and post_id:
                post = CommunityPost.objects.get(id=post_id)
                comment = PostComment.objects.create(post=post, author=request.user, content=content)
                if is_ajax:
                    return JsonResponse({
                        'status': 'ok',
                        'comment_id': comment.id,
                        'post_id': post_id,
                        'author': request.user.full_name,
                        'content': content,
                    })
        # Fallback for non-AJAX (e.g. direct form submit)
        return redirect('discussions')
    posts = CommunityPost.objects.all().prefetch_related('comments')
    return render(request, 'ordering_service/discussions.html', {'posts': posts})


@login_required
def offer_ride(request):
    """Driver posts an available ride with a seat cap."""
    if not request.user.is_driver():
        messages.error(request, "Only drivers can offer rides.")
        return redirect('community_board')

    if request.method == 'POST':
        form = OfferRideForm(request.POST)
        if form.is_valid():
            ride = form.save(commit=False)
            ride.rider = request.user   # driver is stored in rider field as the poster
            ride.driver = request.user  # also the driver
            ride.ride_type = 'offer'
            ride.status = 'pending'
            ride.save()

            # Notify all riders within 10 miles
            User = get_user_model()
            for rider in User.objects.filter(role='rider'):
                Notification.objects.create(
                    recipient=rider,
                    ride_order=ride,
                    message=f"New ride offered: {ride.pickup_location} → {ride.dropoff_location} at {ride.approx_time.strftime('%b %d, %I:%M %p')} — {ride.available_seats} seat(s) available!",
                )

            messages.success(request, "Your ride offer has been posted!")
            return redirect('community_board')
    else:
        form = OfferRideForm()

    return render(request, 'ordering_service/offer_ride.html', {'form': form})


@login_required
@require_POST
def tag_along(request, order_id):
    """Rider claims seats on a driver-offered ride."""
    ride = get_object_or_404(RideOrder, id=order_id, ride_type='offer', status='pending')

    if request.user == ride.driver:
        return JsonResponse({'status': 'error', 'message': 'You cannot tag along on your own ride.'}, status=400)

    seats_requested = int(request.POST.get('seats', 1))
    if seats_requested < 1:
        return JsonResponse({'status': 'error', 'message': 'Must request at least 1 seat.'}, status=400)

    if seats_requested > ride.available_seats:
        return JsonResponse({'status': 'error', 'message': f'Only {ride.available_seats} seat(s) left.'}, status=400)

    # Create or update claim
    claim, created = RideClaim.objects.get_or_create(
        ride_order=ride,
        rider=request.user,
        defaults={'seats_taken': seats_requested},
    )
    if not created:
        # Rider already has a claim — adjust delta
        old_seats = claim.seats_taken
        delta = seats_requested - old_seats
        if delta > ride.available_seats:
            return JsonResponse({'status': 'error', 'message': f'Only {ride.available_seats} more seat(s) available.'}, status=400)
        claim.seats_taken = seats_requested
        claim.save()
        ride.claimed_seats = max(0, ride.claimed_seats + delta)
    else:
        ride.claimed_seats += seats_requested

    ride.save(update_fields=['claimed_seats'])

    # Notify the driver
    Notification.objects.create(
        recipient=ride.driver,
        ride_order=ride,
        message=f"{request.user.full_name} tagged along for {seats_requested} seat(s) on your ride to {ride.dropoff_location}!",
    )

    return JsonResponse({
        'status': 'ok',
        'available_seats': ride.available_seats,
        'claimed_seats': ride.claimed_seats,
        'offered_seats': ride.offered_seats,
    })


from django.http import HttpResponseForbidden
from django.db.models import Q
from .models import ChatMessage, RideClaim

@login_required
def chat_room(request, ride_order_id):
    ride = get_object_or_404(RideOrder, id=ride_order_id)
    
    # Check access permission
    has_access = False
    if ride.ride_type == 'request':
        has_access = (request.user == ride.rider) or (ride.status in ('accepted', 'completed') and request.user == ride.driver)
    elif ride.ride_type == 'offer':
        has_access = (request.user == ride.driver) or ride.claims.filter(rider=request.user).exists()
        
    if not has_access:
        return HttpResponseForbidden("You do not have access to this chat room.")
        
    # Determine participants list
    participants = []
    is_group = (ride.ride_type == 'offer')
    
    if is_group:
        # Add driver and all claiming riders
        if ride.driver:
            participants.append(ride.driver)
        for claim in ride.claims.select_related('rider').all():
            if claim.rider not in participants:
                participants.append(claim.rider)
    else:
        # Show the other user
        if request.user == ride.rider:
            if ride.driver:
                participants.append(ride.driver)
        else:
            participants.append(ride.rider)
            
    return render(request, 'ordering_service/chat_room.html', {
        'ride': ride,
        'participants': participants,
        'is_group': is_group,
        'is_completed': ride.status == 'completed',
    })

@login_required
def get_messages_api(request, ride_order_id):
    ride = get_object_or_404(RideOrder, id=ride_order_id)
    
    # Check access permission
    has_access = False
    if ride.ride_type == 'request':
        has_access = (request.user == ride.rider) or (ride.status in ('accepted', 'completed') and request.user == ride.driver)
    elif ride.ride_type == 'offer':
        has_access = (request.user == ride.driver) or ride.claims.filter(rider=request.user).exists()
        
    if not has_access:
        return JsonResponse({'status': 'error', 'message': 'Forbidden'}, status=403)
        
    messages = ride.chat_messages.select_related('sender').order_by('created_at')
    messages_data = []
    for msg in messages:
        messages_data.append({
            'sender_id': msg.sender.id,
            'sender_name': msg.sender.full_name or msg.sender.username,
            'sender_role': msg.sender.role.title(),
            'profile_picture': msg.sender.profile_picture.url if msg.sender.profile_picture else None,
            'content': msg.get_decrypted_content(),
            'created_at': msg.created_at.strftime('%I:%M %p'),
        })
        
    return JsonResponse({'messages': messages_data})

@login_required
@require_POST
def send_message_api(request, ride_order_id):
    ride = get_object_or_404(RideOrder, id=ride_order_id)
    
    # Check access permission
    has_access = False
    if ride.ride_type == 'request':
        has_access = (request.user == ride.rider) or (ride.status in ('accepted', 'completed') and request.user == ride.driver)
    elif ride.ride_type == 'offer':
        has_access = (request.user == ride.driver) or ride.claims.filter(rider=request.user).exists()
        
    if not has_access:
        return JsonResponse({'status': 'error', 'message': 'Forbidden'}, status=403)
        
    if ride.status == 'completed':
        return JsonResponse({'status': 'error', 'message': 'This ride has ended. The chat is closed.'}, status=400)
        
    content = request.POST.get('content', '').strip()
    if not content:
        return JsonResponse({'status': 'error', 'message': 'Empty message'}, status=400)
        
    msg = ChatMessage(ride_order=ride, sender=request.user)
    msg.encrypt_and_save(content)
    
    return JsonResponse({'status': 'ok'})

@login_required
def map_view(request):
    return render(request, 'ordering_service/map_view.html')

@login_required
def map_data(request):
    user = request.user
    locations = []
    
    # Include current user's live location
    locations.append({
        'id': user.id,
        'name': 'You',
        'role': user.role,
        'profile_picture': user.profile_picture.url if user.profile_picture else None,
        'lat': user.driver_lat,
        'lng': user.driver_lng,
        'is_self': True
    })
    
    matched_user_ids = set()
    
    # Case 1: Accepted request-type rides (one-to-one)
    accepted_requests = RideOrder.objects.filter(
        status='accepted', ride_type='request'
    ).filter(Q(rider=user) | Q(driver=user))
    
    for ride in accepted_requests:
        if ride.rider == user and ride.driver:
            matched_user_ids.add(ride.driver.id)
        elif ride.driver == user and ride.rider:
            matched_user_ids.add(ride.rider.id)
            
    # Case 2: Claimed offer-type rides (one-to-many)
    if user.role == 'rider':
        claims = RideClaim.objects.filter(rider=user).select_related('ride_order__driver')
        for claim in claims:
            if claim.ride_order.driver:
                matched_user_ids.add(claim.ride_order.driver.id)
    elif user.role == 'driver':
        my_offers = RideOrder.objects.filter(driver=user, ride_type='offer')
        claims = RideClaim.objects.filter(ride_order__in=my_offers).select_related('rider')
        for claim in claims:
            matched_user_ids.add(claim.rider.id)
            
    # Get matched user model records
    from django.contrib.auth import get_user_model
    User = get_user_model()
    matched_users = User.objects.filter(id__in=matched_user_ids, driver_lat__isnull=False, driver_lng__isnull=False)
    
    for u in matched_users:
        locations.append({
            'id': u.id,
            'name': u.full_name or u.username,
            'role': u.role,
            'profile_picture': u.profile_picture.url if u.profile_picture else None,
            'lat': u.driver_lat,
            'lng': u.driver_lng,
            'is_self': False
        })
        
    return JsonResponse({'locations': locations})


@login_required
def my_trips(request):
    user = request.user
    
    # 1. Accepted request-type rides (one-to-one)
    active_requests = RideOrder.objects.filter(
        status='accepted', ride_type='request'
    ).filter(Q(rider=user) | Q(driver=user)).select_related('rider', 'driver')
    
    # 2. Offer-type rides (one-to-many)
    # If user is the driver: show pending/accepted offers
    active_offers = []
    if user.is_driver():
        active_offers = RideOrder.objects.filter(
            ride_type='offer', status__in=['pending', 'accepted'], driver=user
        ).select_related('driver')
    
    # If user is a rider: show offers they claimed
    claimed_offers = []
    if user.is_rider():
        claims = RideClaim.objects.filter(rider=user).select_related('ride_order__driver')
        claimed_offers = [claim.ride_order for claim in claims if claim.ride_order.status in ['pending', 'accepted']]
        
    # Combine lists
    active_rides = list(active_requests) + list(active_offers) + list(claimed_offers)
    
    # De-duplicate
    seen_ids = set()
    unique_active_rides = []
    for ride in active_rides:
        if ride.id not in seen_ids:
            seen_ids.add(ride.id)
            unique_active_rides.append(ride)
            
    return render(request, 'ordering_service/my_trips.html', {
        'active_rides': unique_active_rides,
    })


@login_required
@require_POST
def end_ride(request, ride_order_id):
    ride = get_object_or_404(RideOrder, id=ride_order_id)
    if request.user != ride.driver:
        return HttpResponseForbidden("Only the driver can end this ride.")
        
    ride.status = 'completed'
    ride.save(update_fields=['status'])
    
    # Notify passengers
    if ride.ride_type == 'request':
        if ride.rider:
            Notification.objects.create(
                recipient=ride.rider,
                ride_order=ride,
                message=f"Your ride with {request.user.full_name} has ended.",
            )
    elif ride.ride_type == 'offer':
        for claim in ride.claims.select_related('rider').all():
            Notification.objects.create(
                recipient=claim.rider,
                ride_order=ride,
                message=f"Your ride with {request.user.full_name} has ended.",
            )
            
    messages.success(request, "Ride ended successfully.")
    next_url = request.META.get('HTTP_REFERER') or 'my_trips'
    return redirect(next_url)
