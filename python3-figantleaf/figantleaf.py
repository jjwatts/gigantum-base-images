import hashlib
import json
import os
import configparser
import requests
from requests.exceptions import HTTPError
import tarfile
import time
from yaml import CLoader as Loader, CDumper as Dumper
import yaml as yaml
from string import ascii_lowercase
import shutil
import pandas as pd
import getpass
import subprocess
import sys
import time
import git
from pybtex.database import BibliographyData, Entry
import pylatex as ltx
import networkx as nx
import io


with open('/mnt/labbook/.git/HEAD', 'r') as file:
    head = file.read().replace('\n','').replace(':','').replace('/','_').replace(' ','')

def ConfigSectionMap(section,Config):
    dict1 = {}
    options = Config.options(section)
    for option in options:
        try:
            dict1[option] = Config.get(section, option)
            #if dict1[option] == -1:
                #print ("skip: %s" % option)
        except:
            print("exception on %s!" % option)
            dict1[option] = None
    return dict1

if not os.path.exists("/mnt/labbook/output/untracked/overleaf-{}.properties".format(head)):
    
    #print("""Enter details for local git setup""")
    #name=input('Enter your full name (for github setup):')
    #email=input('Enter your email (for github setup):')
    print("""
    Enter the location of you overleaf overleaf project
    """)
    overleaf_repo=input()
#    print("""
#    Enter the your figshare token
#    """)
#    figshare_token=input()
    
    
    with open("/mnt/labbook/output/untracked/overleaf-{}.properties".format(head), "w") as prop:
#        prop.write("[figshare]\n")
#        prop.write("url=https://api.figshare.com/v2/{endpoint}\n")
#        prop.write("token={}\n".format(figshare_token))
#        prop.write("chunksize=1048576\n")
        prop.write("[git]\n")
#        prop.write("username={}\n".format(name))
#        prop.write("email={}\n".format(email))
        prop.write("overleaf_repository={}\n".format(overleaf_repo))
        

Config = configparser.ConfigParser()
Config.read("/home/giguser/.dimensions/dsl.ini")

Configoverleafrepo = configparser.ConfigParser()
Configoverleafrepo.read("/mnt/labbook/output/untracked/overleaf-{}.properties".format(head))

fprops = ConfigSectionMap("figshare",Config)
gprops = ConfigSectionMap("git",Configoverleafrepo)
oprops = ConfigSectionMap("overleaf",Config)

BASE_URL = fprops['url']
TOKEN = fprops['token']
CHUNK_SIZE = int(fprops['chunksize'])
name=oprops['username'].split('@')[0]
email=oprops['username']
repository=gprops['overleaf_repository']
os.environ['GIT_USERNAME']=oprops['username']
os.environ['GIT_PASSWORD']=oprops['password']
project_dir = os.path.dirname(os.path.abspath(__file__))
os.environ['GIT_ASKPASS']=os.path.join(project_dir, 'askpass.py')

print(os.environ['GIT_ASKPASS'])


### Setiing up git infrastructure        
#if not os.path.exists('/mnt/labbook/output/untracked/overleaf'):
#    os.mkdir('/mnt/labbook/output/untracked/overleaf')
repo = None

if not os.path.exists('/mnt/labbook/output/untracked/tmp_overleaf-{}'.format(head)):
    os.mkdir('/mnt/labbook/output/untracked/tmp_overleaf-{}'.format(head))
#if not os.path.exists('/mnt/labbook/output/untracked/overleaf_credentials'):
#    os.mkdir('/mnt/labbook/output/untracked/overleaf_credentials')
    

