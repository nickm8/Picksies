# movie_app/utils.py
import jwt
from django.conf import settings
from django.http import JsonResponse
from .models import MovieNight
import logging

logger = logging.getLogger(__name__)

def generate_movie_night_token(movie_night):
    """Generate JWT token for movie night access"""
    payload = {
        'c': movie_night.access_code
    }
    
    secret = getattr(settings, 'SECRET_KEY')
    token = jwt.encode(payload, secret, algorithm='HS256')
    return token

def verify_movie_night_token(token):
    """Verify JWT token and return movie night"""
    try:
        secret = getattr(settings, 'SECRET_KEY')
        payload = jwt.decode(token, secret, algorithms=['HS256'])
        
        access_code = payload.get('c')
        
        if not access_code:
            logger.warning("Token missing access code")
            return None
            
        movie_night = MovieNight.objects.get(
            access_code=access_code,
            is_active=True
        )
        logger.info(f"Token verified for movie night: {movie_night.title}")
        return movie_night
        
    except jwt.InvalidTokenError as e:
        logger.warning(f"JWT token invalid: {e}")
        return None
    except MovieNight.DoesNotExist:
        logger.warning(f"MovieNight not found for access_code: {access_code}")
        return None
    except Exception as e:
        logger.error(f"Token verification failed: {e}")
        return None

def movie_night_required(view_func):
    """Decorator to require valid movie night token"""
    def wrapper(request, *args, **kwargs):
        token = request.GET.get('t')
        if not token:
            return JsonResponse({'error': 'Missing authentication token'}, status=401)
        
        movie_night = verify_movie_night_token(token)
        if not movie_night:
            return JsonResponse({'error': 'Invalid or expired token'}, status=401)
            
        # Add movie_night to kwargs
        kwargs['movie_night'] = movie_night
        return view_func(request, *args, **kwargs)
    
    return wrapper
