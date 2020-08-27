import functools


def cases(cases):
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args):
            for c in cases:
                new_args = args + (c if isinstance(c, tuple) else (c,))
                try:
                    f(*new_args)
                except Exception as e:
                    params_msg = ", ".join(map(str, new_args[1:]))
                    if e.args and e.args[0]:
                        msg = e.args[0]
                        e.args = (str(msg) + " : " + params_msg,)
                    else:
                        e.args = (params_msg,)
                    raise
        return wrapper
    return decorator