#if not os.path.exists("/mnt/labbook/output/untracked/overleaf_credentials/id_rsa"):
#    command = "ssh-keygen -t rsa -b 4096 -C {} -f /mnt/labbook/output/untracked/overleaf_credentials/id_rsa".format(email)
#    args = command.split(' ')
#    keygen = subprocess.Popen(args).wait()
#    time.sleep(5)
#    if os.path.exists("/mnt/labbook/output/untracked/overleaf_credentials/id_rsa"):
#        f = open("/mnt/labbook/output/untracked/overleaf_credentials/id_rsa.pub","r")
#        public_key = f.read()
#        print("""
#        Copy the following public key into github.com -> settings -> ssh keys
#        press return when done
#        """)
#        print(public_key)
#        input()        
#    else:
#        print('ssh-keygen did not work')
    
    
#if not os.path.isdir("/home/giguser/.ssh"):
#    os.mkdir ('/home/giguser/.ssh')
#    subprocess.Popen("chmod 700 /home/giguser/.ssh".split(" ")).wait()
          
#    with open("/home/giguser/.ssh/config","w") as config:
#        config.write("Host github.com\n")
#        config.write("IdentityFile /mnt/labbook/output/untracked/overleaf_credentials/id_rsa\n")
        
#    with open("/home/giguser/.ssh/known_hosts","wb") as out:
#        subprocess.call("ssh-keyscan github.com >> ~/.ssh/known_hosts".split(), stdout=out)
#    subprocess.Popen(['git', 'config', '--global', 'user.name', '"{}"'.format(name)]).wait()
#    subprocess.Popen(['git', 'config', '--global', 'user.email', '"{}"'.format(email)]).wait()

if not os.path.exists("/mnt/labbook/output/untracked/overleaf-{}/.git".format(head)):
    os.chdir('/mnt/labbook/output/untracked')
    repo = git.Repo.clone_from(repository,'overleaf-{}'.format(head))
    #print("git clone {} overleaf".format(repository))
    #subprocess.Popen("git clone {} overleaf".format(repository).split(" ") ).wait()
else:
    repo = git.Repo('/mnt/labbook/output/untracked/overleaf-{}/'.format(head))


if not os.path.exists('/mnt/labbook/output/untracked/overleaf-{}/figshare'.format(head)):
    os.mkdir('/mnt/labbook/output/untracked/overleaf-{}/figshare'.format(head))    

os.chdir('/mnt/labbook/code')
if repo is None:
    repo = git.Repo('/mnt/labbook/output/untracked/overleaf-{}/'.format(head))
    repo.git.pull()



def raw_issue_request(method, url, data=None, binary=False):
    headers = {'Authorization': 'token ' + TOKEN}
    #print(headers, data)
    if data is not None and not binary:
        data = json.dumps(data)
    response = requests.request(method, url, headers=headers, data=data)
    try:
        response.raise_for_status()
        try:
            data = json.loads(response.content)
        except ValueError:
            data = response.content
    except HTTPError as error:
        print ('Caught an HTTPError: {}'.format(error.message))
        print ('Body:\n', response.content)
        raise

    return data


def issue_request(method, endpoint, *args, **kwargs):
    #print(BASE_URL.format(endpoint=endpoint))
    return raw_issue_request(method, BASE_URL.format(endpoint=endpoint), *args, **kwargs)


def list_articles():
    result = issue_request('GET', 'account/articles')
    print ('Listing current articles:')
    if result:
        for item in result:
            print (u'  {url} - {title}'.format(**item))
    else:
        print ('  No articles.')
        
        
def get_project_articles(project_id):
    
    data = {"page_size": 100}

    result = issue_request('GET', 'account/projects/{}/articles'.format(project_id), data=data)
    #print ('Listing current articles:')
    if result:
        return result
    else:
        return [dict(id=None,title=None)]

        
def list_projects():
    result = issue_request('GET', 'account/projects')
    print ('Listing current projects:')
    if result:
        for item in result:
            print (u'  {url} - {title}'.format(**item))
    else:
        print ('  No projects.')
        
    
        
def search_projects(search_term):
    data = {
        'search_for': search_term  
    }
    result = issue_request('POST', 'account/projects/search', data=data)
    print ('Listing current projects:')
    if result:
        for item in result:
            print (u'  {url} - {title}'.format(**item))
        return result
    else:
        print ('  No projects.')
        
