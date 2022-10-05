import datetime
from clfparser import CLFParser
import operator

# def tail(file, n=1, bs=1024):
#     f = open(file)
#     f.seek(0,2)
#     l = 1-f.read(1).count('\n')
#     B = f.tell()
#     while n >= l and B > 0:
#             block = min(bs, B)
#             B -= block
#             f.seek(B, 0)
#             l += f.read(block).count('\n')
#     f.seek(B, 0)
#     l = min(l,n)
#     lines = f.readlines()[-l:]
#     f.close()
#     return lines

URLS_TO_EXCLUDE = ["/sitenews/rss/",
                   "/favicon.ico/"]

def webpage_url_filter(url):
    return True if url[-1] == "/" and url not in URLS_TO_EXCLUDE else False

def retrieve_log(filename):
    with open(filename, "r") as f:
        content = f.readlines()
    return [CLFParser.logDict(l) for l in content]

def filter_log_to_get_ip_urls(records, cutoff_time):
    return [r['r'].split(" ")[1] for r in records
            if r['h'] != '-' and
            r['r'][0:4] == '"GET'and
            isinstance(r['time'], datetime.date) and
            r['time'] > cutoff_time]

def pages_by_popularity(filename, cutoff_time, url_filter):
    records = retrieve_log(filename)
    kept = filter(url_filter,
                  filter_log_to_get_ip_urls(records, cutoff_time))
    urls = {}
    for item in kept:
        if item in urls:
            urls[item] = urls[item] + 1
        else:
            urls[item] = 1
    most_pop = sorted(urls.items(), key=operator.itemgetter(1), reverse=True)
    return most_pop

def most_popular_pages(filename, cutoff_time, num=5, url_filter=None):
    return pages_by_popularity(filename, cutoff_time, url_filter)[0:num]

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Get most popular pages')
    parser.add_argument('--logfile', type=str, default="access.log")
    parser.add_argument('--date', type=str, default="")
    parser.add_argument('--diff', type=int, default=10)
    parser.add_argument('--num', type=int, default=5)
    parser.add_argument('--stdfilter', type=bool, default=True)
    parser.add_argument('--filter', dest='stdfilter', action='store_true')
    parser.add_argument('--no-filter', dest='stdfilter', action='store_false')
    parser.set_defaults(stdfilter=True)
    options = parser.parse_args()

    if options.date == "":
        cutoff_time = datetime.datetime.now() - \
                      datetime.timedelta(minutes=options.diff)
    else:
        cutoff_time = datetime.datetime.strptime(options.date,
                                                 '%Y-%m-%d %H:%M:%S')
    if options.stdfilter:
        url_filter = webpage_url_filter
    else:
        url_filter = None
    pages = most_popular_pages(options.logfile, cutoff_time,
                               options.num, url_filter)
    for k,v in pages:
        print(k, v)
