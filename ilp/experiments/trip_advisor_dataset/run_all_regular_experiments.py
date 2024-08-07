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
    ('experiment_9', 'one_dc_one_tgd_committee_50.py'),
    ('experiment_10', 'one_dc_one_tgd_committee_15_av.py'),
    ('experiment_11', 'one_dc_one_tgd_committee_15_pav.py'),
    ('experiment_12', 'one_dc_one_tgd_committee_15_2_truncated_av.py'),
    ('experiment_13', 'one_dc_one_tgd_committee_15_cc.py'),
    ('experiment_14', 'one_dc_one_tgd_committee_15_sav.py'),
    ('experiment_15', 'one_dc_one_tgd_committee_30_2_opt.py'),
    ('experiment_16', 'one_dc_one_tgd_committee_30_1_opt.py'),
    ('experiment_17', 'one_dc_one_tgd_committee_30_0_opt.py'),
]

# Run each script with the updated global variable
for script_dir, script in scripts:
    subprocess.run(['python', script], cwd=script_dir)