def create_project(title):
    data = {
        'title': title  
    }
    result = issue_request('POST', 'account/projects', data=data)
    #print ('Created project:', result['location'], '\n')
    result = raw_issue_request('GET', result['location'])    
    return result['id']

def create_project_article(project_id,title):
    with open('/home/giguser/jupyter_token', 'r') as file:
        jupyter_token = file.read().replace('\n','').split(',')
    data = {
        "title": title,  
        "references": ['https://gigantum.com/{}/{}'.format(jupyter_token[1],jupyter_token[2])]
    }
    result = issue_request('POST', 'account/projects/{}/articles'.format(project_id), data=data)
    #print ('Created project article:', result['location'], '\n')
    result = raw_issue_request('GET', result['location'])    
    return result['id']


def create_article(title):
    with open('/home/giguser/jupyter_token', 'r') as file:
        jupyter_token = file.read().replace('\n','').split(',')
    data = {
        "title": title,  
        "references": ['https://gigantum.com/{}/{}'.format(jupyter_token[1],jupyter_token[2])]
    }
    print("references are...",data["references"])
    result = issue_request('POST', 'account/articles', data=data)
    #print ('Created article:', result['location'], '\n')

    result = raw_issue_request('GET', result['location'])

    return result['id']



def update_article(article_id, data):

    result = issue_request('PUT', 'account/articles/{}'.format(article_id), data=data)
    #print (result)

    #result = raw_issue_request('GET', result['location'])

    return 

def reserve_article_doi(article_id):
    article = issue_request('GET', 'account/articles/{}'.format(article_id))
    #print(article)
    if article.get('doi', None) in [None,'']:
        result = issue_request('POST', 'account/articles/{}/reserve_doi'.format(article_id))
        print("a doi was requested", result['doi'])
        return result['doi']
    else:
        return article['doi']


def list_files_of_article(article_id):
    result = issue_request('GET', 'account/articles/{}/files'.format(article_id))
    print ('Listing files for article {}:'.format(article_id))
    if result:
        for item in result:
            print ('  {id} - {name}'.format(**item))
    else:
        print ('  No files.')
        
def get_files_of_article(article_id):
    result = issue_request('GET', 'account/articles/{}/files'.format(article_id))
    if result:
        return result
    else:
        return [dict(name=None,id=None)]



def get_file_check_data(file_name):
    with open(file_name, 'rb') as fin:
        md5 = hashlib.md5()
        size = 0
        data = fin.read(CHUNK_SIZE)
        while data:
            size += len(data)
            md5.update(data)
            data = fin.read(CHUNK_SIZE)
        return md5.hexdigest(), size

def upload_file(article_id,dirname,f):
    file_info = initiate_new_upload(article_id, "{}/{}".format(dirname,f))
    upload_parts(file_info, "{}/{}".format(dirname,f))
    complete_upload(article_id, file_info['id'])


def initiate_new_upload(article_id, file_name):
    endpoint = 'account/articles/{}/files'
    endpoint = endpoint.format(article_id)

    md5, size = get_file_check_data(file_name)
    data = {'name': os.path.basename(file_name),
            'md5': md5,
            'size': size}

    result = issue_request('POST', endpoint, data=data)
    #print ('Initiated file upload:', result['location'], '\n')

    result = raw_issue_request('GET', result['location'])

    return result


def complete_upload(article_id, file_id):
    issue_request('POST', 'account/articles/{}/files/{}'.format(article_id, file_id))
    
def delete_file(article_id, file_id):
    issue_request('DELETE', 'account/articles/{}/files/{}'.format(article_id, file_id))    


def upload_parts(file_info, file_path):
    url = '{upload_url}'.format(**file_info)
    result = raw_issue_request('GET', url)

    #print ('Uploading parts:')
    with open(file_path, 'rb') as fin:
        for part in result['parts']:
            upload_part(file_info, fin, part)



