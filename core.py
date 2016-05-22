__author__ = 'jqol'

import http.cookiejar
import urllib.request
import urllib.parse
import json
import re
import os

QUERY_POST_DATA = """ig_user(%s) { media.after(%s, %d) {
  count,
  nodes {
    caption,
    code,
    comments {
      count
    },
    date,
    dimensions {
      height,
      width
    },
    display_src,
    id,
    is_video,
    likes {
      count
    },
    owner {
      id
    },
    thumbnail_src
  },
  page_info
}
 }"""

DOWNLOAD_DIR = os.path.curdir + '//download'
try:
    os.mkdir(DOWNLOAD_DIR)
except FileExistsError:
    pass


class InstaCrawler:
    def __init__(self, username):
        self._user_name = username
        self._user_id = 0
        self._cookJar = http.cookiejar.CookieJar()
        self._opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self._cookJar))

    def refresh_list(self):
        with self._opener.open("https://www.instagram.com/%s/?__a=1" % self._user_name) as r:
            rs = r.read().decode('utf-8', 'strict')
        user_json = json.loads(rs)['user']
        self._user_id = user_json['id']
        count = user_json['media']['count']
        done = 0
        for node in user_json['media']['nodes']:
            done += 1
            print('[%d/%d]' % (done, count))
            self.process_media_node(node)
        cursor = user_json['media']['page_info']['end_cursor']
        while True:
            query_url = 'https://www.instagram.com/query/?' \
                        + urllib.parse.urlencode({'q':
                                                      QUERY_POST_DATA % (self._user_id, cursor, 100),
                                                  'ref': 'users::show'}
                                                 )
            with self._opener.open(query_url) as r:
                rs = r.read().decode('utf-8', 'strict')
            page_json = json.loads(rs)['media']
            for node in page_json['nodes']:
                done += 1
                print('[%d/%d]' % (done, count))
                self.process_media_node(node)
            if not page_json['page_info']['has_next_page']:
                break
            cursor = page_json['page_info']['end_cursor']

    def process_media_node(self, node):
        retry = 0
        while retry < 3:
            retry += 1
            src = node['display_src']
            assert isinstance(src, str)
            try:
                if node['is_video']:
                    self.download_video(node['code'])
                else:
                    src = re.sub('/s\d+x\d+', '', src)
                    f = node['code'] + ".jpg"
                    self.download_image(src, f)
            except urllib.error.URLError as e:
                print(e)
                print('retry %d' % retry)
            break

    def download_file(self, url, f):
        print('downloading file[%s]==%s' % (url, f))
        file_path = DOWNLOAD_DIR + '/' + f
        if os.path.isfile(file_path):
            print('File[%s] exits, skip downloading!!'% file_path)
            return
        try:
            response = self._opener.open(url)
            open(file_path, mode='wb').write(response.read())
        except urllib.error.URLError as e:
            print(e)
            if os.path.isfile(file_path):
                os.remove(file_path)
            raise

    def download_image(self, url, f):
        print('downloading image[%s]==%s' % (url, f))
        self.download_file(url, f)

    def download_video(self, code):
        print('downloading video[%s]=>%s.mp4' % (code, code))
        video_url = ''
        with self._opener.open('https://www.instagram.com/p/%s/?__a=1' % code) as response:
            video_json = json.loads(response.read().decode('utf-8', 'strict'))
            video_url = video_json['media']["video_url"]
        self.download_file(video_url, '%s.mp4' % code)


if __name__ == "__main__":
    InstaCrawler('theellenshow').refresh_list()
