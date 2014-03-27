
from collections import deque
from requests_oauthlib import OAuth2Session
import settings
from sqlalchemy import create_engine
from sqlalchemy import func
from sqlalchemy import distinct
from sqlalchemy.orm import sessionmaker
from repository import Repository
import requests
from requests_oauthlib import OAuth2Session

import time
import gzip
import json
import logging
from counter import Counter
from collections import defaultdict


session = None

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
        r = requests.get(lang_url, params={}, auth=myauth)
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
    global session
    if session is None:
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

    counter = Counter(5000)
    while l > 0:
        counter.check_limit()

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
        counter.increment()
        print counter.count, l, p['since']

        if l == 0:
            print result

        result = result.json()

        session.commit()
    

def getLocally():

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.WARNING)
    file_handler = logging.FileHandler('mergehistory.log')
    logger.addHandler(file_handler)
    session = getSession()
    line_number = 0
    with gzip.open(zipfile,"rb") as input_file:

        for line in input_file:
            line_number += 1
            try:
                user_repositories = json.loads(line)

                for repo in user_repositories:
                    if "created_at" in repo and repo["created_at"]:
                        year = repo["created_at"][:4]
                        is_success = Repository.update(session, repo['id'], creation_date = year, main_lang = repo['language'])

                        if is_success:
                            logger.info('%d %s %s' %(repo['id'] , year , repo['language']))
                        else:
                            logger.warning(str(line_number) + ':' + str(repo['id']) +' update was unsuccessful')

                    else:
                        print repo
                logger.info('user repos updated')
                session.commit()
                file_handler.flush()
            except:
                logger.error(str(line_number) + ':' + line)
                
    logging.shutdown()

def get_extra_data(oauth):
    session = getSession()

    # usernames = session.query(Repository.username).group_by(Repository.username)

    # temproary test on small amount of data
    start = time.time()
    usernames = session.query(Repository.username).group_by(Repository.username).order_by(Repository.username).limit(1000).all()
    print 'usernames selected', time.time() - start

    counter = Counter(12500)
    while len(usernames) > 0:
        for username in usernames:
            # print 'geting data for user: ', username
            counter.check_limit()
            repos = get_repo_info_by_user(username, oauth)
            counter.increment()
        usernames = get_next_users(usernames[-1])
        print 'usernames selected after ', usernames[-1]
               
def get_next_users(lastusername):
    usernames = session.query(Repository.username).filter(Repository.username > lastusername).group_by(Repository.username).order_by(Repository.username).limit(1000)
    
    return usernames.all()
    
def get_user_repos(username, oauth):

    url = 'https://api.github.com/users/%s/repos' %(username)
    result = oauth.get(url).json()

    return result

def get_repo_info_by_user(username, oauth):
    session = getSession()
    user_results = get_user_repos(username, oauth)
    for repo in user_results:
        update_repo_info(repo)
    session.commit()

def update_repo_info(repo):
    #takes JSON object of a users repo and returns critical values for repo
    if 'size' in repo:
        size = repo["size"]
        star_ct = repo["stargazers_count"]
        fork_ct = repo["forks_count"]
        issue_ct = repo["open_issues_count"]
        create_at = repo["created_at"][:4]
        update_at = repo["updated_at"]
        language = repo["language"]
        repo_id = repo["id"]

        # print '     : updating repo: ', repo_id
        success = Repository.update(session, repo_id, 
            size = size, stargazers_count = star_ct, forks_count = fork_ct, open_issues_count = issue_ct,
            creation_date = create_at, main_lang = language)
    else:
        print repo
def exportToJSON():
    session = getSession()
    sum_per_year = session.query(Repository.creation_date, func.count(Repository.id)).\
                            filter(Repository.main_lang is not None,\
                            Repository.main_lang != '',\
                            Repository.creation_date is not None,\
                            Repository.creation_date != '2014',\
                            Repository.creation_date != '2007').\
                            group_by(Repository.creation_date).\
                            order_by(Repository.creation_date).all()
    
    repos = session.query(Repository.main_lang, Repository.creation_date, \
                    func.count(Repository.id)).filter(\
                    Repository.main_lang is not None,\
                    Repository.main_lang != '',\
                    Repository.creation_date is not None,\
                    Repository.creation_date != '2014',\
                    Repository.creation_date != '2007').\
                    group_by(Repository.main_lang, Repository.creation_date).\
                    order_by(Repository.main_lang, Repository.creation_date).all()
    
    timeline_data = defaultdict((lambda:defaultdict(float)))

    for (lang,year,count) in repos:
        count_formatted = float(count*100)/float(sum_per_year[int(year) - 2008][1])

        # don't round the count to have a correct sum for 'other' langs
        if count_formatted < 0.1:
            lang = 'other'
        else:
            count_formatted = round(count_formatted, 2)

        
        timeline_data[lang][year] += count_formatted
      
    # format the dictonary into array, as d3 cannot iterate over the dict
    export_data = {'languages': []}

    for lang in timeline_data:
        lang_popularity = [0,0,0,0,0,0]
        for year in timeline_data[lang]:
            lang_popularity[int(year)-2008] = timeline_data[lang][year]
        export_data['languages'].append({'name': lang, 'lang_popularity': lang_popularity})

    # for t in timeline_data:
    #     print t, timeline_data[t]

    with open('timeline_data.json', 'w') as outfile:
     json.dump(export_data, outfile, sort_keys = True, indent = 4, ensure_ascii=False)

if __name__ == '__main__':
    get_extra_data()    
