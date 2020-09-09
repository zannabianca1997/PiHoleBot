#!/usr/bin/env bash

# find the directory of the script
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"

install_dir="/opt/PiHoleBot"
conf_dir="/etc/opt/PiHoleBot"
log_dir="/var/opt/PiHoleBot"

print_usage() {
  printf "Usage: install [-u]\n"
  printf "Install the bot on the system. Use the -u to uninstall\n"
}

install() {
  printf "Copying scripts to %s\n" "$install_dir"
  cp -r "$DIR/src" "$install_dir"

  printf "Copying configuration files to %s\n" "$conf_dir"
  cp -r "$DIR/conf" "$conf_dir"
  touch "$conf_dir/users.ids"
  touch "$conf_dir/admins.ids"
  printf "%s" "$TOKEN" >"$conf_dir/TOKEN"

  printf "Creating log directory %s\n" "$log_dir"
  mkdir "$log_dir"

  printf "Creating user PiHoleBot to run service\n"
  useradd PiHoleBot

  printf "Giving rights to user"
  # permitting it to launch pihole as sudo
  cp "$DIR/sudo_file" /etc/sudoers.d/PiHoleBot
  chown root:root /etc/sudoers.d/PiHoleBot
  chmod 440 /etc/sudoers.d/PiHoleBot
  # permitting to edit log
  chown PiHoleBot:PiHoleBot "$log_dir"

  printf "Adding service\n"
  cp "$DIR/PiHoleBot.service" /etc/systemd/system/PiHoleBot.service

  printf "Done. Use 'systemctl start PiHoleBot' to launch\n"
}

uninstall() {
  printf "Removing scripts from %s\n" "$install_dir"
  rm -r "$install_dir"

  printf "Removing configuration files from %s\n" "$conf_dir"
  rm -r "$conf_dir"

  printf "Removing log files from %s\n" "$log_dir"
  rm -r "$log_dir"

  printf "Removing user\n"
  userdel PiHoleBot
  rm /etc/sudoers.d/PiHoleBot

  printf "Removing service\n"
  rm /etc/systemd/system/PiHoleBot.service
}

TOKEN=""

while getopts 'urt:' flag; do
  case "${flag}" in
  u)
    uninstall
    exit 0
    ;;
  r)
    uninstall #then go on installing as normal
    ;;
  t)
    TOKEN=$OPTARG
    ;;
  *)
    print_usage
    exit 1
    ;;
  esac
done
install
exit 0
