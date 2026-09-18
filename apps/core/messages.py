class Messages:

    class Validation:
        SUCCESS = "Validation successful."

    class Auth:
        LOGOUT_SUCCESS = "Logged out successfully."
        REGISTER_SUCCESS = "Account created successfully."
        LOGIN_SUCCESS = "Logged in successfully."
        PASSWORD_CHANGED = "Password changed successfully."
        STAFF_REQUIRED = "Access denied. Staff permissions required."
        WELCOME_BACK = "Welcome back, {email}!"
        INVALID_CREDENTIALS = "Invalid staff credentials or permission denied."
        PASSWORDS_DO_NOT_MATCH = "Passwords do not match."

    class Vendor:
        CREATED_SUCCESS = "Vendor profile created successfully."
        CREATED_NAME_SUCCESS = "Vendor '{company_name}' created successfully!"
        UPDATED_SUCCESS = "Vendor profile updated successfully."
        UPDATED_NAME_SUCCESS = "Vendor '{company_name}' updated successfully!"
        SUBMIT_SUCCESS = "Vendor details validated successfully. Ready for confirmation."
        EMAIL_EXISTS = "A vendor with the email '{email}' already exists. Please enter a unique contact email address."
        STATUS_UPDATED = "Vendor '{company_name}' status updated to {status}."

    class Event:
        """Event success and validation messages."""

        CREATED_SUCCESS = "Event created successfully."
        CREATED_TITLE_SUCCESS = "Event '{title}' created successfully!"
        UPDATED_SUCCESS = "Event updated successfully."
        UPDATED_TITLE_SUCCESS = "Event '{title}' updated successfully!"
        SUBMIT_SUCCESS = "Event details validated successfully. Ready for confirmation."
        START_DATE_IN_FUTURE = "Event start date must be in the future."
        END_DATE_IN_FUTURE = "Event end date must be in the future."
        END_DATE_AFTER_START = "Event end date must be after event start date."
        BOOKING_START_BEFORE_START = "Booking start date must be before event start date."
        BOOKING_END_AFTER_BOOKING_START = "Booking end date must be after booking start date."
        BOOKING_END_CANNOT_EXCEED_START = "Booking end date cannot be after event start date."
        INACTIVE_VENDOR = "Cannot assign event to an inactive vendor."
        SEATS_MINIMUM = "Total seats must be at least 1."
        MIN_SEATS_AT_LEAST_ONE = "min_seats_per_booking must be at least 1."
        MAX_SEATS_GE_MIN_SEATS = "max_seats_per_booking must be greater than or equal to min_seats_per_booking."
        MAX_SEATS_LE_TOTAL_SEATS = "max_seats_per_booking cannot exceed total_seats."
        VENUE_SCHEDULE_CONFLICT = "An event is already scheduled at venue '{venue}' between {start} and {end}. Please select a different venue or another date/time slot."
        STATUS_UPDATED = "Event '{title}' status updated to {status}."
        BOOKING_START_BEFORE_EVENT_START = "booking_start_date cannot be before event start_date."
        BOOKING_END_AFTER_EVENT_END = "booking_end_date cannot be after event end_date."
        SHOW_START_BEFORE_EVENT_START = "show_start_date cannot be before event start_date."
        SHOW_END_AFTER_EVENT_END = "show_end_date cannot be after event end_date."
        SHOW_END_AFTER_SHOW_START = "show_end_date must be strictly after show_start_date."
        BOOKING_START_AFTER_SHOW_START = "booking_start_date cannot be after show_start_date."
        BOOKING_END_AFTER_SHOW_START = "booking_end_date cannot be after show_start_date."

        # Warning messages
        WARN_DEACTIVATE_RUNNING = "Deactivating event '{title}' while it is currently RUNNING is highly risky."
        WARN_DEACTIVATE_BOOKED = "Deactivating '{title}' will affect {count} booked user(s)."
        WARN_EDIT_RUNNING = "Event '{title}' is currently RUNNING. Editing details of a running event is risky."
        WARN_EDIT_BOOKING_ENABLED = "Booking is currently ENABLED for '{title}'. Editing details will affect {count} booked user(s)."
        WARN_EDIT_EXPIRED = "Event '{title}' has EXPIRED. Editing details of an expired event is risky."
        WARN_SEATS_REDUCED = "Reducing total seats to {new_total} is less than currently booked seats ({count})."

    class Booking:
        BOOKED_SUCCESS = "Tickets booked successfully."
        CANCELLED_SUCCESS = "Booking cancelled successfully."
        CANCELLED_RESTORED = "Booking cancelled and seats restored!"
        SUBMIT_SUCCESS = "Booking details validated successfully. Ready for confirmation."
        BOOKING_NOT_OPEN = "Booking is only allowed when event status is BOOKING_ENABLED and event is active."
        EVENT_INACTIVE = "Cannot book an inactive event."
        EVENT_NOT_FOUND = "Event not found."
        SEATS_UNAVAILABLE = "Only {available} seats remaining (requested {requested})."
        MIN_SEATS_NOT_MET = "At least {min_seats} seat(s) required per booking."
        MAX_LIMIT_REACHED = "Maximum limit reached. You can book at most {max_seats} seat(s) per booking."
        PAYMENT_GATEWAY_ENABLED = "Payment Gateway is enabled. Booking status updates are managed automatically via payment webhooks."
        STATUS_UPDATED = "Booking status successfully updated to '{status}'."
        STATUS_INVALID = "Invalid booking status specified."

    class User:
        STATUS_UPDATED = "User '{email}' status updated to {role}."
        CANNOT_MODIFY_SELF = "You cannot modify your own staff privileges."
