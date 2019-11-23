#!/bin/bash

# database dependencies
# ODBC may be dumb and may be required to update /etc/odbcinst.ini
# to include abs path to libs e.g. /usr/lib/x86_64-linux-gnu/odbc/%the-lib.so%

apt install -y unixodbc-dev libsqliteodbc
