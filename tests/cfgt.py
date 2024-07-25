import sys

sys.path.append("/proj/python/pyappm/src/pyappm")

from configuration import PyAPPMConfiguration  # type: ignore

cfg = PyAPPMConfiguration().load()
print(cfg.authors)
