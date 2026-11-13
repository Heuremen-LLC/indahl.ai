import re, sys, html
t = open(sys.argv[1],encoding='utf-8').read()
m = re.search(r'<main.*?</main>', t, re.S)
body = m.group(0) if m else t
body = re.sub(r'<script.*?</script>|<style.*?</style>', '', body, flags=re.S)
body = re.sub(r'</(p|h\d|li|tr|section|div|ul|table)>', '\n', body)
body = re.sub(r'<br\s*/?>', '\n', body)
body = re.sub(r'<a [^>]*href="([^"]*)"[^>]*>(.*?)</a>', lambda m: m.group(2)+' ['+m.group(1)+']', body, flags=re.S)
body = re.sub(r'<[^>]+>', '', body)
print(html.unescape(re.sub(r'\n\s*\n+','\n',body)))
