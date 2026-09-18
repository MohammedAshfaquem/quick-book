class StatusChoices:
    ACTIVE   = "active"
    INACTIVE = "inactive"


class FilterParams:
    NAME   = "name"
    STATUS = "status"
    SEARCH = "search"


class CommonFields:
    ID              = "id"
    CREATED_AT      = "created_at"
    UPDATED_AT      = "updated_at"
    IS_ACTIVE       = "is_active"

    UPDATED_AT_DESC = "-updated_at"
    CREATED_AT_DESC = "-created_at"


class ModuleNames:

    VENDOR    = "vendor"
    VENDORS   = "vendors"
    EVENT     = "event"
    EVENTS    = "events"
    BOOKING   = "booking"
    BOOKINGS  = "bookings"
    REFERRAL  = "referral"
    REFERRALS = "referrals"
    USER      = "user"
    USERS     = "users"


class ActionType:
    SUBMIT  = "submit"
    WARNING = "warning"
    CONFIRM = "confirm"


class VerboseNames:
    class User:
        NAME = "User"
        PLURAL = "Users"

    class Vendor:
        NAME = "Vendor"
        PLURAL = "Vendors"

    class Event:
        NAME = "Event"
        PLURAL = "Events"

    class Booking:
        NAME = "Booking"
        PLURAL = "Bookings"

    class ReferralNode:
        NAME = "Referral Node"
        PLURAL = "Referral Nodes"





