from ep_info import EP_INFO
import json

new_key = "ids_temp_file"

outs = [
    {**entry, new_key: f"pipe/temp/new_key_{entry['ident']}.txt"} for entry in EP_INFO
]

with open("ep_info.py", "w", encoding="utf-8") as f:
    f.write("EP_INFO = ")
    json.dump(outs, f, indent=4, ensure_ascii=False)
