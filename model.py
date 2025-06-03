from pydantic import BaseModel
from typing import List, Dict, Optional

class StrainGenes(BaseModel):
    strain_id: Optional[str] = None
    gene_id: Optional[str] = None

class AntigenEpitopeSequence(BaseModel):
    Epitopes_Sequence: str 
    Strain_Name: str
    Antigen_Name: str 
    Organism: str 
    References: int 
    Assays: int 

class StrainID(BaseModel):
    strain_id: str

class SelectByStrainSequence(BaseModel):
    query: str;
    match_count: int;
    mismatches: int;
    query_start: int;
    query_end: int;
    target: str;
    strand: str;
    target_start: int;
    target_end: int;
    block_counts: int;

class ChartData:
    chart_id: int  
    name: str 
    color: str 
    strain_id: str
    GBID: str
    position: int
    value: float

class EpitopeSeqData:
    Epitope_Name: str
    Strain_Name: str
    Epitope_Source_Molecule: str
    Epitope_Source_Organism: str
    References: str
    Assay: str

class AntigenData:
    Antigen_Name: str
    Strain_Name: str
    Organism: str
    Epitopes: int
    Assays: int
    References: int

# สร้าง Pydantic model สำหรับผลลัพธ์
class EpitopeSequenceTcellResponse(BaseModel):
    Antigen_Name: str
    Epitopes_Sequence: str
    Mapped_Start_Position: int
    Mapped_End_Position: int
    Subjects_Tested: int | None
    Response_Freq_95_CI: float | None

    class Config:
        from_attributes = True

