
class VendorFields:

    COMPANY_NAME  = "company_name"
    CONTACT_EMAIL = "contact_email"
    CONTACT_PHONE = "contact_phone"
    DESCRIPTION   = "description"
    IS_ACTIVE     = "is_active"

    # Query param filter keys
    FILTER_NAME   = "name"
    FILTER_STATUS = "status"


class VendorUrls:

    CREATE = "create/"                  
    UPDATE = "<pk>/update/"           
    DETAIL = "<pk>/detail/"         
    STATUS = "<pk>/status/"         
    LIST   = "list/"                       


class VendorNames:

    CREATE = "vendor-create"
    UPDATE = "vendor-update"
    DETAIL = "vendor-detail"
    STATUS = "vendor-status"
    LIST   = "vendor-list"
