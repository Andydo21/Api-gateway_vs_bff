import pybreaker
import logging

logger = logging.getLogger(__name__)

# Circuit Breaker Configurations
# Trips after 3 failures, stays open for 30 seconds
startup_breaker = pybreaker.CircuitBreaker(
    fail_max=3, 
    reset_timeout=30,
    name="StartupServiceBreaker"
)

user_breaker = pybreaker.CircuitBreaker(
    fail_max=3, 
    reset_timeout=30,
    name="UserServiceBreaker"
)

booking_breaker = pybreaker.CircuitBreaker(
    fail_max=3, 
    reset_timeout=30,
    name="BookingServiceBreaker"
)

# We'll use the default listeners or none for now to avoid AttributeError
