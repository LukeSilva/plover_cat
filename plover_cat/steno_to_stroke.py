from plover import system
from plover.steno import Stroke

def steno_to_stroke(steno):
    if steno_to_stroke.system != system.NAME:
        keys = []
        letters = ''
        has_hyphen = False
        for k in system.KEYS:
            if not has_hyphen and k.startswith('-'):
                has_hyphen = True
                keys.append(None)
                letters += '-'
            keys.append(k)
            letters += k.strip('-')
        steno_to_stroke.keys = keys
        steno_to_stroke.letters = letters
        steno_to_stroke.system = system.NAME
        steno_to_stroke.numbers = {
            v.strip('-'): k.strip('-')
            for k, v in system.NUMBERS.items()
        }
    n = -1
    keys = set()
    for l in steno:
        rl = steno_to_stroke.numbers.get(l)
        if rl is not None:
            keys.add('#')
            l = rl
        n = steno_to_stroke.letters.find(l, n + 1)
        assert n >= 0, (steno_to_stroke.letters, l, n)
        k = steno_to_stroke.keys[n]
        if k is not None:
            keys.add(k)
    return Stroke(keys)

steno_to_stroke.system = None
