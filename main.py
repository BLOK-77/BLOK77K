# main.py - Shadow Downloader (نسخة متكاملة بملف واحد)
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
import uvicorn
import os
import subprocess
import sys
import re
from pathlib import Path

# ========== تثبيت المكتبات تلقائياً ==========
def install_packages():
    packages = ['yt-dlp', 'instaloader', 'httpx', 'aiohttp']
    for pkg in packages:
        try:
            __import__(pkg.replace('-', '_'))
        except ImportError:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', pkg])

install_packages()

# ========== استيراد المكتبات ==========
import yt_dlp
import instaloader
import httpx
import asyncio
import shutil
from datetime import datetime

# ========== إعداد التطبيق ==========
app = FastAPI()

# مجلد التحميلات
DOWNLOAD_DIR = Path("downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)

# ========== كود HTML كامل داخل Python ==========
HTML_CODE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Shadow Downloader - تحميل وسائط</title>
    
    <!-- Google AdSense -->
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-xxxxxxxxxxxxxxxx" 
     crossorigin="anonymous"></script>
    
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0f0f1f 0%, #1a1a2e 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
            color: #fff;
        }
        .container {
            background: rgba(255,255,255,0.05);
            backdrop-filter: blur(12px);
            border-radius: 24px;
            padding: 40px;
            max-width: 700px;
            width: 100%;
            border: 1px solid rgba(255,255,255,0.1);
            box-shadow: 0 25px 50px rgba(0,0,0,0.5);
        }
        h1 {
            font-size: 2.5rem;
            text-align: center;
            margin-bottom: 10px;
            background: linear-gradient(45deg, #f093fb 0%, #f5576c 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .subtitle {
            text-align: center;
            color: #aaa;
            margin-bottom: 30px;
            font-size: 0.9rem;
        }
        .input-group {
            display: flex;
            flex-direction: column;
            gap: 15px;
        }
        input[type="url"] {
            padding: 18px 20px;
            border-radius: 16px;
            border: 2px solid rgba(255,255,255,0.1);
            background: rgba(255,255,255,0.05);
            color: #fff;
            font-size: 1rem;
            transition: all 0.3s;
        }
        input[type="url"]:focus {
            outline: none;
            border-color: #f5576c;
            background: rgba(255,255,255,0.08);
        }
        button {
            padding: 18px;
            border: none;
            border-radius: 16px;
            background: linear-gradient(45deg, #f093fb 0%, #f5576c 100%);
            color: #fff;
            font-size: 1.2rem;
            font-weight: bold;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
            box-shadow: 0 8px 24px rgba(245,87,108,0.3);
        }
        button:hover {
            transform: scale(1.02);
            box-shadow: 0 12px 32px rgba(245,87,108,0.5);
        }
        button:active {
            transform: scale(0.98);
        }
        .status {
            margin-top: 25px;
            padding: 15px;
            border-radius: 12px;
            background: rgba(255,255,255,0.05);
            text-align: center;
            min-height: 60px;
            display: flex;
            align-items: center;
            justify-content: center;
            word-break: break-all;
        }
        .status.success {
            background: rgba(46, 213, 115, 0.15);
            border: 1px solid #2ed573;
        }
        .status.error {
            background: rgba(255, 71, 87, 0.15);
            border: 1px solid #ff4757;
        }
        .ads-container {
            margin: 30px 0 20px;
            padding: 15px;
            background: rgba(255,255,255,0.03);
            border-radius: 12px;
            border: 1px dashed rgba(255,255,255,0.1);
            text-align: center;
            min-height: 100px;
        }
        .footer {
            margin-top: 25px;
            text-align: center;
            font-size: 0.7rem;
            color: #666;
        }
        .badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            background: rgba(245,87,108,0.2);
            color: #f5576c;
            font-size: 0.7rem;
            margin-top: 5px;
        }
        .clear-btn {
            background: rgba(255,255,255,0.05);
            color: #888;
            padding: 8px 16px;
            border-radius: 8px;
            border: 1px solid rgba(255,255,255,0.1);
            cursor: pointer;
            font-size: 0.8rem;
            margin-top: 10px;
        }
        .clear-btn:hover {
            background: rgba(255,255,255,0.1);
        }
        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid rgba(255,255,255,0.3);
            border-radius: 50%;
            border-top-color: #fff;
            animation: spin 1s ease-in-out infinite;
        }
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>⚡ Shadow Downloader</h1>
        <p class="subtitle">YouTube • TikTok • Instagram • Twitter • Facebook • Telegram • Snapchat</p>
        
        <form id="downloadForm" class="input-group">
            <input type="url" id="urlInput" placeholder="الصق رابط الفيديو أو الصورة..." required>
            <button type="submit" id="downloadBtn">🚀 تحميل بأعلى دقة</button>
        </form>

        <!-- إعلان Google -->
        <div class="ads-container">
            <ins class="adsbygoogle"
                 style="display:block"
                 data-ad-client="ca-pub-xxxxxxxxxxxxxxxx"
                 data-ad-slot="xxxxxxxxxx"
                 data-ad-format="auto"
                 data-full-width-responsive="true"></ins>
            <script>(adsbygoogle = window.adsbygoogle || []).push({});</script>
        </div>

        <div id="status" class="status">⏳ انتظر... الصق الرابط واضغط تحميل</div>
        
        <div style="text-align: center; margin-top: 15px;">
            <button class="clear-btn" onclick="clearDownloads()">🗑️ مسح الملفات المحملة</button>
        </div>
        
        <div class="footer">
            <span class="badge">🔥 يعمل محلياً على Pydroid 3</span>
            <p style="margin-top: 10px;">جميع الحقوق محفوظة © 2026 Shadow Downloader</p>
        </div>
    </div>

    <script>
        const form = document.getElementById('downloadForm');
        const status = document.getElementById('status');
        const urlInput = document.getElementById('urlInput');
        const downloadBtn = document.getElementById('downloadBtn');

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const url = urlInput.value.trim();
            if (!url) {
                status.className = 'status error';
                status.textContent = '❌ الرجاء إدخال رابط صحيح';
                return;
            }

            status.className = 'status';
            status.innerHTML = '<div class="loading"></div> جاري التحميل... قد يستغرق بضع ثوانٍ...';
            downloadBtn.disabled = true;
            downloadBtn.textContent = '⏳ جاري...';
            
            try {
                const formData = new FormData();
                formData.append('url', url);
                
                const response = await fetch('/download', {
                    method: 'POST',
                    body: formData
                });

                if (response.ok) {
                    const blob = await response.blob();
                    const link = document.createElement('a');
                    link.href = URL.createObjectURL(blob);
                    const contentDisposition = response.headers.get('content-disposition');
                    let filename = 'media.mp4';
                    if (contentDisposition) {
                        const match = contentDisposition.match(/filename=(.+)/);
                        if (match) filename = match[1];
                    }
                    link.download = filename;
                    document.body.appendChild(link);
                    link.click();
                    link.remove();
                    
                    status.className = 'status success';
                    status.textContent = '✅ تم التحميل بنجاح! ابحث عن الملف في مجلد downloads';
                } else {
                    const error = await response.text();
                    status.className = 'status error';
                    status.textContent = `❌ خطأ: ${error}`;
                }
            } catch (error) {
                status.className = 'status error';
                status.textContent = `❌ فشل الاتصال: ${error.message}`;
            } finally {
                downloadBtn.disabled = false;
                downloadBtn.textContent = '🚀 تحميل بأعلى دقة';
            }
        });

        async function clearDownloads() {
            if (!confirm('هل أنت متأكد من مسح جميع الملفات المحملة؟')) return;
            try {
                const res = await fetch('/clear');
                const data = await res.json();
                status.className = 'status success';
                status.textContent = `✅ ${data.status}`;
            } catch (error) {
                status.className = 'status error';
                status.textContent = `❌ فشل المسح: ${error.message}`;
            }
        }
    </script>
