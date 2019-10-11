import subprocess, os
def post_save_hook(os_path, model, contents_manager, **kwargs):
    try:
        labmanager_ip = open('/home/giguser/labmanager_ip').read().strip()
        tokens = open('/home/giguser/jupyter_token').read().strip()
        username, owner, lbname, jupyter_token = tokens.split(',')
        #url_args = f'file={os.path.basename(os_path)}&jupyter_token={jupyter_token}'
        url_args = "file={}&jupyter_token={}".format(os.path.basename(os_path), jupyter_token)
        url = "http://{}:10001/api/savehook/{}/{}/{}?{}".format(labmanager_ip,username,owner,lbname,url_args)
        subprocess.run(['wget', '--spider', url], cwd='/tmp')
            #f'http://{labmanager_ip}:10001/api/savehook/{username}/{owner}/{lbname}?{url_args}'], cwd='/tmp')
    except Exception as e:
        print(e)
