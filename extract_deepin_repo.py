#! /usr/bin/env python3

import gzip
import json
import os
import re
import sys
import urllib.parse
import urllib.request

request_cache_dir = None


def request_url(url):
    use_cache = request_cache_dir is not None
    cache_file = os.path.join(request_cache_dir, urllib.parse.quote(url, safe=''))
    if use_cache and os.path.isfile(cache_file):
        with open(cache_file, 'rb') as fin:
            content = fin.read()
    else:
        response = urllib.request.urlopen(url)
        assert response.status == 200
        content = response.read()
        if use_cache:
            os.makedirs(request_cache_dir, exist_ok=True)
            with open(cache_file, 'wb') as fout:
                fout.write(content)
    return content


class Package:
    def __init__(self, control):
        self.control = control

    def search_key(self, key):
        pattern = rf'(^{re.escape(key)} *: *)(.+(?:\n .+)*)'.replace(' ', r'[^\S\n]')
        return re.search(pattern, self.control, re.I | re.M)

    def update(self, key, value):
        match = self.search_key(key)
        control = self.control[:match.start(0)] + match.group(1) + value + self.control[match.end(0):]
        return Package(control)

    def __getitem__(self, key):
        match = self.search_key(key)
        return match.group(2) if match else None

    def __str__(self):
        return self.control


class Repository:
    COMMENT_PATTERN = re.compile(r'^#.*\n?', re.M)

    def __init__(self, repo_config=None):
        self.packages = {}
        if repo_config is None:
            return
        for url in repo_config['packages_files']:
            url = repo_config['location'] + url
            packages_file = request_url(url)
            if url.endswith('.gz'):
                packages_file = gzip.decompress(packages_file)
            packages_file = re.sub(Repository.COMMENT_PATTERN, '', packages_file.decode())
            for paragraph in packages_file.split('\n\n'):
                if paragraph and not paragraph.isspace():
                    self.add(Package(paragraph))

    def keys(self):
        return self.packages.keys()

    def add(self, package):
        name = package['Package']
        if name is None:
            print(package.control)
        assert name is not None
        try:
            self.packages[name].append(package)
        except KeyError:
            self.packages[name] = [package]

    def __contains__(self, name):
        return len(self[name]) > 0

    def __getitem__(self, name):
        name = re.search(r'[^\s:(]+', name)
        name = name.group() if name is not None else None
        try:
            return self.packages[name]
        except KeyError:
            return []


def extract_packages(diff, src, dest, train):
    name = train[0]
    missing_packages = []
    if name not in diff and name not in dest:
        packages = src[name]
        if not packages:
            missing_packages.append(train)
        else:
            for pkg in packages:
                diff.add(pkg)
                for alt_depend in (pkg['Depends'] or '').split(','):
                    satisfied = False
                    current = len(missing_packages)
                    for depend in filter(len, map(str.strip, alt_depend.split('|'))):
                        unsatisfied = extract_packages(diff, src, dest, [depend] + train)
                        missing_packages.extend(unsatisfied)
                        satisfied |= not unsatisfied
                    if satisfied:
                        missing_packages = missing_packages[:current]
    return missing_packages


def extract_deepin_repo(config, filename_prefix):
    deepin_repo = Repository(config['deepin_repository'])
    app_names = config['apps']

    for host, host_config in config['host_repositories'].items():
        print('>>> ', host)
        host_repo = Repository(host_config)

        extracted_packages = Repository()
        for app_name in app_names:
            unresolvable = extract_packages(extracted_packages, deepin_repo, host_repo, [app_name])
            for missing in unresolvable:
                print('缺失软件包:', ' <- '.join(missing))
        packages_file = ''
        for name in sorted(extracted_packages.keys()):
            for pkg in extracted_packages[name]:
                pkg = pkg.update('Filename', filename_prefix + pkg['Filename'])
                packages_file += str(pkg) + '\n\n'
        yield host, packages_file


if __name__ == '__main__':
    request_cache_dir = sys.argv[4]
    with open(sys.argv[1], 'rt') as f:
        config = json.load(f)
    for host, packages_file in extract_deepin_repo(config, sys.argv[3]):
        folder = os.path.join(sys.argv[2], host)
        os.makedirs(folder, exist_ok=True)
        with open(os.path.join(folder, 'Packages'), 'wt') as f:
            f.write(packages_file)
