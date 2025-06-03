import uvicorn
from fastapi import FastAPI, HTTPException,APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from collections import defaultdict
import pymysql

import mysql.connector
from mysql.connector import Error



# app = FastAPI()
router = APIRouter()

# เปิด CORS สำหรับ localhost:3000 (frontend)
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:3000"],  # เปลี่ยนเป็น URL frontend ที่ใช้จริงได้
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )




def get_db_connection():
    # return pymysql.connect(
    #     host= "localhost",
    #     user="test",
    #     password="1234",
    #     port=3307,
    #     database="mydatabase",
    #     cursorclass=pymysql.cursors.DictCursor
    # )
    try:
        return mysql.connector.connect(
            host='localhost',
            port=3306,
            database='web_tbrc',
            user='test',
            password='1234'   
        )

    except Error as e:
        print("Error while connecting to MySQL:", e)
        return None

@router.get("/protein_web/basic/{protein_code}")
def get_protein_basic(protein_code: str):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM protein_tb WHERE protein_code = %s", (protein_code,))
        protein_info = cursor.fetchone()
        if not protein_info:
            raise HTTPException(status_code=404, detail="Protein not found")

        cursor.execute("SELECT * FROM sq_tb WHERE protein_code = %s", (protein_code,))
        sequence = cursor.fetchone()

        cursor.execute("""
            SELECT k.keyword, k.category
            FROM protein_keywords pk
            JOIN keywords k ON pk.keyword_id = k.id
            WHERE pk.protein_code = %s
        """, (protein_code,))
        raw_keywords = cursor.fetchall()
        keywords = defaultdict(list)
        for row in raw_keywords:
            keywords[row["category"].strip()].append(row["keyword"].strip())

        return {
            "protein_code": protein_code,
            "info": protein_info,
            "sequence": sequence,
            "keyword": dict(keywords),
        }
    finally:
        cursor.close()
        conn.close()

@router.get("/protein_web/structure/{protein_code}")
def get_protein_structure(protein_code: str):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM protein3d WHERE protein_code = %s", (protein_code,))
        structure = cursor.fetchone()
        if not structure:
            raise HTTPException(status_code=404, detail="Structure not found")
        return structure
    finally:
        cursor.close()
        conn.close()

@router.get("/protein_web/go_terms/{protein_code}")
def get_go_terms(protein_code: str):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM go_term WHERE protein_code = %s", (protein_code,))
        go_terms = cursor.fetchall()

        cursor.execute("""
            SELECT id, protein_code, aspect, term, source, evidence
            FROM go_term
            WHERE protein_code = %s AND aspect = 'Cellular Component'
        """, (protein_code,))
        go_cc = cursor.fetchall()

        return {
            "GO_terms": go_terms,
            "GO_annotation_cc": go_cc
        }
    finally:
        cursor.close()
        conn.close()

@router.get("/protein_web/locations/{protein_code}")
def get_locations_publications(protein_code: str):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # ดึงข้อมูล locations ตาม protein_code
        cursor.execute("SELECT * FROM locations WHERE protein_code = %s", (protein_code,))
        locations = cursor.fetchall()
        location_ids = [loc["id"] for loc in locations]

        # ดึง publications ของแต่ละ location_id
        if location_ids:
            format_strings = ','.join(['%s'] * len(location_ids))
            cursor.execute(f"""
                SELECT lp.location_id, pub.*
                FROM location_pub lp
                JOIN publications pub ON lp.publication_id = pub.id
                WHERE lp.location_id IN ({format_strings})
            """, tuple(location_ids))
            pub_rows = cursor.fetchall()
        else:
            pub_rows = []

        # รวม publications ตาม location_id
        location_pub_map = defaultdict(list)
        for row in pub_rows:
            location_pub_map[row["location_id"]].append({
                "title": row["title"],
                "authors": row["authors"],
                "journal": row["journal"],
                "vol_page_year": row["vol_page_year"],
                "pubmed_url": row["pubmed_url"],
                "europe_pmc_url": row["europe_pmc_url"],
                "journal_url": row["journal_url"],
            })

        # จัดรูปแบบข้อมูล locations พร้อม publications
        location_results = []
        for loc in locations:
            location_results.append({
                "location_name": loc["location_name"],
                "evidence_type": loc["evidence_type"],
                "evidence_detail": loc["evidence_detail"],
                "description": loc.get("description"),
                "uniprot_id": loc.get("uniprot_id"),
                "publications": location_pub_map.get(loc["id"], [])
            })

        return {
            "locations": location_results
        }
    finally:
        cursor.close()
        conn.close()


