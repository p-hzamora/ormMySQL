from enum import Enum


class ConditionType(Enum):
    EQUAL = "=="
    LESS_THAN = "<"
    GREATER_THAN = ">"
    LESS_THAN_OR_EQUAL = "<="
    GREATER_THAN_OR_EQUAL = ">="
    NOT_EQUAL = "!="
    REGEXP = "REGEXP"
    BETWEEN = "BETWEEN"
    LIKE = "LIKE"
    IN = "IN"
    IS = "IS"
    IS_NOT = "IS NOT"
