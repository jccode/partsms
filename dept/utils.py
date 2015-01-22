# -*- coding: utf-8 -*-

def user_str(user):
    """
    format user

    Arguments:
    - `user`:
    """
    if user.last_name and user.first_name:
        val = user.last_name + user.first_name
    elif user.first_name and not user.last_name:
        val = user.first_name
    else:
        val = user.username
    return val

