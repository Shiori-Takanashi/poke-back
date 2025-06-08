# ------------------
# imports
# ------------------
from __future__ import annotations

import asyncio
from pathlib import Path

import aiohttp
from django.core.management.base import BaseCommand

from utils.cmd_logger_file import setup_logger_file
from ep_registry.models import Endpoint

file_logger = setup_logger_file(__name__.split('.')[-1])

# ---------- 定数 ----------
# DBに登録する際の名前, エンドポイント名、のタプルです。
# DBでpokemon-がついていると面倒であり、
# かつ、最終的にspfのデータはmonsterモデルに統合されます。
# ポケモンプレイヤーの私が悩んで考えた結果、
# このような区分が必要だという結論です。
# 特殊なポケモンの扱いが難しいのです。
# pokemon-を略した形式を「登録名」と呼ぶことにします。

NAME_AND_EP = list[tuple[str, str]] = [
    ("species", "pokemon-species"),
    ("pokemon", "pokemon"),
    ("form",    "pokemon-form"),
]

class Command(BaseCommand):

    def handle(self, *args, **options):
        pass

    def load_