</body>
</html>
"""

# ========== دوال التحميل ==========
def detect_platform(url):
    url_lower = url.lower()
    if 'youtube.com' in url_lower or 'youtu.be' in url_lower:
        return 'youtube'
    elif 'tiktok.com' in url_lower:
        return 'tiktok'
    elif 'instagram.com' in url_lower:
        return 'instagram'
    elif 'twitter.com' in url_lower or 'x.com' in url_lower:
        return 'twitter'
    elif 'facebook.com' in url_lower:
        return 'facebook'
    elif 't.me' in url_lower or 'telegram.org' in url_lower:
        return 'telegram'
    elif 'snapchat.com' in url_lower:
        return 'snapchat'
    else:
        return 'unknown'

def download_with_ytdlp(url):
    """تحميل باستخدام yt-dlp لجميع المواقع"""
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',
        'outtmpl': str(DOWNLOAD_DIR / '%(title)s.%(ext)s'),
        'quiet': True,
        'no_warnings': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
            # التحقق من وجود الملف
            if os.path.exists(filename):
                return filename
            
            # البحث عن أي ملف تم تحميله حديثاً
            for file in DOWNLOAD_DIR.glob('*'):
                if file.stat().st_mtime > (asyncio.get_event_loop().time() - 120):
                    return str(file)
            
            return filename
    except Exception as e:
        # محاولة بسيطة بدون خيارات متقدمة
        simple_opts = {
            'format': 'best',
            'outtmpl': str(DOWNLOAD_DIR / '%(title)s.%(ext)s'),
            'quiet': True,
        }
        with yt_dlp.YoutubeDL(simple_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            return ydl.prepare_filename(info)

def download_instagram(url):
    """تحميل من إنستغرام"""
    try:
        loader = instaloader.Instaloader(
            download_videos=True,
            download_pictures=True,
            save_metadata=False,
            post_metadata_txt_pattern="",
            filename_pattern="{shortcode}_original"
        )
        
        # استخراج shortcode
        shortcode_match = re.search(r'/p/([^/?]+)', url)
        if not shortcode_match:
            raise Exception("رابط إنستغرام غير صالح")
        
        shortcode = shortcode_match.group(1)
        post = instaloader.Post.from_shortcode(loader.context, shortcode)
        loader.download_post(post, target=str(DOWNLOAD_DIR))
        
        # إرجاع أول ملف تم تحميله
        for file in DOWNLOAD_DIR.glob('*_original.*'):
            if file.stat().st_mtime > (asyncio.get_event_loop().time() - 120):
                return str(file)
        return None
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"فشل تحميل إنستغرام: {str(e)}")

# ========== مسارات API ==========
@app.get("/", response_class=HTMLResponse)
async def home():
    """عرض الصفحة الرئيسية"""
    return HTML_CODE

@app.post("/download")
async def download_media(url: str = Form(...)):
    """تحميل الوسائط من الرابط"""
    if not url.startswith(('http://', 'https://')):
        raise HTTPException(status_code=400, detail="رابط غير صالح")
    
    platform = detect_platform(url)
    filename = None
    
    try:
        if platform == 'instagram':
            filename = download_instagram(url)
        else:
            filename = download_with_ytdlp(url)
        
        if not filename or not os.path.exists(filename):
            raise HTTPException(status_code=404, detail="لم يتم العثور على الملف المحمّل")
        
        # إرجاع الملف
        return FileResponse(
            path=filename,
            filename=os.path.basename(filename),
            media_type='application/octet-stream'
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/clear")
async def clear_downloads():
    """مسح جميع الملفات المحملة"""
    try:
        for file in DOWNLOAD_DIR.glob('*'):
            if file.is_file():
                file.unlink()
        return {"status": "تم مسح جميع الملفات بنجاح"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"فشل المسح: {str(e)}")

# ========== تشغيل التطبيق ==========
if __name__ == "__main__":
    print("""
    ╔═══════════════════════════════════════════╗
    ║   🔥 Shadow Downloader v3.0 🔥           ║
    ║   كل شيء في ملف واحد                     ║
    ║   افتح الرابط في متصفح هاتفك:           ║
    ║   http://localhost:8000                  ║
    ╚═══════════════════════════════════════════╝
    """)
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")