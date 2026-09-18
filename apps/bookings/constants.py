from django.db import models


class BookingStatus(models.TextChoices):
    PENDING   = "pending", "Pending"
    CONFIRMED = "confirmed", "Confirmed"
    CANCELLED = "cancelled", "Cancelled"
    FAILED    = "failed", "Failed"


class BookingFields:
    USER              = "user"
    EVENT             = "event"
    EVENT_ID          = "event_id"
    USER_EMAIL        = "user_email"
    EVENT_TITLE       = "event_title"
    EVENT_START_DATE  = "event_start_date"
    VENDOR_NAME       = "vendor_name"
    SEATS             = "seats"
    TOTAL_PRICE       = "total_price"
    STATUS            = "status"
    RELATION_BOOKINGS = "bookings"

    # Query param filter keys
    FILTER_STATUS = "status"
    FILTER_EVENT  = "event"
    FILTER_USER   = "user"


class BookingUrls:
    CREATE = "create/"                   
    UPDATE = "<pk>/update/"         
    DETAIL = "<pk>/detail/"        
    STATUS = "<pk>/status/"        
    LIST   = "list/"                    
    CLEANUP = "cleanup/"                


class BookingNames:
    CREATE = "booking-create"
    UPDATE = "booking-update"
    DETAIL = "booking-detail"
    STATUS = "booking-status"
    LIST   = "booking-list"
    CLEANUP = "booking-cleanup"

