
from collections import deque
from settings import myauth
from settings import zipfile
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from repository import Repository
import requests
import time
import gzip
import json
import logging


#  ''' this function queries and returns github repos by languages used '''
def getLanguages():
    languages = deque([])
    # take any language as a seed
    languages.append('python')

    #while len(languages) != 0:
    lang = languages.popleft()
    p = {'q': 'languages:Python'}
    r = requests.get('https://api.github.com/search/repositories',
                    params=p, auth=myauth)

    result = r.json()

    print len(result['items'])

    for item in result['items']:
        lang_url = item['languages_url']
        print lang_url
        r = requests.get(lang_url, params={}, auth=('pgayane', 'Gayan4ik'))
        proj_langs = r.json()
        for lang in proj_langs:
            if not (lang in languages):
                languages.append(lang)

    #print len(languages)
    for lang in languages:
        print lang


def printSizePerLanguage():

    #get lang list

    lf = open('langs', 'r')
    langs = lf.readlines()
    lf.close()

    statf = open("stat", "w")
    counter = 0

    for lang in langs:
        lang = lang.strip()
        p = {'q': 'language:' + lang, 'page': 1, 'per_page': 1}
        r = requests.get('https://api.github.com/search/repositories', params=p, auth=myauth)
        print r.request.url

    result = r.json()
    if 'total_count' in result:
        statf.write(lang + ':' + str(result['total_count']) + '\n')
        print lang, result['total_count']
    else:
        print lang, str(result)[:200]

    counter += 1
    if counter == 20:
        counter = 0
        time.sleep(60)
      
    statf.close()

def getSession():
    engine = create_engine('postgresql://pgayane:g@localhost:5433/githubDB')
    Session = sessionmaker(bind=engine)
    session = Session()

    return session

def getAllRepos():
    
    session = getSession()

    p = {'since': 17262486}
    result = requests.get('https://api.github.com/repositories', params=p, auth=myauth).json()
    l = len(result)
    counter = 1
    print counter, l, p['since']

    start_time = time.time()
    while l > 0:
        if counter % 5000 == 0:
            delta = time.time() - start_time
            if delta < 3660:
                print 'sleep for %f' % (delta)
                time.sleep(3660 - delta)
            else:
                print 'not sleeping as delta is %f' % (delta)
            start_time = time.time()

        for proj in result:
            if 'id' in proj:
                rep = Repository()
                rep.id = proj['id']
                rep.full_name = proj['full_name']
                rep.languages_url = proj['languages_url']
                session.add(rep)
            else:
                print proj
                
        p['since'] = result[-1]['id']
        while l == 0:
            result = requests.get('https://api.github.com/repositories', params=p, auth=myauth)
        l = len(result.json())
        counter += 1
        print counter, l, p['since']

        if l == 0:
            print result

        result = result.json()

        session.commit()
    

def getLocally():

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    file_handler = logging.FileHandler('mergehistory.log')
    logger.addHandler(file_handler)
    
   
    session = getSession()

    with gzip.open(zipfile,"rb") as input_file:

        for line in input_file:
            try:
                user_repositories = json.loads(line)

                for repo in user_repositories:
                    if "created_at" in repo and repo["created_at"]:
                        year = repo["created_at"][:4]
                        is_success = Repository.update(session, repo['id'], creation_date = year, main_lang = repo['language'])

                        if is_success:
                            logger.info('%d %s %s' %(repo['id'] , year , repo['language']))
                        else:
                            logger.warning(str(repo['id']) +' update was unsuccessful')

                    else:
                        print repo
                logger.info('user repos updated')
                session.commit()
                file_handler.flush()
                print 'commits and flush to log file'
            except:
                logging.shutdown()
                print "Failed to load:"
                # print line
                break


if __name__ == '__main__':
    getLocally()
