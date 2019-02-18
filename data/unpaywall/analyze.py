from data.unpaywall import read_all
from data import parse_jsonl_parallel

fields = set()


def analyze_array(data: list, name: str):
    for item in data:
        yield from analyze_object(item, name)


def analyze_object(data: dict, recurse: str) -> (str,type):
    for name, value in data.items():
        if value is None:
            continue

        t = type(value)
        if list is t:
            yield from analyze_array(value, recurse+'.'+name)
        if dict is t:
            yield from analyze_object(value, recurse+'.'+name)

        result = (recurse + '.' + name, t)
        if result not in fields:
            fields.add(result)
            yield result


def analyze():
    for num, (line, json) in enumerate(parse_jsonl_parallel(read_all(), processes=1)):
        yield from analyze_object(json, 'obj')


if __name__ == '__main__':
    results = {}
    for name, typ in analyze():
        print(name, typ)
        results[name] = typ

    with open('unpaywall.analyze.result','w') as file:
        for name, typ in results.items():
            file.write(f'{name:60s} {typ}\n')