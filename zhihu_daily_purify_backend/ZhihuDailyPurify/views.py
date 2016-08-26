from aiohttp import web

from ZhihuDailyPurify.models import DailyNewsCollection


# noinspection PyUnusedLocal
async def index(request):
    return web.Response(text='index')


async def news(request):
    date = request.match_info.get('date', None)
    return web.json_response(await DailyNewsCollection.of_date(date))


async def search(request):
    keyword = request.GET.get('q', None)
    return web.json_response(await DailyNewsCollection.search_by_keyword(keyword))