def upload_part(file_info, stream, part):
    udata = file_info.copy()
    udata.update(part)
    url = '{upload_url}/{partNo}'.format(**udata)

    stream.seek(part['startOffset'])
    data = stream.read(part['endOffset'] - part['startOffset'] + 1)

    raw_issue_request('PUT', url, data=data, binary=True)
    #print ('  Uploaded part {partNo} from {startOffset} to {endOffset}'.format(**part))
    
def create_gigantum_figshare():
    f = open("/mnt/labbook/.gigantum/project.yaml", "r", encoding="utf-8")       
    with open('/mnt/labbook/.git/HEAD', 'r') as file:
        head = file.read().replace('\n','')
    y = yaml.load(f, Loader=Loader)
    p = search_projects('""'+y['name']+' '+head+'""')
    if p is None:        
        return create_project(y['name']+' '+head)
    else:
        #print('project already created',p)
        return p[0]['id']
    
def make_tarfile(output_filename, source_dir):
    with tarfile.open(output_filename, "w:gz") as tar:
        tar.add(source_dir, arcname=os.path.basename(source_dir))
    
def sync_folders_to_figshare():
    letters = [letter1+letter2 for letter1 in ascii_lowercase for letter2 in ascii_lowercase]
    for fn in ['input','output','code']:
        make_tarfile('/mnt/share/{}.tar.gz'.format(fn),'/mnt/labbook/{}'.format(fn))
        
        chunk_size = 1500000000
        file_number = 0
        article_id = create_project_article(FIGSHARE_PROJECT_ID,'{}.tar.gz'.format(fn))
        with open('/mnt/share/{}.tar.gz'.format(fn), 'rb') as f:
            chunk = f.read(chunk_size)
            while chunk:
                filebase ='{}.tar.gz.part{}'.format(fn,letters[file_number])
                filename='/mnt/share/{}'.format(filebase)
                with open(filename, 'wb') as chunk_file:
                    chunk_file.write(chunk)
                    file_info = initiate_new_upload(article_id, filename)
                    upload_parts(file_info, filename)
                    #print(file_info)
                    complete_upload(article_id, file_info['id'])
                    os.remove(filename)
                file_number += 1
                chunk = f.read(chunk_size)
        os.remove('/mnt/share/{}.tar.gz'.format(fn))
        
        
FIGSHARE_PROJECT_ID = create_gigantum_figshare()

def fig_tofigshare(plt, df, filename, to_overleaf=False):
    
    filename = filename.strip()
    articles = pd.DataFrame(get_project_articles(FIGSHARE_PROJECT_ID))[['id','title']]
    if len(articles[articles['title']==filename].index) > 0:
        print("updating existing article")
        article_id = list(articles[articles['title']==filename].id)[0]
        
    else: 
        print("no match found - creating a new article")
        article_id = create_project_article(FIGSHARE_PROJECT_ID,filename)
    dirName = "/mnt/labbook/output/untracked/figtmp_{}".format(article_id)
    os.mkdir(dirName)
    
    plt.savefig("{}/{}_print.png".format(dirName,filename), dpi=300)
    plt.savefig("{}/{}_web.png".format(dirName,filename), dpi=75)
    df.to_csv("{}/{}.csv".format(dirName,filename))
    df.to_pickle("{}/{}.pkl".format(dirName,filename))
    
    files = pd.DataFrame(get_files_of_article(article_id))
    #print(files)
    
    for f in [ "{}{}".format(filename,ftype) 
              for ftype in['_print.png','_web.png','.csv','.pkl']]:
        #print(f)
        if len(files[files['name']== f]) > 0:
            #print('deleted file')
            delete_file(article_id, list(files[files['name']== f]['id'])[0])

        
        file_info = initiate_new_upload(article_id, "{}/{}".format(dirName,f))
        upload_parts(file_info, "{}/{}".format(dirName,f))
        complete_upload(article_id, file_info['id'])
    
    shutil.rmtree(dirName)
    doi = reserve_article_doi(article_id)
    print(doi)
    
    if to_overleaf==True:
        print_file =  "{}_print.png".format(filename)
        fig_to_overleaf(article_id,print_file)

    
    return article_id, doi

