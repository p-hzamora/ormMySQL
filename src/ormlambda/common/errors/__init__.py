class DifferentTablesAndVariablesError(Exception):
    def __str__(self) -> str:
        return "The number of tables and the variables used in the lambda select are not 'consistent'"
