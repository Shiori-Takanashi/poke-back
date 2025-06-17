from ep_info import EP_INFO
import json

# temp-fileを除去
entries = [{k: v for k, v in entry.items() if k != "temp-file"} for entry in EP_INFO]

with open("ep_info.py", "w", encoding="utf-8") as f:
    f.write("EP_INFO = ")
    json.dump(entries, f, indent=4, ensure_ascii=False)
    f.write("\n")
