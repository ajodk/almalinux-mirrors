#!/usr/bin/env python3

import yaml
import os
import shutil
import requests
import sys

def mirror_available(mirror):
    """Check mirror availability."""
    try:
        mirror['address']['https']
    except:
        print('No https address for mirror ' + mirror['name'])
        return False
    for version in config['version']:
        for repo in config['repos']:
            check_url = ("%s%s/%srepodata/repomd.xml" % (mirror['address']['https'], version, repo['path'])).replace('$basearch', 'x86_64')
            request = requests.get(check_url)
            if request.status_code != 200:
                print('Mirror ' + mirror['name'] + ' is NOT available')
                return False
    print('Mirror ' + mirror['name'] + ' is available')
    return True

# read config
with open('config.yml') as f:
    config = yaml.safe_load(f)
    mirrorlist_dir = config['mirrorlist_dir']
    mirrors_dir = config['mirrors_dir']

# delete mirrorlist dir if exists
shutil.rmtree(mirrorlist_dir, ignore_errors=True)

# read and verify mirrors
verified_mirrors = []
for mirror_file in os.listdir(mirrors_dir):
    with open(mirrors_dir + '/' + mirror_file) as f:
        # filter broken or unavailable mirrors
        try:
            mirror = yaml.safe_load(f)
            mirror['name']
        except:
            print('Cannot load mirror data from file ' + mirror_file)
            continue
        if mirror_available(mirror):
            verified_mirrors.append(mirror)

# exit if no mirrors found
if verified_mirrors == []:
    sys.exit('No working mirrors found')

# write verified mirrors to mirrorlist files
for mirror in verified_mirrors:
    for version in config['version']:
        os.makedirs(mirrorlist_dir + '/' + str(version), exist_ok=True)
        for repo in config['repos']:
            path = mirror['address']['https'] + str(version) + '/' + repo['path']
            with open(mirrorlist_dir + '/' + str(version) + '/' + repo['name'], 'a') as f:
                print(path, file=f)