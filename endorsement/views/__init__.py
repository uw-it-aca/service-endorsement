from userservice.user import UserService


def get_netid_of_current_user():
    return UserService().get_user()


def get_override_user():
    return UserService().get_override_user()


def get_original_user():
    return UserService().get_original_user()
