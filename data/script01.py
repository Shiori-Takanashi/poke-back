import json
from ep_info import EP_INFO


new_data = []
for entry in EP_INFO:
    name_value = entry["name"]
    if "-" in name_value:
        parts = name_value.split("-")
        alias = "_".join(part for part in parts)
        mdlclass = "".join(part.capitalize() for part in parts)
    else:
        mdlclass = name_value.capitalize()
        alias = name_value
    filename = "./temp/" + mdlclass.lower() + ".txt"

    new_dict = {"alias": alias, **entry, "model-class": mdlclass, "temp-file": filename}
    new_data.append(new_dict)


with open("ep_info.py", "w", encoding="utf-8") as file:
    file.write("EP_INFO = ")
    file.write(json.dumps(new_data, indent=4, ensure_ascii=False))
