import re,sys,glob,json,subprocess,urllib.parse
base="https://indahl.ai"
for f in sorted(glob.glob("page_*.html")):
    h=open(f,encoding="utf-8").read()
    srcs=re.findall(r'<script[^>]+src="([^"]+)"',h)
    links=re.findall(r'<link[^>]+href="([^"]+)"',h)
    inl=len(re.findall(r'<script(?![^>]*src)(?![^>]*ld\+json)[^>]*>',h))
    print(f, "scripts:",srcs, "inline-nonld:",inl)
