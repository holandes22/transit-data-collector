import os

import click
import requests
import requests_ftp

requests_ftp.monkeypatch_session()


class FTPCollector(object):

    def __init__(self, addr, filename):
        self.session = requests.Session()
        self.addr = 'ftp://{}/'.format(addr)
        self.filename = filename
        self.dst_path = '.'
        self.url = '{}{}'.format(self.addr, self.filename)
        dst_filename = self.get_dst_filename()
        self.dst_filepath = os.path.join(self.dst_path, dst_filename)

    def get_dst_filename(self):
        resp = self.session.list(self.addr)
        resp.raise_for_status()
        for line in resp.content.split('\n'):
            if self.filename in line:
                date, time = line.split()[:2]
                filename, ext = self.filename.split('.')
                return '{}_{}_{}.{}'.format(filename, date, time, ext)
        raise ValueError('File {} not found in server'.format(self.filename))

    def collect(self):
        if os.path.exists(self.dst_filepath):
            return
        click.secho('Downloading file', fg='green')
        resp = self.session.get(self.url)
        click.secho('Saving file', fg='green')
        with open(self.dst_filepath, 'wb') as fdescriptor:
            with click.progressbar(resp.iter_content(1024)) as bar:
                for chunk in bar:
                    fdescriptor.write(chunk)

@click.command()
@click.option('--addr', default='gtfs.mot.gov.il', help='Address of the server')
@click.argument('filename')
def collect(addr, filename):
    FTPCollector(addr, filename).collect()


if __name__ == '__main__':
    collect()