def df_to_figshare(df, filename, article_name=None, to_overleaf=False, caption=None):
    
    articles = pd.DataFrame(get_project_articles(FIGSHARE_PROJECT_ID))[['id','title']]
    
    if article_name is None:
        article_name = filename
    
    if len(articles[articles['title']==article_name].index) > 0:
        article_id = list(articles[articles['title']==article_name].id)[0]
        print('article id is', article_id)
        
    else: 
        article_id = create_project_article(FIGSHARE_PROJECT_ID,article_name)
    dirName = "/mnt/labbook/output/untracked/figtmp_{}".format(article_id)
    os.mkdir(dirName)
    
    
    df.to_csv("{}/{}.csv".format(dirName,filename))
    df.to_pickle("{}/{}.pkl".format(dirName,filename))
    
    files = pd.DataFrame(get_files_of_article(article_id))
    #print(files)
    
    for f in [ "{}{}".format(filename,ftype) 
              for ftype in['.pkl','.csv']]:
        #print(f)
        if len(files[files['name']== f]) > 0:
            #print('deleted file')
            delete_file(article_id, list(files[files['name']== f]['id'])[0])

        
        file_info = initiate_new_upload(article_id, "{}/{}".format(dirName,f))
        upload_parts(file_info, "{}/{}".format(dirName,f))
        complete_upload(article_id, file_info['id'])
    
    shutil.rmtree(dirName)
    doi = reserve_article_doi(article_id)
    print(doi)
    
    if to_overleaf==True:
        new_files = pd.DataFrame(get_files_of_article(article_id))
        table_file =  "{}.pkl".format(filename)
        overleaf = pd.DataFrame()
        if 'overleaf_mapping' in list(pd.DataFrame(get_project_articles(FIGSHARE_PROJECT_ID)).title):
            overleaf = figshare_to_df('overleaf_mapping', filename='overleaf')
            
            if len(overleaf[(overleaf['article_name']==filename) & (overleaf['name']==table_file)].index) == 0:
                print("adding new figure")
                figures = len(overleaf[overleaf['overleaf'].str.contains("table_")].index)
                new_overleaf=pd.DataFrame([dict(article_id=article_id,
                                           article_name=filename,
                                           name=table_file,
                                           overleaf='table_{}'.format(figures+1),
                                           caption=caption)])
                #print(overleaf)
                overleaf = pd.concat([overleaf,new_overleaf])
                
        else:
            #print("adding the first table", dict(article_id=article_id,
            #                        article_name=filename,
            #                        name=table_file,
            #                        overleaf='table_1'))
                  
            overleaf=pd.DataFrame([dict(article_id=article_id,
                                    article_name=filename,
                                    name=table_file,
                                    overleaf='table_1',
                                    caption=caption)])
                
        if filename != 'overleaf':        
            df_to_figshare(overleaf,
                      'overleaf', 
                      article_name='overleaf_mapping')
            
        create_overleaf_files(overleaf)
        try:
            repo.git.pull()
            repo.git.commit('-m', 'updates for {}-()'.format(filename,table_file), author=email) 
            repo.git.push()
        except Exception as e:
            print('No changes found, so nothing was committed',str(e))
    
    
    return article_id, doi

