from setup import user_ids, admin_ids

with open(user_ids) as user_file:
    users_list = [int(line) for line in user_file]

with open(admin_ids) as admin_file:
    admins_list = [int(line) for line in admin_file]
