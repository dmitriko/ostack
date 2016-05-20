#!/usr/bin/python
""" Update MongoDB config from Ansible"""
from ansible.module_utils.basic import *  # pylint: disable=unused-wildcard-import,wildcard-import


MONGO_CONF = '/etc/mongod.conf'


def conf_as_dict(conf_path):
    "Return dict with values parsed from config"
    result = {}
    content = open(conf_path).read()
    for line in content.splitlines():
        if not line:
            continue
        if line.startswith('#'):
            continue
        if '=' in line:
            part1, part2 = line.split('=', 1)
        result[part1.strip()] = part2.strip()
    return result


def fix_content(content, data, added_keys):
    """Accept list of strings and return list of strings
    fixed with new data

    """
    def coerce_value(value):
        "Convert Python value to mongo conf value"
        if isinstance(value, bool):
            return str(value).lower()
        return value

    def format_line(key, value):
        "Return string key=value"
        return "{0}={1}".format(key, coerce_value(value))        

    def fix_line(line, data):
        "Fix line with data if needed, return without changes if ok"
        if line.startswith('#'):
            return line
        for key, value in data.items():
            if line.startswith(key):
                return format_line(key, value)
        return line

    result = []
    for line in content:
        result.append(fix_line(line, data))
    for key in added_keys:
        result.append(format_line(key, data[key]))
    return result


def doit(data):
    "Return True if changes were made, False othervise"
    changed = False
    conf_path = data.pop('conf_path')
    conf = conf_as_dict(conf_path)
    added_keys = []
    for key in data:
        if not key in conf:
            changed = True
            added_keys.append(key)
            continue
        if data[key] is None:
            continue
        if str(conf[key]).lower() != str(data[key]).lower():
            changed = True
    if not changed:
        return False
    content = [x.strip() for x in open(conf_path).read().splitlines()]
    new_content = fix_content(content, data, added_keys)
    with open(conf_path, 'w') as file_:
        file_.write("\n".join(new_content))
    return True


def main():
    "Process args and call doit"
    module = AnsibleModule(
        argument_spec={
            'auth': {'required': False, 'type': 'bool'},
            'smallfiles': {'required': False, 'type': 'bool'},
            'dbpath': {'required': False, 'type': 'str'},
            'bind_ip': {'required': False, 'type': 'str'},
            'conf_path': {'default': MONGO_CONF, 'type': 'str'}
            }
        )
    data = {}
    for key, value in module.params.items():
        if value is not None:
            data[key] = value
    module.exit_json(changed=doit(data))


if __name__ == '__main__':
    main()
