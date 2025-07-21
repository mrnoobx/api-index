from flask import Flask, request, jsonify
import aiohttp
import asyncio
import logging
from urllib.parse import parse_qs, urlparse

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# -- Use working cookies for private/folder shares --
cookies = {
    'PANWEB': '1',
    'browserid': '3y0kiWkfKhPHtg5J8dZFSYtwNzncsGY7n3JOtIJsdZ6Wo4XfJxNeA28UtIE=',
    'lang': 'en',
    '__bid_n': '1900b9f02442253dfe4207',
    'ndut_fmt': '3ABC40FE764692D905796B3BF93947ADFDC570385C17E3A68137C9D7451429E0',
    '__stripe_mid': 'b85d61d2-4812-4eeb-8e41-b1efb3fa2a002a54d5',
    'ndus': 'YylKpiCteHuiYEqq8n75Tb-JhCqmg0g4YMH03MYD',
    'csrfToken': '_CFePPJLR7i9z5IPx1cQydow',
    '__stripe_sid': 'b2997993-3227-4e11-a688-c355d62839c678db3c',
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Accept': '*/*',
    'Connection': 'keep-alive',
}

def find_between(text, start, end):
    try:
        return text.split(start, 1)[1].split(end, 1)[0]
    except IndexError:
        return ""

async def get_formatted_size(size_bytes):
    try:
        size_bytes = int(size_bytes)
        if size_bytes >= 1024 ** 2:
            return f"{size_bytes / (1024 ** 2):.2f} MB"
        elif size_bytes >= 1024:
            return f"{size_bytes / 1024:.2f} KB"
        else:
            return f"{size_bytes} bytes"
    except:
        return "unknown"

async def fetch_link_data(url, get_direct_links=False):
    async with aiohttp.ClientSession(cookies=cookies, headers=headers) as session:
        try:
            async with session.get(url) as resp:
                text = await resp.text()
                js_token = find_between(text, 'fn%28%22', '%22%29')
                log_id = find_between(text, 'dp-logid=', '&')
                if not js_token or not log_id:
                    return None

                request_url = str(resp.url)
                if 'surl=' not in request_url:
                    return None
                surl = request_url.split('surl=')[1]

                params = {
                    'app_id': '250528',
                    'web': '1',
                    'channel': 'dubox',
                    'clienttype': '0',
                    'jsToken': js_token,
                    'dplogid': log_id,
                    'page': '1',
                    'num': '20',
                    'order': 'time',
                    'desc': '1',
                    'site_referer': request_url,
                    'shorturl': surl,
                    'root': '1'
                }

                async with session.get('https://www.1024tera.com/share/list', params=params) as res:
                    data = await res.json()

                if 'list' not in data:
                    return None

                files = data['list']

                if files[0].get('isdir') == "1":
                    params.update({
                        'dir': files[0]['path'],
                        'order': 'asc',
                        'by': 'name',
                    })
                    params.pop('desc', None)
                    params.pop('root', None)

                    async with session.get('https://www.1024tera.com/share/list', params=params) as res2:
                        data = await res2.json()
                        if 'list' not in data:
                            return None
                        files = data['list']

                results = []
                for f in files:
                    file_info = {
                        "file_name": f.get("server_filename"),
                        "size": await get_formatted_size(f.get("size", 0)),
                        "size_bytes": f.get("size", 0),
                        "thumb": f.get("thumbs", {}).get("url3", ""),
                        "dlink": f.get("dlink")
                    }

                    if get_direct_links:
                        async with session.head(f.get("dlink"), headers=headers) as r:
                            file_info["direct_link"] = r.headers.get("location")

                    results.append(file_info)

                return results
        except Exception as e:
            logging.error(f"Fetch error: {e}")
            return None

@app.route('/')
def home():
    return jsonify({'status': 'ok', 'message': 'TeraBox API Working', 'contact': '@vip_labani'})

@app.route('/api')
async def api():
    url = request.args.get('url')
    if not url:
        return jsonify({'status': 'error', 'message': 'Missing url parameter'})
    data = await fetch_link_data(url, get_direct_links=False)
    return jsonify({
        'ShortLink': url,
        'Extracted Info': data,
        'status': 'success' if data else 'error'
    })

@app.route('/api2')
async def api2():
    url = request.args.get('url')
    if not url:
        return jsonify({'status': 'error', 'message': 'Missing url parameter'})
    data = await fetch_link_data(url, get_direct_links=True)
    return jsonify({
        'ShortLink': url,
        'Extracted Files': data,
        'status': 'success' if data else 'error'
    })

@app.route('/direct', methods=['GET'])
async def get_direct_metadata():
    url = request.args.get('url')
    if not url or not url.startswith("http"):
        return jsonify({'status': 'error', 'message': 'Invalid or missing URL'})

    try:
        async with aiohttp.ClientSession() as session:
            async with session.head(url, allow_redirects=True) as res:
                info = {
                    'Content-Type': res.headers.get('Content-Type'),
                    'Content-Length': res.headers.get('Content-Length'),
                    'Accept-Ranges': res.headers.get('Accept-Ranges'),
                    'Last-Modified': res.headers.get('Last-Modified'),
                    'Direct-Link': str(res.url)
                }
                return jsonify({'status': 'success', 'Metadata': info})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/help')
def help():
    return jsonify({
        'Usage': 'Pass `url` as query parameter',
        'Example1': '/api?url=https://terafileshare.com/s/xxx',
        'Example2': '/api2?url=https://terafileshare.com/s/xxx',
        'DirectLink': '/direct?url=https://d8.freeterabox.com/file/xyz.mp4'
    })
    
