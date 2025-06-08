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

EP_TYPES: list[tuple[str, str]] = [
    ("species", "pokemon-species"),
    ("pokemon", "pokemon"),
    ("form",    "pokemon-form"),
]

# ------------------
# Django 管理コマンド
# ------------------
class Command(BaseCommand):
    """
    temp フォルダに xxx_idxs.txt を生成し、
    API の count とファイル行数の一致を検証する。
    不一致でも処理は正常終了する。
    """

    # ---------- エントリポイント ----------
    def handle(self, *args, **options):
        logger.start("処理開始")

        # 準備
        temp_dir = Path(__file__).resolve().parent.parent.parent / "temp"
        temp_dir.mkdir(exist_ok=True)

        # 関数01
        if self._check_flags():
            file_logger.info("1.フラグ有効化、確認。")
            self.stdout("1.フラグ有効化、確認。")

        # 関数02
        ep_info = self._build_ep_info(temp_dir)
        file_logger.info("2. urlとfilenameの構築、完了。")
        self.stdout("2. urlとfilenameの構築、完了。")

        # フェーズ03
        if asyncio.run(self._download_and_save_all_indexes(ep_info)):
            file_logger.info("3. IDファイルのダウンロード、完了。")
            self.stdout("3. IDファイルのダウンロード、完了。")
        else:
            return

        # フェーズ04
        file_totals = self._get_file_totals(ep_info)

        # フェーズ05
        api_counts  = asyncio.run(self._fetch_api_counts(ep_info))

        # フェーズ06
        self._validate_counts(api_counts, file_totals)

        logger.finish("処理完了")

    # ----------------------------------------
    # フェーズ01: using=Trueの確認
    # ----------------------------------------
    def _check_flags(self) -> bool:


        # ファイル冒頭の定数から登録名を取得。setであることに注意。
        constant_ep_names = {name for _, name in EP_TYPES}
         # ep_registryアプリで登録されたものをadmin画面から有効にする。
        active_ep_names = set(
            Endpoint.objects.filter(using=True).values_list("name", flat=True)
        )
        # set = set - set
        inactive_ep_names = constant_ep_names - active_ep_names

        if not inactive_ep_names:
            return True

        # spfの順に並び替える。
        if inactive_ep_names:
            ordered_inactive_ep_names = [
                name for _, name in EP_TYPES if name in inactive_ep_names
            ]
            # spfが全て有効化されていれていなければ終了
            file_logger.fairue("using=True 未設定: " + ", ".join(orderd_inactive_ep_names))
            raise ValueError("using=True 未設定: " + ", ".join(orderd_inactive_ep_names))

    # ----------------------------------------
    # Endpoint 情報を辞書化
    # ----------------------------------------
    def _build_ep_info(self, temp_dir: Path) -> dict[str, dict[str, str | Path]]:

        ep_info: dict[str, dict[str, str | Path]] = {}

        # fmt_nameは、"species","pokemon","form"の三つ。
        for fmt_name, ep_name in EP_TYPES:
            # first()???
            url = Endpoint.objects.filter(name=ep_name).values_list("url", flat=True).first()

            # ep_nameが一つでも見つからなければ終了。
            if not url:
                file_logger.failure(f"Endpoint '{ep_name}' が見つかりません。")
                raise ValueError(f"Endpoint '{ep_name}' が見つかりません。")

            # fileは次のコマンドで削除されるので、temp。
            ep_info[fmt_name] = {
                "url": url,
                "temp_file": temp_dir / f"{fmt_name}_idxs.txt",
            }
        # spfの全てのデータをreturn
        return ep_info

    # ----------------------------------------
    # すべての idx をダウンロードして保存
    # ----------------------------------------
    async def _download_and_save_all_indexes(self, ep_info: dict[str, dict]) -> bool:
        async with aiohttp.ClientSession() as session:
            tasks = [
                self._download_and_save(v["url"], v["file"], session)
                for v in ep_info.values()
            ]
            results = await asyncio.gather(*tasks)
            if not all(results):
                file_logger.failure("3. IDファイルのダウンロードに失敗しました。")
                self.stderr.write("3. フェーズ03にてエラー発生。\n")
                return False
            return True





    async def _download_and_save(self, ep_url: str, file_path: Path, session: aiohttp.ClientSession) -> None:
        url = f"{ep_url}?limit=3000"
        indexes: list[int] = []

        while url:
            retry = 1
            # 試行ループ：最大6回（1～5回目）
            while retry <= 5:
                try:
                    async with session.get(url) as res:
                        if res.status != 200:
                            file_logger.failure(f"{url} にて {res.status}")
                            retry += 1
                            continue

                        data = await res.json()
                        urls = [entry["url"] for entry in data.get("results", [])]

                        if not urls:
                            file_logger.failure("URLが含まれていません。調査してください。")
                            self.stderr.write("2. フェーズ02にてエラー発生。\n")
                            return False

                        # URLチェック
                        for url in urls:
                            if not u.startswith("https://pokeapi.co/"):
                                file_logger.failure("未知のURLを検出。調査してください。")
                                self.stderr.write("2. フェーズ02にてエラー発生。\n")
                                return False

                        # インデックス抽出＆変換
                        indexes_str = [u.rstrip("/").split("/")[-1] for u in urls]
                        try:
                            indexes_int = [int(s) for s in indexes_str]
                        except ValueError:
                            file_logger.failure("URLの末尾に数字がありませんでした。調査してください。")
                            self.stderr.write("2. フェーズ02にてエラー発生。\n")
                            return False

                        indexes.extend(indexes_int)

                        next_url = data.get("next")
                        if isinstance(next_url, str) and next_url.startswith("https://pokeapi.co/"):
                            url = next_url
                        else:
                            url = None

                        self.stdout.write("進行中…\n")
                        break  # 試行ループ脱出、外側のループへ。
                except Exception as e:
                    file_logger.failure(f"Fetch error {url}: {e}")
                    file_logger.info("Time sleep 3 seconds.")
                    await asyncio.sleep(3)
                    file_logger.info(f"{url}について再取得を試みます。")
                    retry += 1
            else:
                # retryが上限を超えた場合
                file_logger.failure(f"最大リトライ回数を超えました: {url}")
                self.stderr.write("2. フェーズ02にてエラー発生。\n")
                return False

        # 収集したすべてのindexを書き出し
        try:
            file_path.write_text(
                "\n".join(map(str, sorted(indexes))),
                encoding="utf-8"
            )
        except FileNotFoundError:
            return
        file_logger.success(f"{file_path.name} を保存 ({len(indexes)} 行)")
        return

    # ----------------------------------------
    # API count を取得
    # ----------------------------------------
    async def _fetch_api_counts(self, ep_info: dict[str, dict]) -> dict[str, int]:
        async with aiohttp.ClientSession() as session:
            tasks = {
                key: self._fetch_count(d["url"], session) for key, d in ep_info.items()
            }
            counts = await asyncio.gather(*tasks.values())
            return dict(zip(tasks.keys(), counts))

    async def _fetch_count(
        self, url: str, session: aiohttp.ClientSession
    ) -> int:
        try:
            async with session.get(url) as res:
                if res.status == 200:
                    return int((await res.json())["count"])
        except Exception as e:
            logger.failure(f"Count fetch error {url}: {e}")
        return 0

    # ----------------------------------------
    # ファイル行数を取得
    # ----------------------------------------
    def _get_file_totals(self, ep_info: dict[str, dict]) -> dict[str, int]:
        totals: dict[str, int] = {}
        for key, entry in ep_info.items():
            try:
                totals[key] = len(entry["file"].read_text(encoding="utf-8").splitlines())
            except FileNotFoundError:
                totals[key] = 0
        return totals

    # ----------------------------------------
    # count と total の一致を検証
    # ----------------------------------------
    def _validate_counts(
        self,
        api_counts: dict[str, int],
        file_totals: dict[str, int],
    ) -> None:
        mismatch_found = False
        for key in api_counts:
            api = api_counts[key]
            total = file_totals[key]
            if api != total:
                mismatch_found = True
                msg = f"[不一致] {key:<7} api={api} total={total}"
                logger.warning(msg)
                self.stderr.write(msg + "\n")
            else:
                logger.success(f"[一致]   {key:<7} api=total={api}")

        if not mismatch_found:
            self.stdout.write("すべて一致しました\n")
