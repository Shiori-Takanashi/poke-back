#!/bin/bash

# shiori のパスワードを使って sudo 経由で PostgreSQL にアクセスし、
# pokeback データベースを削除する

echo "Obear0311" | sudo -S -u postgres psql -c "DROP DATABASE IF EXISTS pokeback;"
