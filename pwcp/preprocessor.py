from pcpp import Preprocessor
from io import StringIO
from os import path
from .config import FILE_EXTENSION


class PyPreprocessor(Preprocessor):
    def on_comment(self, tok):
        # ignore this type of comments as // is python operation
        if tok.type == self.t_COMMENT2:
            return True
        return False


def preprocess(filename, config={}):
    p = PyPreprocessor(fix_indentation=True)
    with open(filename) as f:
        p.parse(f)
    out = StringIO()
    p.write(out)
    out.seek(0)
    res = out.read()
    if config.get("save_files"):
        dir, file = path.split(filename)
        if file.endswith(FILE_EXTENSION):
            file = file.rpartition(".")[0] + ".py"
        else:
            file += ".py"
        with open(path.join(dir, file), "w") as f:
            f.write(res)
    return res
