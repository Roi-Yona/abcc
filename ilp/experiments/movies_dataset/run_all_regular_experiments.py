import subprocess

# List of scripts to run
scripts = [
    ('experiment_1', 'no_constraints.py'),
    ('experiment_2', 'one_dc.py'),
    ('experiment_3', 'one_tgd.py'),
    ('experiment_4', 'one_dc_one_tgd.py'),
    ('experiment_5', 'one_tgd_committee_10.py'),
    ('experiment_6', 'one_tgd_committee_20.py'),
    ('experiment_7', 'one_tgd_committee_30.py'),
    ('experiment_8', 'one_tgd_committee_40.py'),
    ('experiment_9', 'one_tgd_committee_50.py'),
    ('experiment_10', 'one_dc_one_tgd_av.py'),
    ('experiment_11', 'one_dc_one_tgd_2_truncated_av.py'),
    ('experiment_12', 'one_dc_one_tgd_pav.py'),
    ('experiment_13', 'one_dc_one_tgd_cc.py'),
    ('experiment_14', 'one_dc_one_tgd_sav.py'),
    ('experiment_17', 'one_dc_one_tgd_0_opt.py'),
    ('experiment_16', 'one_dc_one_tgd_1_opt.py'),
    ('experiment_15', 'one_dc_one_tgd_2_opt.py'),
    ('experiment_18', 'one_dc_one_tgd_3_opt.py'),
]

# Run each script with the updated global variable
for script_dir, script in scripts:
    subprocess.run(['python3', script], cwd=script_dir)
