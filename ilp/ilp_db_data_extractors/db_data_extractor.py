import time

import database.database_server_interface.database_server_interface as db_interface
import ilp.ilp_reduction.abc_to_ilp_convertor as ilp_convertor


class DBDataExtractor:
    """An abstract class for an ILP experiment.
    """
    def __init__(self,
                 abc_convertor: ilp_convertor.ABCToILPConvertor,
                 database_engine: db_interface.Database):
        self._abc_convertor = abc_convertor
        self._db_engine = database_engine
        self.convert_to_ilp_timer = -1
        self.extract_data_timer = -1

    def _extract_data_from_db(self) -> None:
        # Abstract function.
        pass

    def extract_data_from_db(self) -> None:
        start = time.time()
        self._extract_data_from_db()
        end = time.time()
        self.extract_data_timer = end - start

    def _convert_to_ilp(self) -> None:
        # Abstract function.
        pass

    def convert_to_ilp(self) -> None:
        start = time.time()
        self._convert_to_ilp()
        end = time.time()
        self.convert_to_ilp_timer = end - start

    def extract_and_convert(self) -> None:
        # Extract problem data from the database.
        self.extract_data_from_db()

        # Convert to ILP problem (add the model properties)
        self.convert_to_ilp()

    # TODO: Consider put join tables here.


if __name__ == '__main__':
    pass