def figshare_to_graph(filename, article_name):
    articles = pd.DataFrame(get_project_articles(FIGSHARE_PROJECT_ID))[['id','title']]
    
    if len(articles[articles['title']==article_name].index) > 0:
        article_id = list(articles[articles['title']==article_name].id)[0]
        print('article id is', article_id)
        
    else: 
        print("Could not find the article")
        return None
        
    dirname = "/mnt/labbook/output/untracked/graphtmp_{}".format(article_id)
    
    if os.path.exists(dirname):
        shutil.rmtree(dirname)

    os.mkdir(dirname)
    
    files = pd.DataFrame(get_files_of_article(article_id))
    print("looking for", '{}.graphml'.format(filename), "in", article_id)
    match = files[files['name']== '{}.graphml'.format(filename)]
    if len(match.index) > 0:
        download_url = list(match['download_url'])[0]
        graphlocation = '{}/tmp_{}.graphml'.format(dirname,filename)
        graph = raw_issue_request('GET', download_url,  binary=True)
        with open(graphlocation, 'wb') as f:
                f.write(graph)
        return dirname,article_id
    else: 
            print("file not found")
            return None
    

    
    

def graph_to_figshare(nodesdf, edgesdf, filename, article_name=None, caption=None):
    articles = pd.DataFrame(get_project_articles(FIGSHARE_PROJECT_ID))[['id','title']]
    
    if article_name is None:
        article_name = filename
    
    if len(articles[articles['title']==article_name].index) > 0:
        article_id = list(articles[articles['title']==article_name].id)[0]
        print('article id is', article_id)
        
    else: 
        article_id = create_project_article(FIGSHARE_PROJECT_ID,article_name)
        
    files = pd.DataFrame(get_files_of_article(article_id))
    #print(files)
    
    for f in [ "{}{}".format(filename,ftype) 
              for ftype in['graphml']]:
        #print(f)
        if len(files[files['name']== f]) > 0:
            #print('deleted file')
            delete_file(article_id, list(files[files['name']== f]['id'])[0])
        
    dirname = "/mnt/labbook/output/untracked/figtmp_{}".format(article_id)

    os.mkdir(dirname)
    
    
    G = nx.Graph()
    G.add_edges_from([(e[1]['n1'],e[1]['n2'],{"weight":e[1]['weight']}) 
                  for e in edgesdf[edgesdf['n1'] < edgesdf['n2']].iterrows()])
    G.add_nodes_from([(n[0], n[1]) for n in nodesdf.iterrows()])

    nx.write_graphml(G, "{}/{}.graphml".format(dirname,filename))
    
    files = pd.DataFrame(get_files_of_article(article_id)) 
    
    for f in [ "{}{}".format(filename,ftype) 
              for ftype in['.graphml']]:
        #print(f)
        if len(files[files['name']== f]) > 0:
            #print('deleted file')
            delete_file(article_id, list(files[files['name']== f]['id'])[0])
       
        file_info = initiate_new_upload(article_id, "{}/{}".format(dirname,f))
        upload_parts(file_info, "{}/{}".format(dirname,f))
        complete_upload(article_id, file_info['id'])
    

    shutil.rmtree(dirname)
    

    df_to_figshare(nodesdf, "{}_nodes".format(filename),  article_name=article_name)
    df_to_figshare(edgesdf, "{}_edges".format(filename),  article_name=article_name)
    
    return article_id
    
    
    
    

def figshare_to_df(article_name, filename=None):
    
    articles = pd.DataFrame(get_project_articles(FIGSHARE_PROJECT_ID))[['id','title']]

    if filename is None:
        filename = article_name
    
    
    if len(articles[articles['title']==article_name].index) > 0:
        article_id = list(articles[articles['title']==article_name].id)[0]
        files = pd.DataFrame(get_files_of_article(article_id))
        match = files[files['name']== '{}.pkl'.format(filename)]
        if len(match.index) > 0:
            download_url = list(match['download_url'])[0]
            pkl = raw_issue_request('GET', download_url,  binary=True)
            with open('/mnt/labbook/output/untracked/tmp_{}.pkl'.format(filename), 'wb') as f:
                    f.write(pkl)
            df = pd.read_pickle('/mnt/labbook/output/untracked/tmp_{}.pkl'.format(filename))
            os.remove('/mnt/labbook/output/untracked/tmp_{}.pkl'.format(filename))
            return df
        else: 
            print("file not found")
            return None
        
