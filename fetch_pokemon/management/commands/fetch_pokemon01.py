# ------------------
# コマンドの基本インポート
# ------------------

# クラス定義の順序の自由化のインポート
from __future__ import annotations

# 必須級のインポート
from pathlib import Path
from utils.cmd_logger_setup import setup_logger

# 同期処理のインポート（出来れば使わない。非同期の練習のため。）
# import requests

# Json処理のインポート
import json

# 非同期処理のインポート（簡単な処理でも非同期を練習したい。）
import asyncio
import aiohttp
# import aiofiles # json処理と併用することが多いはず。

# Djangoコマンドのインポート
from django.core.management.base import BaseCommand

# モデルのインポート
from ep_registry.models import Endpoint
from fetch_pokemon.models import PokemonSpecies, Pokemon, PokemonForm

# コマンド用のロガーをセットアップ（引数はコマンド名）
logger = setup_logger(__name__.split('.')[-1])

# ------------------
# コマンドクラスの定義
# ------------------

class Command(BaseCommand):

    def handle(self, *args, **options):
        logger.start("処理開始")
        if not self.check_using_flag():
            self.stderr.write("Using flag is not set correctly for required endpoints.")
            return
        s_ep, p_ep, f_ep = self.get_base_url()

        dir_path = Path(__file__).resolve().parent.parent.parent / "temp"
        dir_path.mkdir(exist_ok=True)

        s_file_path = dir_path / "species_idxs.txt"
        p_file_path = dir_path / "pokemon_idxs.txt"
        f_file_path = dir_path / "form_idxs.txt"

        result = asyncio.run(self.request_of_urls(s_ep, p_ep, f_ep, s_file_path, p_file_path, f_file_path))

        s_total, p_total, f_total = self.get_totals(s_file_path, p_file_path, f_file_path)
        s_count, p_count, f_count = asyncio.run(self.get_counts(s_ep, p_ep, f_ep))


        if result:
            self.stdout.write("Index files have been created successfully.")
        else:
            self.stderr.write("An error occurred while creating index files.")
        logger.finish("処理完了")



    def check_using_flag(self):
        names = ["pokemon-species", "pokemon", "pokemon-form"]
        flag_names = Endpoint.objects.filter(using=True).values_list("name", flat=True)
        for name in names:
            if name not in flag_names:
                raise ValueError(f"{name}で、using=Trueが設定されていません。")
        return True

    def get_base_url(self):
        s_ep = Endpoint.objects.filter(name="pokemon-species").values_list("url", flat=True).first()
        p_ep = Endpoint.objects.filter(name="pokemon").values_list("url", flat=True).first()
        f_ep = Endpoint.objects.filter(name="pokemon-form").values_list("url", flat=True).first()
        if not s_ep or not p_ep or not f_ep:
            raise ValueError("必要なエンドポイントが見つかりません。")
        return s_ep, p_ep, f_ep

    async def request_of_urls(self, s_ep, p_ep, f_ep, s_file_path, p_file_path, f_file_path):
        async with aiohttp.ClientSession() as session:
            tasks = [
                self.get_existing_idxs(s_ep, s_file_path, session),
                self.get_existing_idxs(p_ep, p_file_path, session),
                self.get_existing_idxs(f_ep, f_file_path, session)
            ]
            results = await asyncio.gather(*tasks)
            if all(results):
                self.stdout.write("All index files have been successfully created.")
                return True
            else:
                self.stderr.write("An error occurred while creating index files.")
                return False

    async def get_existing_idxs(self, base_url, filepath, session):
        existing_idxs = set()
        url = f"{base_url}?limit=3000"
        while True:
            try:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        for item in data["results"]:
                            idx = int(item["url"].split("/")[-2])
                            existing_idxs.add(idx)
                        url = data.get("next", None)
                        # print("get next url !") <= デバッグ用
                        if not url:
                            with open(filepath, "w", encoding="utf-8") as file:
                                file.write("\n".join(map(str, sorted(existing_idxs))))
                            return True
            except Exception as e:
                self.stderr.write(f"Error fetching {base_url}: {e}")
                return False

    def get_totals(self, s_file_path, p_file_path, f_file_path):
        try:
            with open(s_file_path, "r", encoding="utf-8") as file:
                s_total = len(file.readlines())
            with open(p_file_path, "r", encoding="utf-8") as file:
                p_total = len(file.readlines())
            with open(f_file_path, "r", encoding="utf-8") as file:
                f_total = len(file.readlines())
            return s_total, p_total, f_total
        except FileNotFoundError as e:
            self.stderr.write(f"File not found: {e}")
            return 0, 0, 0

    async with def get_counts(self, s_url, p_url, f_url):
        async with aiohttp.ClientSession() as session:
            tasks = [
                self.get_count(s_url, session),
                self.get_count(p_url, session),
                self.get_count(f_url, session)
            ]
        return s_count, p_count, f_count = await asyncio.gather(*tasks)

    async with def get_count(self, url, session):
        count = 0
        try:
            with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    count = data["count"]
        except Exception as e:
            self.stderr.write(f"Error fetching count from {url}: {e}")
        return count
