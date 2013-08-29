import os.path
import subprocess
import tornado.autoreload
import tornado.ioloop

#an alternative:
#watchmedo shell-command --pattern="*.rst;*.py" --recursive --command="make html" .

included_ext = ['.py', '.rst', '.css', '.html']

def build():
    subprocess.call('make html'.split())
    #restart dev server
    subprocess.call('touch ../src/index.py'.split())

def watch_rst(arg, dirname, fnames):
    for fn in fnames:
        for ext in included_ext:
            if fn.endswith(ext):
                f_path = os.path.join(dirname, fn)
                tornado.autoreload.watch(f_path)
                #print f_path, os.path.exists(f_path)

def main():
    tornado.autoreload.add_reload_hook(build)
    os.path.walk('.', watch_rst, None)
    loop = tornado.ioloop.IOLoop.instance()
    tornado.autoreload.start(loop)
    loop.start()

if __name__ == '__main__':
    main()