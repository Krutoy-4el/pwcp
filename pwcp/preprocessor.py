from os import path
from io import StringIO
from linecache import getline

from pypp import Preprocessor

from .config import FILE_EXTENSION


class PyPreprocessor(Preprocessor):
    def on_error(self, file, line, msg):
        raise SyntaxError(msg, (file, line, 1, getline(file, line)))


def preprocess(src, p=None):
    if p is None:
        p = PyPreprocessor()
    p.parse(src)
    out = StringIO()
    p.write(out)
    return out.getvalue()


def preprocess_file(filename, config={}):
    with open(filename) as f:
        res = preprocess(f)
    if config.get("save_files"):
        dir, file = path.split(filename)
        if file.endswith(FILE_EXTENSION):
            file = file.rpartition(".")[0] + ".py"
        else:
            file += ".py"
        with open(path.join(dir, file), "w") as f:
            f.write(res)
    return res


def maybe_preprocess(src, filename, preprocessor=None):
    if isinstance(src, bytes):
        src = src.decode()
    if isinstance(src, str):
        # disable preprocessing of non-ppy files by default
        if preprocessor is None and not filename.endswith(FILE_EXTENSION):
            preprocessor = PyPreprocessor(disabled=True)
        # this is essential for interactive mode
        has_newline = src.endswith("\n")
        src = preprocess(src, preprocessor)
        if not has_newline:
            src = src.rstrip("\n")
    return src
