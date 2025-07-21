from flask import Flask, request, jsonify
import requests
import re
import json

app = Flask(__name__)

COOKIES = {
    "browserid": "gyokpJlA1epANEJHHu2WHv9UYKMZ6VBVMwRtEBdBnfe2P2C9KfasxP7d-xalea9i8kjkfE5UiVwaQ-Y3",
    "lang": "en",
    "__bid_n": "1982dd8dd414faddca4207",
    "ndus": "YvuYYdkpeHuiE3CnyBdabQ9tcNveCMUziDvsA6bN",
    "csrfToken": "1j1vbsyNIFCL8uQg7rCQVxQI",
    "ndut_fmt": "A431F1A43FF2AAA416DB8AE7F0C6DFDA7996073841D91CF646561EA94A67FA22"
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Android 14; Mobile; rv:140.0) Gecko/140.0 Firefox/140.0",
    "Referer": "https://www.1024terabox.com/",
    "Origin": "https://www.1024terabox.com"
}


def extract_info(page_text):
    """Extracts JSON-like meta data for file list."""
    try:
        match = re.search(r"window\.yunData\s*=\s*(\{.*?\});", page_text)
        if match:
            return json.loads(match.group(1))
    except:
        return None
    return None


@app.route("/api/terabox", methods=["GET"])
def terabox_download():
    link = request.args.get("q")
    if not link:
        return jsonify({"error": "Missing 'q' param"}), 400

    session = requests.Session()
    session.headers.update(HEADERS)
    session.cookies.update(COOKIES)

    try:
        res = session.get(link)
        if res.status_code != 200:
            return jsonify({"error": "Failed to fetch share page"}), 400

        info = extract_info(res.text)
        if not info or "file_list" not in info or not info["file_list"]["list"]:
            return jsonify({"error": "File list not found"}), 400

        file_entry = info["file_list"]["list"][0]
        fs_id = file_entry["fs_id"]
        uk = info.get("uk")
        shareid = info.get("shareid")

        # Step 2: Call filemeta to get actual direct link
        api_url = "https://www.1024terabox.com/share/list"
        params = {
            "app_id": "250528",
            "channel": "chunlei",
            "clienttype": "0",
            "web": "1",
            "shareid": shareid,
            "uk": uk
        }

        post_data = {
            "page": "1",
            "num": "100",
            "order": "time",
            "desc": "1",
            "shareid": shareid,
            "uk": uk
        }

        response = session.post(api_url, params=params, data=post_data)
        meta = response.json()
        dlink = meta["list"][0]["dlink"]

        # Step 3: Fetch direct final redirect link
        final_res = session.get(dlink, allow_redirects=False)
        final_link = final_res.headers.get("Location")

        return jsonify({
            "success": True,
            "filename": file_entry.get("server_filename"),
            "direct_link": final_link
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(port=5000)
    
