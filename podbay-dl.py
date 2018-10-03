import os, sys, re
from bs4 import BeautifulSoup
import requests as req
try:
  from progress.bar import Bar
except:
  print("'progress' module not found. progress will not be shown on downloads.")
  # Do `pip install progress` to download and have progress bars be shown on downloads.

WINDOWS, LINUX = 0, 1
OS = WINDOWS if os.name == 'nt' else LINUX
def mktrn(string, assign):
  return str.maketrans(dict.fromkeys(string, assign))
# For filename translations, if the filename contains an invalid character
fn_tran = mktrn(r'<>:"/\|?*', '-') if OS is WINDOWS else mktrn('/', '-')
Mb = 1024 * 1024
chunk_size = Mb
media_finder = re.compile(".*\.mp3.*")

if 'progress' not in sys.modules:
  def incremental_dl(url, filename):
    with open(filename+'.tmp', 'wb') as file:
      req_data = req.get(url, stream=True)
      print("Downloading '%s'" % filename)
      for data in req_data.iter_content(chunk_size):
        file.write(data)
      print("'%s' downloaded." % filename)
    os.rename(filename+'.tmp', filename)
else:
  def incremental_dl(url, filename):
    with open(filename+'.tmp', 'wb') as file:
      req_data = req.get(url, stream=True)
      size = int(req_data.headers['content-length'])
      bar = Bar(filename, max=size//chunk_size+1)
      for data in req_data.iter_content(chunk_size):
        file.write(data)
        bar.next()
      bar.finish()
    os.rename(filename+'.tmp', filename)

class Episode:
  __slots__ = ['page_url', 'title', 'comment']
  def __init__(self, page, title, comment):
    self.page_url = page
    self.title = title
    self.comment = comment
  def media_url(self):
    soup = BeautifulSoup(req.get(self.page_url).text, 'lxml')
    return soup.find('a', href=media_finder, **{'class': 'btn btn-mini btn-primary'}).get('href')
  def download(self):
    media_url = self.media_url()
    try:
      incremental_dl(media_url, self.title + '.mp3')
    except OSError:
      safe_title = self.title.translate(fn_tran)
      incremental_dl(media_url, safe_title + '.mp3')

class Podbay:
  __slots__ = ['uploader_url', 'name', 'img_url', 'episodes']
  def __init__(self, uploader):
    if uploader.isdigit():
      uploader = "http://podbay.fm/show/" + uploader
    self.uploader_url = uploader
    request = req.get(uploader)
    if request.status_code is not 200:
      raise Exception('URL is not valid \'%s\'' % uploader)
    soup = BeautifulSoup(request.text, 'lxml')
    self.name = soup.find('meta', property='og:title').get('content')
    if self.name == '':
      raise Exception('Failed to retrieve data from \'%s\'' % uploader)
    self.img_url = soup.find('a', rel='lightbox').get('href')
    self.episodes = []
    ep_finder = re.compile(uploader + "/e/.*")
    for data in soup.find_all('a', rel='tooltip', href=ep_finder):
      self.episodes.append(Episode(
        data.get('href'),       #url
        data.string,            #title
        data.get('title')[3:-4] #comment
      ))
  def is_downloaded(self, title):
      #return os.path.exists(self.episodes[title].title+'.mp3')
      return os.path.exists(title+'.mp3')
  def download(self, folder=None):
    folder = folder if folder else self.name
    if not os.path.exists(folder):
      try:
        os.mkdir(folder)
      except OSError:
        folder = folder.translate(fn_tran)
        if not os.path.exists(folder):
          os.mkdir(folder)
    os.chdir(folder)
    if not os.path.exists('cover.jpg'):
      incremental_dl(self.img_url, 'cover.jpg')
    for episode in self.episodes[::-1]:
      if not self.is_downloaded(episode.title):
        episode.download()

if __name__ == "__main__":
  if len(sys.argv) < 1:
    raise ValueError('Missing parameters: full_url/show_id...')
  for url in sys.argv[1:]:
    uploader = Podbay(url)
    uploader.download()

