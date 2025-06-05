from __future__ import annotations

import json
from pathlib import Path

from django.core.management.base import BaseCommand
from ep_registry.models import Endpoint


class Command(BaseCommand):
    help = "JSONファイル all_ep.json の内容をDBに登録する（description, using は空）"

    def handle(self, *args, **options):
        self.delete_ep()
        self.register_ep()

    def delete_ep(self):
        Endpoint.objects.all().delete()

    def register_ep(self):
        json_path = Path(__file__).resolve().parent.parent.parent / "data" / "all_ep.json"
        with open(json_path, "r", encoding="utf-8") as f:
            ep_list = json.load(f)

        objects = []
        for idx, ep in enumerate(ep_list, start=1):
            url = ep["url"]
            if not url.startswith("https://pokeapi.co/api/"):
                raise ValueError(f"不正なURL: {url}")

            objects.append(Endpoint(
                id=idx,
                category=ep["category"],
                name=ep["name"],
                url=url,
                description="",
                using=False,
            ))

        Endpoint.objects.bulk_create(objects, ignore_conflicts=False)
