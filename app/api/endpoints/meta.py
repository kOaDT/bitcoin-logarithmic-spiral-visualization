from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse, Response
from datetime import datetime

router = APIRouter()

@router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "bitcoin-logarithmic-spiral-api"}

@router.get("/robots.txt", response_class=PlainTextResponse)
def robots(request: Request):
    base_url = str(request.base_url)
    sitemap_url = f"{base_url}sitemap.xml"
    data = f"User-agent: *\nAllow: /\nSitemap: {sitemap_url}"
    return data

@router.get("/sitemap.xml")
async def sitemap(request: Request):
    base_url = str(request.base_url).rstrip('/')
    xml_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>{base_url}/</loc>
    <lastmod>{datetime.now().strftime('%Y-%m-%d')}</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>
</urlset>
'''
    return Response(content=xml_content, media_type="application/xml")

@router.get("/.well-known/security.txt", response_class=PlainTextResponse)
def security_txt():
    content = """Contact: mailto:cyb.hub@proton.me
Preferred-Languages: en, fr, de
"""
    return content 