#!/usr/bin/python
""" Update OpenStack config from Ansible using crudini"""
from ansible.module_utils.basic import *  # pylint: disable=unused-wildcard-import,wildcard-import
from subprocess import Popen, PIPE


def set_option(data):
    "Set value in config, return crudini stderr output)"
    if not data['value']:
        raise RuntimeError("Value is not provided")
    if not os.path.exists(data['dest']):
        raise RuntimeError(
            "Config file does not exist at %s" % data['dest'])
    proc = Popen(['crudini', '--verbose', '--set',
                  data['dest'], data['section'], data['option'], data['value']],
                 stdout=PIPE, stderr=PIPE)

    _, out = proc.communicate()
    return out


def del_option(data):
    "Delete option in config, return crudini stderr output)"
    if not os.path.exists(data['dest']):
        raise RuntimeError(
            "Config file does not exist at %s" % data['dest'])
    proc = Popen(['crudini', '--verbose', '--del',
                  data['dest'], data['section'], data['option']],
                 stdout=PIPE, stdin=PIPE)
    _, out = proc.communicate()
    return out


def main():
    "Process args and call crudini to set or remove option"
    module = AnsibleModule(
        argument_spec={
            'dest': {'required': True, 'type': 'str'},
            'section': {'required': True, 'type': 'str'},
            'option': {'required': True, 'type': 'str'},
            'value': {'required': False, 'type': 'str'},
            'state': {'default': 'present',
                      'choices': ['present', 'absent'],
                      'type': 'str'}
            }
        )
    changed = True
    try:
        if module.params['state'] == 'present':
            output = set_option(module.params)
        else:
            output = del_option(module.params)
        if 'unchanged' in output:
            changed = False
        module.exit_json(changed=changed, msg=output)
    except Exception, exc:  #pylint: disable=broad-except
        module.fail_json(changed=changed, msg=str(exc))


if __name__ == '__main__':
    main()