def create_overleaf_files(overleaf):
    files = []
    
    articles = get_project_articles(FIGSHARE_PROJECT_ID)
    #print(articles)
    for article in articles:
        #print(article['title'])
        newfiles = get_files_of_article(article['id'])
        for i,f in enumerate(newfiles):
            newfiles[i]['article_id'] = article['id']
            newfiles[i]['article_name'] = article['title']
        files += newfiles
        
    fdf = pd.DataFrame(files)
    #print("fdf",fdf)
    
    fdf.sort_values(by = ['article_id','article_name','name'])
    fdfo = fdf[['article_id','article_name','name']]
    fdfo = fdfo.merge(overleaf[['article_id','name','overleaf']], 
               on=['article_id','name'],
               how='outer')
    
    #print("fdfo", fdfo)
    
    fdfo = fdfo.where(pd.notnull(fdfo), None)
    
    for_download = overleaf.merge(fdf[['article_id','name','download_url']], on=['article_id','name'])

    
    #print("for_download",for_download)
    
    # create individual files
    for row in for_download.iterrows():
        if len(row[1]['overleaf']) > 0:
            download_url = row[1]['download_url']
            file = raw_issue_request('GET', download_url,  binary=True)
            if '.pkl' in row[1]['name']:
                with open('/mnt/labbook/output/untracked/tmp_overleaf-{}/{}'.format(head,row[1]['name']), 'wb') as f:
                          f.write(file)
                df = pd.read_pickle('/mnt/labbook/output/untracked/tmp_overleaf-{}/{}'.format(head,row[1]['name']))
                df.to_latex('/mnt/labbook/output/untracked/overleaf-{}/figshare/{}.tex'.format(head,row[1]['overleaf']))
                repo.git.add('figshare/{}.tex'.format(row[1]['overleaf']))
            else:
                extension = row[1]['name'].split('.')[-1]
                with open('/mnt/labbook/output/untracked/overleaf-{}/figshare/{}.{}'.format(head,row[1]['overleaf'],extension), 'wb') as f:
                    f.write(file)
                    repo.git.add('figshare/{}.{}'.format(row[1]['overleaf'],extension))
                
    # create bibliography file
    adf = pd.DataFrame(articles)
    #print(adf)
    bib_data = BibliographyData()

    for row in for_download.iterrows():

        if len(row[1]['overleaf']) > 0:
            idx = adf[adf['id']==row[1]['article_id']].index[0]
            bib_data.add_entry( key= row[1]['overleaf'],
                              entry=Entry('article', [
                                            ('title', adf.at[idx,'title'] ),
                                            ('journal', "figshare"),
                                            ('doi', adf.at[idx,'doi']),
                                        ]

                                    ))
            
    bib_data.to_file('/mnt/labbook/output/untracked/overleaf-{}/figures_tables.bib'.format(head))
    repo.git.add('figures_tables.bib')
    
    # write supplementary tex
    
    geometry_options = {"tmargin": "1cm", "lmargin": "1cm"}
    doc = ltx.Document(geometry_options=geometry_options)
    doc.preamble.append(ltx.Package('biblatex',options=['sorting=none']))
    doc.preamble.append(ltx.Command('addbibresource',arguments=[ltx.NoEscape("figures_tables.bib")]))
    doc.preamble.append(ltx.Package('booktabs'))
    doc.preamble.append(ltx.Package('longtable'))
    
    with doc.create(ltx.Subsection('images and tables supplementary file')):
        for row in for_download.iterrows():
            if len(row[1]['overleaf']) > 0:
                idx = adf[adf['id']==row[1]['article_id']].index[0]
                #print("The name is...",row[1]['name'])
                if '.pkl' in row[1]['name']:
                    #print("I should be including something here")
                    with doc.create(ltx.Table(position='hbt')) as table_holder:
                        table_holder.append(ltx.Command('input',arguments=[ltx.NoEscape("figshare/{}.tex".format(row[1]['overleaf']))]))
                        if row[1]['caption'] is not None:
                            table_holder.add_caption(row[1]['caption'])
                            with open("/mnt/labbook/output/untracked/overleaf-{}/figshare/{}_caption.tex".format(head,row[1]['overleaf']), "w") as text_file:
                                text_file.write(row[1]['caption'])
                        else: 
                            table_holder.add_caption(adf.at[idx,'title'])
                            with open("/mnt/labbook/output/untracked/overleaf-{}/figshare/{}_caption.tex".format(head,row[1]['overleaf']), "w") as text_file:
                                text_file.write(adf.at[idx,'title'])
                        repo.git.add('figshare/{}_caption.tex'.format(row[1]['overleaf']))
                        table_holder.append(ltx.Command('cite',arguments=[ltx.NoEscape(row[1]['overleaf'])])) 
                    
                else:
                    with doc.create(ltx.Figure(position='hbt')) as image_holder: 
                        image_holder.add_image('figshare/{}'.format(row[1]['overleaf']))
                        #print("THE CAPTION IS:", row[1]['caption'])
                        if row[1]['caption'] is not None:
                            image_holder.add_caption(row[1]['caption'])
                            with open("/mnt/labbook/output/untracked/overleaf-{}/figshare/{}_caption.tex".format(head,row[1]['overleaf']), "w") as text_file:
                                text_file.write(ltx.utils.escape_latex(row[1]['caption']))                               
                        else: 
                            image_holder.add_caption(ltx.utils.escape_latex(adf.at[idx,'title']))
                            with open("/mnt/labbook/output/untracked/overleaf-{}/figshare/{}_caption.tex".format(head,row[1]['overleaf']), "w") as text_file:
                                text_file.write(ltx.utils.escape_latex(adf.at[idx,'title']))
                        repo.git.add('figshare/{}_caption.tex'.format(row[1]['overleaf']))
                        image_holder.append(ltx.Command('cite',arguments=[ltx.NoEscape(row[1]['overleaf'])]))        
    
    doc.append(ltx.Command('printbibliography')) 
    
    doc.generate_tex('/mnt/labbook/output/untracked/overleaf-{}/supplementary'.format(head))
    repo.git.add('supplementary.tex')
    
    
