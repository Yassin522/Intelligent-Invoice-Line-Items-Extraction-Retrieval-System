import logging
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions, TableStructureOptions
from docling.datamodel.base_models import InputFormat

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def ingest_invoice(file_path):
    """
    Ingests a PDF and extracts structured data using Docling.
    """
    logger.info(f"Starting ingestion for: {file_path}")
    
    # 1. Configure the Inner Pipeline Options (OCR, Table Structure)
    pipeline_opts = PdfPipelineOptions()
    pipeline_opts.do_ocr = True
    pipeline_opts.do_table_structure = True
    pipeline_opts.table_structure_options.do_cell_matching = True 

    # 2. Configure the Format Option Wrapper
    pdf_format_option = PdfFormatOption(
        pipeline_options=pipeline_opts
    )

    # 3. Initialize Converter with the Wrapper
    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: pdf_format_option
        }
    )

    # 4. Convert the document
    try:
        doc_result = converter.convert(file_path)
        return doc_result.document.export_to_dict()
    except Exception as e:
        logger.error(f"Failed to ingest {file_path}: {e}")
        import traceback
        traceback.print_exc()
        return None