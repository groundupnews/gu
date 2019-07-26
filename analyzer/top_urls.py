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


def most_popular_pages(filename, cutoff_time, num):
    with open(filename) as f:
        content = f.readlines()
    records = [CLFParser.logDict(l) for l in content]
    kept = [r['r'] for r in records
            if r['h'] != '-' and
            r['r'][0:4] == '"GET'and
            isinstance(r['time'], datetime.date) and
            r['time'] > cutoff_time]
    urls = {}
    for record in kept:
        s = record.split(" ")[1]
        if s[-1] == "/" and s != "/sitenews/rss/":
            if s in urls:
                urls[s] = urls[s] + 1
            else:
                urls[s] = 1
    most_pop = sorted(urls.items(), key=operator.itemgetter(1), reverse=True)
    for url in most_pop[0:num]:
        print(url[0], url[1])


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Get most popular pages')
    parser.add_argument('--logfile', type=str, default="access.log")
    parser.add_argument('--date', type=str, default="")
    parser.add_argument('--diff', type=int, default=10)
    parser.add_argument('--num', type=int, default=5)
    options = parser.parse_args()

    if options.date == "":
        cutoff_time = datetime.datetime.now() - \
                      datetime.timedelta(minutes=options.diff)
    else:
        cutoff_time = datetime.datetime.strptime(options.date,
                                                 '%Y-%m-%d %H:%M:%S')
    most_popular_pages(options.logfile, cutoff_time, options.num)
