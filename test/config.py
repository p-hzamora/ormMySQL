from decouple import config

USERNAME = config("USERNAME")
PASSWORD = config("PASSWORD")
HOST = config("HOST")


config_dict: dict[str, str] = {
    "username": USERNAME,
    "password": PASSWORD,
    "host": HOST,
}