@router.get("/protein_web/epitope/{protein_code}")
def get_epitope(protein_code: str):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM epitope WHERE protein_code = %s", (protein_code,))
        epitope = cursor.fetchall()
        if not epitope:
            raise HTTPException(status_code=404, detail="Epitope data not found")
        return {"Epitope": epitope}
    finally:
        cursor.close()
        conn.close()


@router.get("/protein_web")
def get_all_proteins():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # ดึง protein พร้อม sequence
        cursor.execute("""
            SELECT p.protein_code, p.uniProtkbId, p.protein_name, p.gene, p.organism,
                   s.sequence
            FROM protein_tb p
            LEFT JOIN sq_tb s ON p.protein_code = s.protein_code
        """)
        protein_rows = cursor.fetchall()

        # ดึง keyword ทีเดียว
        cursor.execute("""
            SELECT pk.protein_code, k.keyword, k.category
            FROM protein_keywords pk
            JOIN keywords k ON pk.keyword_id = k.id
        """)
        keyword_rows = cursor.fetchall()

        # สร้าง mapping ของ keyword
        keyword_map = defaultdict(lambda: defaultdict(list))
        for row in keyword_rows:
            keyword_map[row["protein_code"]][row["category"].strip()].append(row["keyword"].strip())

        # รวมผลลัพธ์
        results = []
        for row in protein_rows:
            sequence_str = row.get("sequence") or ""
            seq_len = len(sequence_str.replace(" ", "").replace("\n", ""))

            results.append({
                "protein_code": row["protein_code"],
                "uniProtkbId": row.get("uniProtkbId"),
                "protein_name": row.get("protein_name"),
                "gene": row.get("gene"),
                "organism": row.get("organism"),
                "sequence": {
                    "sequence": sequence_str,
                    "length": seq_len
                },
                "keyword": dict(keyword_map.get(row["protein_code"], {}))
            })

        return results
    finally:
        cursor.close()
        conn.close()


@router.get("/download_fasta/{protein_code}")
def download_fasta(protein_code: str):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT p.protein_code, p.gene, s.sequence
            FROM protein_tb p
            JOIN sq_tb s ON p.protein_code = s.protein_code
            WHERE p.protein_code = %s
        """, (protein_code,))
        row = cursor.fetchone()

        if not row:
            raise HTTPException(status_code=404, detail="Protein not found")

        code = row["protein_code"]
        gene = row.get("gene", "")
        sequence = row["sequence"]

        gene_part = f"gene={gene}" if gene else ""
        fasta_content = f">{code}|{gene_part}\n{sequence}\n"

        return Response(
            content=fasta_content,
            media_type="text/plain",
            headers={"Content-Disposition": f"attachment; filename={code}.fasta"}
        )
    except Exception as e:
        print(f"Error in download_fasta: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()


from fastapi import HTTPException, Response

@router.get("/download_epitopes/{protein_code}")
def download_epitopes(protein_code: str):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)  
    try:
        cursor.execute("""
            SELECT epitope_name, start_pos, end_pos, source_molecule
            FROM epitope
            WHERE protein_code = %s
        """, (protein_code,))
        rows = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

    if not rows:
        raise HTTPException(status_code=404, detail="No epitope data found")

    lines = ["epitope_name\tstart_pos\tend_pos\tsource_molecule"]
    for row in rows:
        lines.append(f"{row['epitope_name']}\t{row['start_pos']}\t{row['end_pos']}\t{row['source_molecule']}")
    content = "\n".join(lines)

    return Response(
        content=content,
        media_type="text/plain",
        headers={"Content-Disposition": f"attachment; filename=epitopes_{protein_code}.txt"}
    )


if __name__ == "__main__":
    uvicorn.run("main:app",host="0.0.0.0" ,port=8000,reload=True)