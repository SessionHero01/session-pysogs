#!/usr/bin/env python3

import subprocess
import os
import sys
import tempfile

# Translate environment variables like
# SOGS_X_Y=Z into ini-style config file entries like
# [x]
# y=Z
def translate_env_to_ini(env_vars, output):
    config_map = {}
    prefix = 'SOGS_'
    for name, val in env_vars.items():
        if name.startswith(prefix):
            config_group_name = name[len(prefix):].lower().split('_')[0]
            config_name = name[len(prefix) + len(config_group_name) + 1:].lower()
            if not config_name:
                continue

            config_map[config_group_name] = {
                **config_map.get(config_group_name, {}),
                config_name: val
            }
    
    for group_name, entries in config_map.items():
        output.write(f'[{group_name}]\n')
        for entry_name, entry_val in entries.items():
            output.write(f'{entry_name}={entry_val}\n')
        output.write('\n')


if __name__ == '__main__':
    cmd = sys.argv[1:]

    os_env = dict(**os.environ)

    db_path = os.environ.get('DB_PATH')
    run_db_init = False

    if db_path and 'SOGS_DB_URL' not in os_env:
        print(f"Using database path from DB_PATH: {db_path}")
        if not os.path.exists(db_path):
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            run_db_init = True

        os_env['SOGS_DB_URL'] = f'sqlite:///{db_path}'

    if not cmd:
        cmd = ["uwsgi", "/etc/uwsgi-docker.ini"]

    with tempfile.NamedTemporaryFile(mode='w', suffix='.ini') as temp_ini:
        translate_env_to_ini(os_env, temp_ini)
        temp_ini.flush()

        env = {**os_env, 'SOGS_CONFIG': temp_ini.name}

        # Run the migration first
        if run_db_init:
            print("Initializing database...")
            subprocess.run(['python3', '-msogs', '--initialize'], env=env)


        # Run the program given by the arguments, first argument is the program name
        subprocess.run(cmd, env=env)