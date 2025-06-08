#!/bin/bash

# ルートディレクトリの位置を動的に取得
ROOT_DIR=$(dirname "$(dirname "$(realpath "$0")")")

echo "プロジェクトルート: $ROOT_DIR"

# SQLite3のDBファイルを削除（存在する場合のみ）
DB_FILE="$ROOT_DIR/db.sqlite3"
if [ -f "$DB_FILE" ]; then
    echo "削除: $DB_FILE"
    rm "$DB_FILE"
else
    echo "DBファイルは存在しません: $DB_FILE"
fi

# マイグレーションファイルを削除（__init__.py を除く）
find "$ROOT_DIR" -type d -name "migrations" | while read -r dir; do
    echo "処理中: $dir"
    find "$dir" -type f -name "*.py" ! -name "__init__.py" -delete
    find "$dir" -type f -name "*.pyc" -delete
done

echo "マイグレーション履歴とDBファイルの削除が完了しました。"
