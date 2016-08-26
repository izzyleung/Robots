from aiohttp import web
from ZhihuDailyPurify.views import index, news, search

app = web.Application()

app.router.add_route('GET', '/', index)
app.router.add_route('GET', '/news/{date}', news)
app.router.add_route('GET', '/search/', search)
