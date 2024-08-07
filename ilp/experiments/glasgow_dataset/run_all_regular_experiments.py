import subprocess

# List of scripts to run
scripts = [
    ('experiment_1', 'no_constraints.py'),
    ('experiment_2', 'one_dc.py'),
    ('experiment_3', 'one_tgd.py'),
    ('experiment_4', 'one_dc_one_tgd.py'),
    ('experiment_5', 'two_tgd.py'),
    # ('experiment_6', 'one_tgd_3_representores_per_district.py'),
    ('experiment_7', 'one_dc_one_tgd_av.py'),
    ('experiment_8', 'one_dc_one_tgd_cc.py'),
    ('experiment_9', 'one_dc_one_tgd_2_truncated_av.py'),
    ('experiment_10', 'one_dc_one_tgd_sav.py'),
    ('experiment_11', 'one_dc_one_tgd_2_opt.py'),
    ('experiment_12', 'one_dc_one_tgd_1_opt.py'),
    ('experiment_13', 'one_dc_one_tgd_0_opt.py'),
]

# Run each script with the updated global variable
for script_dir, script in scripts:
    subprocess.run(['python3', script], cwd=script_dir)
