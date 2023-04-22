from pathlib import Path
import sys

import openpyxl
import pandas as pd
import pytest

try: 
    from ..RynekPierwotny import Raport, localisation 
except:  
    sys.path.append(str(Path(sys.path[0]).parent))
    from RynekPierwotny import Raport, localisation    


def test_raport_read_excel(tmpdir):
    df = pd.DataFrame({"Mieszkanie1": [30, "A"], "Mieszkanie2": [40, "B"]})
    fake_file_path = Path(tmpdir / "test_file.xlsx")
    df.to_excel(fake_file_path, index=False)
    function_result = Raport.zad_1(fake_file_path)
    assert df.equals(function_result)


def test_raport_read_excel_raises_exception():
    with pytest.raises(Exception):
        fake_file_path = Path()
        function_result = Raport.zad_1(fake_file_path)
        assert function_result


@pytest.mark.skip(
    reason="""If you want to test this function you need to append your API key, 
than you are free to take of the skip fixture"""
)
def test_localisation():
    assert localisation("Marszałkowska 10") == (52.22, 21.02)
