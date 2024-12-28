import streamlit as st

import config
import mip.experiments.combined_constraints_experiment as combined_constraints_experiment
import frontend.utils as utils
import frontend.abc_settings_input as abc_settings_input
import frontend.problem_output as problem_output
import frontend.contextual_constraints_input_tgd as contextual_constraints_input_tgd
import mip.mip_db_data_extractors.dc_extractor as dc_extractor

MODULE_NAME = f'Main Screen'


def main():
    utils.page_setting()

    # User input ABC with Context problem settings.
    selected_db, selected_rule, committee_size, tgds, dcs = abc_settings_input.abc_settings_input()
    voters_starting_point, voters_group_size, candidates_starting_point, candidates_group_size, solver_timeout = \
        abc_settings_input.advanced_abc_settings_input(selected_db)

    # Display selected options (debug purposes).
    abc_settings_input.present_selected_configuration(selected_db, selected_rule, committee_size, tgds, dcs,
                                                      voters_starting_point, voters_group_size,
                                                      candidates_starting_point, candidates_group_size, solver_timeout)

    # Submit button
    if st.button("Find a winning committee"):
        # TODO: Validate that all DC comparison atoms are valid variables.
        # is_valid, message = contextual_constraints_input_tgd.validate_tgd_constraint(tgds)
        is_valid = True
        message = ""
        if not is_valid:
            st.error(message)
        else:
            st.success("Configuration submitted successfully!")
            st.markdown("Searching for a winning committee...")

            experiment_name = 'user_interface_experiment'
            # Set the new selected voting rule and solver timeout.
            config.SCORE_RULE_NAME = selected_rule
            config.SCORE_FUNCTION = config.SCORE_RULES[selected_rule]
            # Converting to milliseconds.
            config.SOLVER_TIME_LIMIT = solver_timeout * 1000 * 60
            current_experiment = combined_constraints_experiment.CombinedConstraintsExperiment(experiment_name, selected_db,
                                                                                               dcs, tgds,
                                                                                               committee_size,
                                                                                               voters_starting_point,
                                                                                               candidates_starting_point,
                                                                                               voters_group_size,
                                                                                               candidates_group_size)

            # Run the experiment.
            # TODO: Present progress bar (of the solver and the stage..).
            try:
                experiment_results_row_df = current_experiment.run_experiment()
                # Present the results.
                problem_output.present_solver_results(current_experiment.get_db_engine(), experiment_results_row_df)
            except dc_extractor.DCConstraintConvertFailed as e:
                st.error(e.__str__())


if __name__ == "__main__":
    main()
