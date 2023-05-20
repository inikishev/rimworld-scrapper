import urllib.request, urllib.error, multiprocessing.dummy, http.client

def _parse(url):
    broken_URL = False
    try:
        if url == 'ang=': return
        for i in range(3):
            try:
                results = urllib.request.urlopen(url).read().decode("utf-8")
                break
            except (http.client.IncompleteRead, ValueError): 
                print(f'{url} failed during attempt {i}')
                if i == 2: broken_URL = True
        if broken_URL is True: return
        s = results.find('<a href="/') + 100
        s = results.find('<a href="/', s) + len('<a href="')
        e = results.find('"', s)
        #print(s, e, results[s:e])
        url = 'https://gist.githubusercontent.com/' + results[s:e]
        if url == 'ang=': return
        for i in range(3):
            try:
                results = urllib.request.urlopen(url).read().decode("utf-8")
                break
            except (http.client.IncompleteRead, urllib.error.HTTPError): print(f'{url} failed during attempt {i}')
        print(f'{url}')
        return results
    except http.client.IncompleteRead: return


def download_logs(query: str, pages:int=3):
    """Downloads `pages` amount of pages of most recent gists by query. Each page is 10 logs. Tip: put your query in commas like "your_query" to search for exact match."""
    if __name__ == 'RimWorld_Scrapper.GistGithub':
        #print(__name__, __name__=='RimWorld_Scrapper.GistGithub')
        gists=[]
        linksg=[]
        for page in range(pages):
            broken_URL = False
            links = []
            for i in range(3):
                try:
                    results = urllib.request.urlopen(f'https://gist.github.com/search?p={page+1}&q={query.replace(" ","+")}&s=updated').read().decode("utf-8") 
                    break
                except http.client.IncompleteRead: 
                    print(f'{page+1} failed during attempt {i}')
                    broken_URL = True
            if broken_URL is True:
                break
            if 'We couldn’t find any gists matching' in results: 
                if page == 0: print(f'KEEP MALDING: No results found for {query}')
                break
            print(f'Page {page+1} downloaded')
            s=0
            for i in range(10):
                s = results.find('<a class="link-overlay" href="', s) + len('<a class="link-overlay" href="')
                e = results.find('"', s)
                #print(results[s:e])
                if results[s:e] not in linksg: 
                    links.append(results[s:e])
                    linksg.append(results[s:e])
                s += e-s
            #print(links)
            if len(links)>0:
                with multiprocessing.dummy.Pool(10) as p:
                    gist = p.map(_parse, links)

                gists.extend(gist)
            else: 
                print(f'Idk what happened but page {page+1} dident work')
                #with open(f'GistGithub_broken_page{page+1}.txt', 'w', encoding='utf8') as f: f.write(results)
    return gists