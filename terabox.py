import requests
import re
import json
import base64

COOKIES = {
    "ndus": "YedI9dkpeHuiW8-jHcGE6f3dCVcDixRtTsUGPUja",
    "ndut_fmt": "A3BA526605A05842EFF217FA59C1B444B6763A807FB493F7B5F0983AAEF70AAB",
    "csrfToken": "zY1F7nKNn_mZc1tICbrA10b0",
    "browserid": "ZkAlz0GQbsDWGVMmDMzwfH-Ilb07Nz0mx-rMMQi3HD3QQ4DPKJQnv9-G_dw=",
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Android 14; Mobile; rv:140.0) Gecko/140.0 Firefox/140.0",
    "Referer": "https://terabox.com/",
    "Content-Type": "application/json",
}


def get_direct_link(share_url):
    session = requests.Session()
    session.headers.update(HEADERS)
    session.cookies.update(COOKIES)

    # Extract short link code
    match = re.search(r'/s/([a-zA-Z0-9]+)', share_url)
    if not match:
        raise Exception("Invalid Terabox URL format")

    share_id = match.group(1)

    # Step 1: Get share meta
    api_meta = "https://www.terabox.com/share/list"
    params = {
        "app_id": "250528",
        "shorturl": share_id,
        "root": "1",
    }

    res = session.get(api_meta, params=params)
    data = res.json()

    if "list" not in data:
        raise Exception("Invalid or expired link")

    file_list = []
    for item in data["list"]:
        file_info = {
            "filename": item["server_filename"],
            "size": item["size"],
            "fs_id": item["fs_id"],
            "isdir": item["isdir"],
        }
        file_list.append(file_info)

    # Step 2: Get real download link (fetch download URL from play link)
    direct_links = []

    for file in file_list:
        if file["isdir"] == 1:
            continue  # Skip folders for now

        # Build encoded URL for stream access (preview bypass)
        fs_id = file["fs_id"]
        dlink_api = f"https://www.terabox.com/api/download"
        payload = {
            "app_id": "250528",
            "shorturl": share_id,
            "fs_id": fs_id,
            "timestamp": 0,
            "sign": "",
        }

        res2 = session.post(dlink_api, json=payload)
        resp_json = res2.json()
        real_url = resp_json.get("url") or resp_json.get("downloadlink")

        direct_links.append({
            "filename": file["filename"],
            "size": file["size"],
            "download_url": real_url
        })

    return {
        "files": direct_links,
        "share_id": share_id,
        "status": "success"
    }
  
