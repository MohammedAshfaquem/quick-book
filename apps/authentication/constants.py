class AuthUrls:
    REGISTER = "register/"
    LOGIN = "login/"
    LOGOUT = "logout/"
    TOKEN_REFRESH = "token/refresh/"
    CURRENT_USER = "current-user/"
    USERS_LIST = "users/"
    CHANGE_PASSWORD = "change-password/"


class AuthNames:
    REGISTER = "auth-register"
    LOGIN = "auth-login"
    LOGOUT = "auth-logout"
    TOKEN_REFRESH = "auth-token-refresh"
    CURRENT_USER = "auth-current-user"
    USERS_LIST = "auth-users-list"
    CHANGE_PASSWORD = "auth-change-password"


class UserFields:
    EMAIL = "email"
    USERNAME = "username"
    FIRST_NAME = "first_name"
    LAST_NAME = "last_name"
    PASSWORD = "password"
    PASSWORD_CONFIRM = "password_confirm"
    CURRENT_PASSWORD = "current_password"
    NEW_PASSWORD = "new_password"
    NEW_PASSWORD_CONFIRM = "new_password_confirm"
    REFERRAL_CODE = "referral_code"
    REFERRED_BY = "referred_by"
    IS_STAFF = "is_staff"
    IS_ACTIVE = "is_active"
    DATE_JOINED = "date_joined"
    DATE_JOINED_DESC = "-date_joined"
    RELATION_REFERRALS = "referrals"


class JWTFields:
    ACCESS = "access"
    REFRESH = "refresh"