def fig_to_overleaf(article_id,filename,print_file,caption=None):
        repo.git.pull()
        new_files = pd.DataFrame(get_files_of_article(article_id))
        
        
        print(article_id,filename,print_file)
        overleaf = pd.DataFrame()
        if 'overleaf_mapping' in list(pd.DataFrame(get_project_articles(FIGSHARE_PROJECT_ID)).title):
            overleaf = figshare_to_df('overleaf_mapping', filename='overleaf')
            
            if len(overleaf[(overleaf['article_name']==filename) & (overleaf['name']==print_file)].index) == 0:
                print("adding new figure")
                figures = len(overleaf[overleaf['overleaf'].str.contains("fig")].index)
                new_overleaf=pd.DataFrame([dict(article_id=article_id,
                                           article_name=filename,
                                           name=print_file,
                                           overleaf='fig_{}'.format(figures+1),
                                           caption=caption)])
                print(overleaf)
                overleaf = pd.concat([overleaf,new_overleaf])
                
        else:
                  
            overleaf=pd.DataFrame([dict(article_id=article_id,
                                    article_name=filename,
                                    name=print_file,
                                    overleaf='fig_1',
                                    caption=caption)])
        if filename != 'overleaf':        
            df_to_figshare(overleaf,
                      'overleaf', 
                      article_name='overleaf_mapping')
            
        create_overleaf_files(overleaf)
        try:
            repo.git.commit('-m', 'updates for {}-()'.format(filename,print_file), author=email) 
            repo.git.push()
        except Exception as e:
            print('No changes detected, so nothing was committed', str(e))