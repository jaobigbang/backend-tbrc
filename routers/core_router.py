from fastapi import APIRouter, Query, HTTPException
from typing import List, Dict
from collections import defaultdict
# from blast import run_blast

from database import get_cursor
from model import (
    StrainGenes, AntigenEpitopeSequence, StrainID,
    SelectByStrainSequence, ChartData,EpitopeSequenceTcellResponse
)

router = APIRouter()

def query_to_database(sql: str, table: str, values=None):
    connection, cursor = get_cursor()
    try:
        cursor.execute(sql, values)
        results = cursor.fetchall()
        if not results:
            raise HTTPException(status_code=404, detail=f"No matching {table} found")
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        connection.close()

@router.get("/")
async def root():
    return {"message": "Hello World FastAPI"}


######
@router.get('/antigen-epitope-all/')
async def get_list_antigen_epitope_all() -> List[Dict]:
    # sql = """SELECT     
    #         epitope_antigen_data.Epitope_Source_Molecule AS Antigen_Name,
    #         epitope_antigen_data.Epitope_Object_Type,
    #         epitope_antigen_data.Antigen_IRI,
    #         epitope_antigen_data.References,
    #         COUNT(epitope_antigen_data.Epitope_Name) AS Epitope,
    #         IFNULL(Assay.count, 0) AS Assay
    #     FROM (
    #         SELECT 
    #             epitope_table.Epitope_Name,
    #             SUBSTRING_INDEX(antigen_table.Antigen_Name, '(', 1) AS Epitope_Source_Molecule,
    #             epitope_table.Epitope_Object_Type,
    #             antigen_table.Antigen_IRI,
    #             antigen_table.References
    #         FROM 
    #             antigen_table
    #         RIGHT JOIN 
    #             epitope_table 
    #             ON SUBSTRING_INDEX(antigen_table.Antigen_Name, '(', 1) = epitope_table.Source_Molecule
    #     ) AS epitope_antigen_data
    #     LEFT JOIN (
    #         SELECT Epitope_Name, COUNT(*) AS count
    #         FROM tcell_data 
    #         GROUP BY Epitope_Name
    #     ) AS Assay
    #     ON epitope_antigen_data.Epitope_Name = Assay.Epitope_Name
    #     WHERE epitope_antigen_data.Antigen_IRI IS NOT NULL
    #     GROUP BY 
    #         epitope_antigen_data.Epitope_Source_Molecule,
    #         epitope_antigen_data.Epitope_Object_Type,
    #         epitope_antigen_data.Antigen_IRI,
    #         epitope_antigen_data.References,
    #         Assay.count;"""
    sql = """WITH assay_count AS (
                SELECT 
                    tcell_data.Epitope_Source_Molecule,
                    COUNT(tcell_data.Epitope_Name) AS count
                FROM tcell_data
                GROUP BY tcell_data.Epitope_Source_Molecule
            )

            SELECT 
                COUNT(epitope_table.Epitope_Name) AS Epitope,
                IFNULL(epitope_table.Source_Molecule, '') AS Antigen_Name,
                IFNULL(epitope_table.Epitope_Object_Type, '') AS Epitope_Object_Type,
                IFNULL(antigen_table.Antigen_IRI, '') AS Antigen_IRI,
                antigen_table.References,
                IFNULL(assay_count.count, 0) AS Assay
            FROM 
                epitope_table
            LEFT JOIN assay_count 
                ON assay_count.Epitope_Source_Molecule = epitope_table.Source_Molecule
            LEFT JOIN antigen_table 
                ON TRIM(SUBSTRING_INDEX(antigen_table.Antigen_Name, ' (', 1)) = epitope_table.Source_Molecule
            GROUP BY 
                epitope_table.Source_Molecule,
                epitope_table.Epitope_Object_Type,
                antigen_table.Antigen_IRI,
                antigen_table.References,
                assay_count.count
            ORDER BY 
                assay_count.count DESC;"""
    return query_to_database(sql=sql, table='antigen-epitope-joined')

# @router.get('/blast')
# async def run_blast(blast_type:str,sequence:str):
#     return f"Blast: {blast_type}, Sequence: {sequence}"


