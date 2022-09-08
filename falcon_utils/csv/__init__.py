import pandas as pd
import base64
from io import StringIO

def read_bas64_csv(base64_string: "str") -> "pd.DataFrame":
    csv_bytes = base64.b64decode(base64_string)
    csv_text = csv_bytes.decode('latin-1')
    csv_text = StringIO(csv_text)
    df = pd.read_csv(csv_text)
    return df
    