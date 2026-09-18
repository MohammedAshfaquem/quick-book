class EventFields:

    VENDOR = "vendor"
    TITLE = "title"
    DESCRIPTION = "description"
    VENUE = "venue"
    START_DATE = "start_date"
    END_DATE = "end_date"
    BOOKING_START_DATE = "booking_start_date"
    BOOKING_END_DATE = "booking_end_date"
    SHOW_START_DATE = "show_start_date"
    SHOW_END_DATE = "show_end_date"
    TOTAL_SEATS = "total_seats"
    AVAILABLE_SEATS = "available_seats"
    RESERVED_SEATS = "reserved_seats"
    MIN_SEATS_PER_BOOKING = "min_seats_per_booking"
    MAX_SEATS_PER_BOOKING = "max_seats_per_booking"
    PRICE = "price"
    IS_ACTIVE = "is_active"

    # Query param filter keys
    FILTER_NAME        = "name"
    FILTER_STATUS      = "status"
    FILTER_SHOW_STATUS = "show_status"
    FILTER_VENDOR      = "vendor"
    SEARCH = "search"


class ShowStatus:
    UPCOMING = "upcoming"
    BOOKING_ENABLED = "booking_enabled"
    RUNNING = "running"
    EXPIRED = "expired"



class EventUrls:
    CREATE = "create/"                   # POST  /api/v1/events/create/
    UPDATE = "<pk>/update/"         # PATCH /api/v1/events/<id>/update/
    DETAIL = "<pk>/detail/"         # GET   /api/v1/events/<id>/detail/
    STATUS = "<pk>/status/"         # PATCH /api/v1/events/<id>/status/
    LIST   = "list/"                     # GET   /api/v1/events/list/


class EventNames:
    CREATE = "event-create"
    UPDATE = "event-update"
    DETAIL = "event-detail"
    STATUS = "event-status"
    LIST   = "event-list"
