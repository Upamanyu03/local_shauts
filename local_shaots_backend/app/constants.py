EMAIL_REGEX = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"

class Operations:
    SET = "set"
    INCREASE = "increase"
    DECREASE = "decrease"

    @classmethod
    def get_all(cls):
        return {cls.SET, cls.INCREASE, cls.DECREASE}
class GenericStatuses:
    ACTIVE = "active"
    INACTIVE = "inactive"
    DELETED = "deleted"

    @classmethod
    def get_all(cls):
        return {cls.ACTIVE, cls.INACTIVE, cls.DELETED}
class EmailTemplateType:
    BODY = "body"
    SUBJECT = "subject"