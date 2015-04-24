import config_default


class Dict(dict):
    # An improved dictionary that supports attribute access like 'dict.x = value'
    def __init__(self, names=(), values=(), **kw):
        super(Dict, self).__init__(**kw)
        for key, value in zip(names, values):
            self[key] = value

    def __getattr__(self, item):
        try:
            return self[item]
        except KeyError:
            raise AttributeError("'Dict' object has no attribute %s" % item)

    def __setattr__(self, key, value):
        self[key] = value

# Merge two dicts.
def merge(defaults, override):
    r = {}
    for key, value in defaults.iteritems():
        if key in override:
            if isinstance(value, dict):
                r[key] = merge(value, override[key])
            else:
                r[key] = override[key]
        else:
            r[key] = value
    return r

# Convert an ordinary dict data to Dict object which supports attribute access.
def toDict(d):
    D = Dict()
    for key, value in d.iteritems():
        D[key] = toDict(value) if isinstance(value, dict) else value
    return D

configs = config_default.configs

try:
    import config_override
    configs = merge(configs, config_override.configs)
except ImportError:
    pass

configs = toDict(configs)

# For flask app
SECRET_KEY = configs.session.secret
DEBUG = True
TESTING = True