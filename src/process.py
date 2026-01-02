import pandas as pd
import logging

logger = logging.getLogger(__name__)

def process_and_stitch(doc_dict):
    """
    Converts raw Docling tables into Pandas DataFrames, finds the true headers,
    and stitches multi-page fragments.
    """
    if not doc_dict or 'tables' not in doc_dict:
        logger.warning("No tables found in document.")
        return []

    # 1. Convert specific Docling table structure to Pandas DataFrames
    raw_tables = []
    for t_item in doc_dict['tables']:
        data_node = t_item.get('data', [])
        if isinstance(data_node, dict) and 'grid' in data_node:
            grid = data_node['grid']
        elif isinstance(data_node, list):
            grid = data_node
        else:
            continue
        
        # Extract text content
        clean_grid = []
        for row in grid:
            clean_row = []
            for cell in row:
                if isinstance(cell, dict) and 'text' in cell:
                    clean_row.append(cell['text'].strip())
                else:
                    clean_row.append(str(cell).strip())
            clean_grid.append(clean_row)
        
        if not clean_grid:
            continue

        df = pd.DataFrame(clean_grid)
        
        # Add metadata
        page_no = 1
        if 'prov' in t_item and len(t_item['prov']) > 0:
             page_no = t_item['prov'][0].get('page_no', 1)
        df['_page'] = page_no
        raw_tables.append(df)

    if not raw_tables:
        return []

    stitched_tables = []
    current_buffer = raw_tables[0]

    for next_table in raw_tables[1:]:
        cols_match = len(current_buffer.columns) == len(next_table.columns)
        
        last_page = current_buffer['_page'].iloc[-1]
        next_page = next_table['_page'].iloc[0]
        is_next_page = next_page == last_page + 1

        if cols_match and is_next_page:
            data_to_append = next_table
            current_buffer = pd.concat([current_buffer, data_to_append], ignore_index=True)
        else:
            stitched_tables.append(current_buffer)
            current_buffer = next_table

    stitched_tables.append(current_buffer)
    
    # 3. Clean up and Find True Headers
    final_cleaned = []
    for df in stitched_tables:
        if df.empty:
            continue

        # Look for a row containing "Description" or "Amount" in the first 5 rows
        header_idx = 0
        for idx in range(min(5, len(df))):
            row_values = [str(x).lower() for x in df.iloc[idx].values]
            if any(k in row_values for k in ['description', 'amount', 'qty', 'price', 'total']):
                header_idx = idx
                break
    
        # Promote the found row to header
        new_header = df.iloc[header_idx]
        
        # Filter the DataFrame to only include rows AFTER the header
        df = df.iloc[header_idx+1:].copy()
        df.columns = new_header
        
        # Drop metadata column if exists
        if '_page' in df.columns:
            df = df.drop(columns=['_page'])
            
        # Remove empty rows
        df = df.dropna(how='all')
        
        # Only keep tables that actually have data left
        if not df.empty:
            final_cleaned.append(df)

    return final_cleaned