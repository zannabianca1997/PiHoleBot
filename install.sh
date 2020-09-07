#!/usr/bin/env bash

# find the directory of the script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

install_dir="/opt/PiHoleBot"
conf_dir="/etc/opt/PiHoleBot"

echo "Creating directories"
mkdir $install_dir
mkdir $conf_dir

echo "Copying source to directory"
cp "$DIR/src/*" $install_dir/

echo "Copying configuration files"
mv "$DIR/conf" $conf_dir/
touch $conf_dir/users.ids
touch $conf_dir/admins.ids

echo "Done."
exit 0