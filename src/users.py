import logging

from setup import user_ids, admin_ids

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

with open(user_ids) as user_file:
    users_list = [int(line) for line in user_file]

with open(admin_ids) as admin_file:
    admins_list = [int(line) for line in admin_file]

logger.info(f"Loaded {len(users_list)} users, of which {len(admins_list)} are administrators")


def add_user(user_id):
    global admins_list, users_list
    assert user_id not in users_list
    logger.info(f"Adding user {user_id} to the userlist")
    users_list.append(user_id)
    with open(user_ids, "w") as user_file:
        user_file.write("\n".join(str(user) for user in users_list))


def remove_user(user_id):
    global admins_list, users_list
    assert user_id in users_list
    assert len(user_ids) > 1
    logger.info(f"Removing user {user_id}")
    if user_id in admins_list:
        remove_admin(user_id)
    users_list.remove(user_id)
    with open(user_ids, "w") as user_file:
        user_file.write("\n".join(str(user) for user in users_list))


def add_admin(user_id):
    global admins_list, users_list
    assert user_id in users_list
    assert user_id not in admins_list
    logger.info(f"Making user {user_id} admin")
    admins_list.append(user_id)
    with open(admin_ids, "w") as admin_file:
        admin_file.write("\n".join(str(admin) for admin in admins_list))


def remove_admin(user_id):
    global admins_list, users_list
    assert user_id in users_list
    assert user_id in admins_list
    logger.info(f"Removing admin {user_id}")
    admins_list.remove(user_id)
    with open(admin_ids, "w") as admin_file:
        admin_file.write("\n".join(str(admin) for admin in admins_list))
