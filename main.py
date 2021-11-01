"""
Quick and dirty script to generate alfred snippets for emojis

We'll use these files :
https://cdn.jsdelivr.net/npm/emojibase-data@latest/LANG/data.json
"""
import json
import os
import shutil
from typing import Dict, List

import requests
import uuid

import config


def download_emoji_file(language) -> List[Dict]:
    file = requests.get(f"https://cdn.jsdelivr.net/npm/emojibase-data@latest/{language}/data.json")
    return file.json()

def download_shortcodes(language) -> Dict:
    file = requests.get(f"https://cdn.jsdelivr.net/npm/emojibase-data@latest/{language}/shortcodes/emojibase.json")
    return file.json()

def generate_alfred_snippet_file(key, value, cache_dir):
    uid = str(uuid.uuid4())

    content = {
        "alfredsnippet": {
            "snippet": f"{value}",
            "uid": uid,
            "name": f"{value} :{key}:",
            "keyword": f"{key}"
        }
    }
    try:
        with open(f"{cache_dir}/{value} {key} - {uid}.json", "w") as f:
            json.dump(content, f, ensure_ascii=False)
    except OSError:
        pass

def get_shortcodes(shortcodes, hexcode):
    codes = shortcodes.get(hexcode, [])
    if type(codes) is not list:
        codes = [codes]
    return codes

def main():
    emojis_to_convert = {}  # {"shortcode": "emoji"}

    for language in config.languages_to_generate:
        shortcodes = download_shortcodes(language)
        emoji_file = download_emoji_file(language)
        for emoji_info in emoji_file:
            emoji = emoji_info["emoji"]
            for shortcode in get_shortcodes(shortcodes, emoji_info['hexcode']):
                emojis_to_convert[shortcode] = emoji
            if config.enable_skins:
                for skin in emoji_info.get("skins", []):
                    for shortcode in get_shortcodes(shortcodes, skin['hexcode']):
                        emojis_to_convert[shortcode] = skin["emoji"]

    for shortcode, emoji in emojis_to_convert.items():
        print(f":{shortcode}: -> {emoji}")
        generate_alfred_snippet_file(shortcode, emoji, config.cache_dir_def)
        if any((sc.startswith(shortcode) and sc != shortcode) for sc in emojis_to_convert):
          shortcode += ' '
          print(f":{shortcode}:-> {emoji} (deduped version)")
        generate_alfred_snippet_file(shortcode, emoji, config.cache_dir_dedupe)

    shutil.copyfile("icon.png", config.cache_dir_def + "icon.png")
    shutil.copyfile("icon.png", config.cache_dir_dedupe + "icon.png")
    file_name_def = f"./{config.output_dir}Emoji Pack Update.alfredsnippets"
    file_name_dedupe = f"./{config.output_dir}Emoji Pack Update Deduped.alfredsnippets"
    print(f"Saving to {file_name_def}")

    shutil.make_archive(file_name_def, "zip", root_dir=config.cache_dir_def)
    os.rename(file_name_def + ".zip", file_name_def)

    print(f"Saving to {file_name_dedupe}")
    shutil.make_archive(file_name_dedupe, "zip", root_dir=config.cache_dir_dedupe)
    os.rename(file_name_dedupe + ".zip", file_name_dedupe)


if __name__ == '__main__':
    main()