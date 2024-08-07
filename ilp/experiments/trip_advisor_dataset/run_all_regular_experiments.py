import subprocess

# List of scripts to run
scripts = [
    ('experiment_1', 'no_constraints_committee_30.py'),
    ('experiment_2', 'one_dc_committee_30.py'),
    ('experiment_3', 'one_tgd_committee_30.py'),
    ('experiment_4', 'one_dc_one_tgd_committee_30.py'),
    ('experiment_5', 'one_dc_one_tgd_committee_10.py'),
    ('experiment_6', 'one_dc_one_tgd_committee_20.py'),
    ('experiment_7', 'one_dc_one_tgd_committee_30.py'),
    ('experiment_8', 'one_dc_one_tgd_committee_40.py'),
    ('experiment_9', 'one_dc_one_tgd_committee_50.py')
]

# Run each script with the updated global variable
for script_dir, script in scripts:
    subprocess.run(['python', script], cwd=script_dir)