@router.get('/epitope-antigen-all')
async def get_list_epitope_antigen_all(Epitope_Source_Molecule: str = Query(default="")) -> List[Dict]:
    
    try:
        if len(Epitope_Source_Molecule.strip()) == 0:
            sql = """WITH assay_count AS (
                        SELECT 
                            tcell_data.Epitope_Name,
                            tcell_data.Epitope_Source_Molecule,
                            COUNT(*) AS count
                        FROM tcell_data
                        GROUP BY 
                            tcell_data.Epitope_Name,
                            tcell_data.Epitope_Source_Molecule
                    )
                    SELECT 
                        epitope_table.Epitope_Name,
                        IFNULL(epitope_table.Source_Molecule, '') AS Epitope_Source_Molecule,
                        IFNULL(epitope_table.Epitope_Object_Type, '') AS Epitope_Object_Type,
                        IFNULL(antigen_table.Antigen_IRI, '') AS Antigen_IRI,
                        antigen_table.References,
                        IFNULL(assay_count.count, 0) AS Assay
                    FROM 
                        epitope_table
                    LEFT JOIN 
                        assay_count 
                        ON assay_count.Epitope_Name = epitope_table.Epitope_Name
                        AND assay_count.Epitope_Source_Molecule = epitope_table.Source_Molecule
                    LEFT JOIN
                        antigen_table 
                        ON TRIM(SUBSTRING_INDEX(antigen_table.Antigen_Name, ' (', 1)) = epitope_table.Source_Molecule
                    ORDER BY assay_count.count DESC;"""
            result = query_to_database(sql=sql, table='epitope-antigen-joined')
        else:
            # sql = """
            #         SELECT 
            #             epitope_data.`Epitope_Name`,
            #             epitope_data.Epitope_Source_Molecule,
            #             epitope_data.Epitope_Object_Type,
            #             epitope_data.Antigen_IRI,
            #             epitope_data.`References`,
            #             epitope_data.`Starting_Position`,
            #             epitope_data.`Ending_Position`,
            #             IFNULL(Assay.count, 0) AS Assay
            #         FROM (
            #             SELECT 
            #                 epitope_table.`Epitope_Name`,
            #                 TRIM(SUBSTRING_INDEX(antigen_table.`Antigen_Name`, '(', 1)) AS Epitope_Source_Molecule,
            #                 epitope_table.Epitope_Object_Type,
            #                 antigen_table.Antigen_IRI,
            #                 antigen_table.`References`,
            #                 epitope_table.`Starting_Position`,
            #                 epitope_table.`Ending_Position`
            #             FROM 
            #                 antigen_table
            #             LEFT JOIN 
            #                 epitope_table 
            #                 ON TRIM(SUBSTRING_INDEX(antigen_table.`Antigen_Name`, '(', 1)) = epitope_table.`Source_Molecule`
            #             WHERE 
            #                 TRIM(SUBSTRING_INDEX(antigen_table.`Antigen_Name`, '(', 1)) = %s
            #         ) AS epitope_data
            #         LEFT JOIN (
            #             SELECT 
            #                 Epitope_Name,
            #                 Epitope_Source_Molecule,
            #                 COUNT(*) AS count
            #             FROM tcell_data
            #             GROUP BY Epitope_Name, Epitope_Source_Molecule
            #         ) AS Assay
            #         ON epitope_data.Epitope_Name = Assay.Epitope_Name
            #         AND epitope_data.Epitope_Source_Molecule = Assay.Epitope_Source_Molecule;
            #     """
            sql = """WITH assay_count AS (
                        SELECT 
                            tcell_data.Epitope_Name,
                            tcell_data.Epitope_Source_Molecule,
                            COUNT(*) AS count
                        FROM tcell_data
                        GROUP BY 
                            tcell_data.Epitope_Name,
                            tcell_data.Epitope_Source_Molecule
                    )

                    SELECT 
                        epitope_table.Epitope_Name,
                        epitope_table.Starting_Position,
                        epitope_table.Ending_Position,
                        IFNULL(epitope_table.Source_Molecule, '') AS Epitope_Source_Molecule,
                        IFNULL(epitope_table.Epitope_Object_Type, '') AS Epitope_Object_Type,
                        IFNULL(antigen_table.Antigen_IRI, '') AS Antigen_IRI,
                        antigen_table.References,
                        IFNULL(assay_count.count, 0) AS Assay
                    FROM 
                        epitope_table
                    LEFT JOIN 
                        assay_count 
                        ON assay_count.Epitope_Name = epitope_table.Epitope_Name
                        AND assay_count.Epitope_Source_Molecule = epitope_table.Source_Molecule
                    LEFT JOIN
                        antigen_table 
                        ON TRIM(SUBSTRING_INDEX(antigen_table.Antigen_Name, ' (', 1)) = epitope_table.Source_Molecule
                    WHERE epitope_table.Source_Molecule = %s
                    ORDER BY assay_count.count DESC;
                    """
            print(f"🔍 Searching for source molecule: {Epitope_Source_Molecule}")

            result = query_to_database(sql=sql, table='epitope-antigen-joined', values=(Epitope_Source_Molecule,))
        return result
    except Exception as e:
        print(f"❌ Internal error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/epitope/assays')
async def get_asssays_of_antigen_epitope(Epitope_Name: str , Epitope_Source_Molecule: str):
    
    sql = """SELECT Assay_ID_IEDB_IRI, Reference_PMID, Epitope_Name, Epitope_Source_Molecule,
                    Host_Name, Immunization_Comments, Assay_Method, Assay_Response_measured,
                    Assay_Qualitative_Measurement, MHC_Restriction_Name
             FROM tcell_data
             WHERE Epitope_Name = %s OR Epitope_Source_Molecule = %s"""
    return query_to_database(sql=sql, values=(Epitope_Name,Epitope_Source_Molecule), table="tcell_data")

@router.get('/protein-accession-name-strain')
def get_accession_name_strain(strain: str):
    sql = "SELECT * FROM protein_accession_name_strain"
    if len(strain) == 0:
        return query_to_database(sql=sql, table="protein_accession_name_strain")
    sql += " WHERE strain = %s"
    return query_to_database(sql=sql, values=strain, table="protein_accession_name_strain")


    
#######

@router.post('/strain-genes/')
async def get_items_strain_genes(strainGenes: StrainGenes) -> List[Dict]:
    if strainGenes.strain_id == 'all':
        strainGenes.strain_id = None
        strainGenes.gene_id = None
    sql = f"SELECT * FROM strain_genes WHERE 1=1"
    values = []
    if strainGenes.strain_id:
        sql += " AND strain_id = %s"
        values.append(strainGenes.strain_id)

    if strainGenes.gene_id:
        sql += " AND gene_id = %s"
        values.append(strainGenes.gene_id)

    return query_to_database(sql=sql, table='strain genes', values=tuple(values))

@router.get('/antigen/')
async def get_list_antigens() -> List[Dict]:
    
    sql = "SELECT * FROM antigen"
    return query_to_database(sql=sql, table='antigen')


@router.get('/epitope-sequence/')
async def get_list_epitope_sequence(antigenName: str = Query(...)) -> List[Dict]:
    
    sql = "SELECT * FROM epitope_sequence WHERE `epitope_sequence`.`Antigen_Name` = %s"
    return query_to_database(sql=sql, table="Epitope Sequence", values=antigenName)

@router.get('/antigen-epitope-joined/')
async def read_antigen_epitope_sequence_table(Epitope_Source_Molecule: str):
    
    if len(Epitope_Source_Molecule) == 0:
        sql = """
            SELECT Epitope_Name, Epitope_Source_Molecule, Epitope_Source_Organism,
                   COUNT(Epitope_Name) as 'References', COUNT(Assay_ID_IEDB_IRI) as 'Assay'
            FROM `tcell_data`
            GROUP BY Epitope_Name, Epitope_Source_Molecule, Epitope_Source_Organism;
        """
        result = query_to_database(sql=sql, table="tcell_data")
    else:
        sql = """
            SELECT Epitope_Name, Epitope_Source_Molecule, Epitope_Source_Organism,
                   COUNT(Epitope_Name) AS `References`, COUNT(Assay_ID_IEDB_IRI) AS `Assay`
            FROM `tcell_data`
            WHERE Epitope_Source_Molecule = %s
            GROUP BY Epitope_Name, Epitope_Source_Molecule, Epitope_Source_Organism;
        """
        result = query_to_database(sql=sql, values=Epitope_Source_Molecule, table="tcell_data")
    return result




@router.get("/strain-id", response_model=List[StrainID])
async def get_all_strain_id() -> List[StrainID]:
    
    sql = "SELECT distinct(strain_id) FROM strain_alignment_result"
    return query_to_database(sql=sql, table="Strain ID")

@router.get('/strain-sequence-data', response_model=List[SelectByStrainSequence])
async def get_strain_sequence_data(strain_id: str, sequence_query: str = Query(...)):
    
    sql = """
        SELECT `query`, `match_count`, `mismatches`, `query_start`, `query_end`,
               `target`, `strand`, `target_start`, `target_end`, `block_counts`
        FROM `strain_alignment_result`
        WHERE `strain_id` = %s AND (`sequence` = %s OR `query` = %s);
    """
    return query_to_database(sql=sql, table="Strain Sequence Data", values=(strain_id, sequence_query, sequence_query))

@router.get('/chart-data')
async def get_chart_data_position(strain_id: str, accession: str, start: int, end: int):
    sql = """
        SELECT chart_data.chart_id, chart_types.name, chart_types.color, chart_data.strain_id,
               chart_data.GBID, chart_data.position, chart_data.value
        FROM chart_types
        LEFT JOIN chart_data ON chart_types.chart_id = chart_data.chart_id
        WHERE chart_data.position BETWEEN %s AND %s
          AND chart_data.strain_id = %s
          AND chart_data.GBID = %s
    """
    results = query_to_database(sql=sql, table="Chart Data", values=(start, end, strain_id, accession))
    grouped = defaultdict(list)
    for item in results:
        key = (item['name'], item['color'])
        grouped[key].append({"position": item['position'], "value": item['value']})
    return [{"name": k[0], "color": k[1], "data": v} for k, v in grouped.items()]

@router.get("/chart-location-main")
async def get_chart_location_main(strain_id: str, accession: str, start: int, end: int):
    sql = """
        SELECT * FROM chart_location_main
        WHERE strain_id = %s AND GBID = %s AND start >= %s AND end <= %s
    """
    return query_to_database(sql=sql, table="Chart Location Main", values=(strain_id, accession, start, end))

@router.get('/tree-newick')
def get_tree_newick(name: str):
    sql = "SELECT * FROM newick WHERE name = %s"
    results = query_to_database(sql=sql, table="newick", values=(name))
    return results[0]['tree']

@router.get('/gene-bank-data')
def get_gene_bank_data():
    sql = "SELECT * FROM GenBank_Metadata"
    return query_to_database(sql=sql, table="GenBank_Metadata")

@router.get('/get-antigen-tcell-data')
def get_antigen_tecell_data():
    sql = """
        SELECT Epitope_Source_Molecule AS Antigen_Name, Strain_Name,
               Epitope_Source_Organism AS Organism, COUNT(Epitope_Name) AS Epitopes,
               COUNT(Assay_ID_IEDB_IRI) AS Assays, COUNT(Reference_IEDB_IRI) AS `References`
        FROM tcell_data
        GROUP BY Epitope_Source_Molecule, Epitope_Source_Organism, Strain_Name
    """
    return query_to_database(sql=sql, table='tcell_data')

@router.get('/epitope-sequence-tcell')
async def epitope_sequence_tcell(antigenName: str):
    
    sql = """
        SELECT 
            Epitope_Source_Molecule as Antigen_Name,
            Epitope_Name as Epitopes_Sequence,
            Epitope_Starting_Position as Mapped_Start_Position,
            Epitope_Ending_Position as Mapped_End_Position,
            Assay_Number_of_Subjects_Tested as `Subjects_Tested`,
            `Assay_Response_Frequency_(%%)` as `Response_Freq_95_CI`
        FROM `tcell_data`
        WHERE Epitope_Source_Molecule = %s
    """

    return query_to_database(sql=sql, table="tcell_data", values=antigenName)


