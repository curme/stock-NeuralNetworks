import json

if __name__ == "__main__":

    config = None
    with file('./FANNS/system.config', 'rw') as f: config = json.load(f)

    config['accounts'] = {}
    config['accounts']['databases'] = {}
    config['accounts']['databases']['mysql_localhost_root'] = {}
    config['accounts']['databases']['mysql_localhost_root']['username'] = 'root'
    config['accounts']['databases']['mysql_localhost_root']['password'] = ''
    config['filepath'] = {}
    config['filepath']['root'] = './FANNS/'
    config['filepath']['data'] = 'Data/'

    json.dump(config, file('./FANNS/system.config', 'w+'))
    print config
