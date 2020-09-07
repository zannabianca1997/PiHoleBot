#!/usr/bin/env bash

# find the directory of the script
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"

install_dir="/opt/PiHoleBot"
conf_dir="/etc/opt/PiHoleBot"

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

  printf "Done.\n"
}

uninstall() {
  printf "Removing scripts from %s\n" "$install_dir"
  rm -rf "$install_dir"

  printf "Removing configuration files from %s\n" "$conf_dir" 
  rm -rf "$conf_dir"
}

while getopts 'u' flag; do
  case "${flag}" in
  u)
    uninstall
    exit 0
    ;;
  *)
    print_usage
    exit 1
    ;;
  esac
done
install
exit 0
