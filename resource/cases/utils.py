"""
    Script utilizado para performar a organização dos dados obtidos
    antes de realizar asserções.
"""

import pandas as pd

def perform_array_column_to_count(df: pd.DataFrame, field: str) -> list:
    """
        Função recursiva que que realiza iteração para cada nome
        encontrado em field info
    """
    try:
        counter = pd.DataFrame()
        fields = field.split('.')
        
        for f in fields:

            first_occurrence = df[f].dropna().iloc[0] if f in df else None
            is_list = isinstance(first_occurrence, list) if first_occurrence is not None else False
            
            if is_list:

                counter[f] = df[f].apply(len)
                
                if len(fields) > 1:

                    group_nested = []
                    
                    for _, row in df.iterrows():
                        nested = pd.DataFrame(row[f])
                        group_nested.append(nested)
                    
                    combine = pd.concat(group_nested, keys=df.index)
                    
                    return perform_array_column_to_count(combine, '.'.join(fields[1:]))
        return list(counter[field])
    except Exception:
        return []
