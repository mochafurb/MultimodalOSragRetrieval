"""
scripts/generate_dbms_docs.py
──────────────────────────────
Generates 7 comprehensive, publication-grade Database Management System (DBMS)
reference PDF documents in ./data for the Agentic RAG system.

Topics covered:
  1. Relational Model & SQL Reference
  2. Database Normalization & Schema Design
  3. Storage Architecture, Indexing & File Structures
  4. Transaction Management & Concurrency Control (ACID, 2PL, MVCC)
  5. Query Processing, Relational Algebra & Cost-Based Optimization
  6. Database Recovery Mechanisms, WAL & ARIES Algorithm
  7. Distributed Databases, Consensus & Modern NoSQL Architectures
"""

import os
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    KeepTogether,
    HRFlowable,
)

DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)


def build_pdf(filename: str, title: str, subtitle: str, metadata: dict, sections: list):
    pdf_path = DATA_DIR / filename
    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=letter,
        leftMargin=40,
        rightMargin=40,
        topMargin=40,
        bottomMargin=40,
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#1E293B"),
        spaceAfter=6,
    )
    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#475569"),
        spaceAfter=12,
    )
    h1_style = ParagraphStyle(
        "SectionH1",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#0F172A"),
        spaceBefore=14,
        spaceAfter=6,
    )
    h2_style = ParagraphStyle(
        "SectionH2",
        parent=styles["Heading3"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#1E40AF"),
        spaceBefore=10,
        spaceAfter=4,
    )
    body_style = ParagraphStyle(
        "BodyTextCustom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor("#334155"),
        spaceAfter=6,
    )
    callout_style = ParagraphStyle(
        "CalloutText",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=9,
        leading=12.5,
        textColor=colors.HexColor("#1E293B"),
    )
    table_cell_style = ParagraphStyle(
        "TableCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#1E293B"),
    )
    table_header_style = ParagraphStyle(
        "TableHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11,
        textColor=colors.white,
    )

    story = []

    # Title & Subtitle
    story.append(Paragraph(title, title_style))
    story.append(Paragraph(subtitle, subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#2563EB"), spaceAfter=10))

    # Metadata Card Table
    meta_data = [
        [
            Paragraph(f"<b>Document ID:</b> {metadata.get('doc_id', 'N/A')}", table_cell_style),
            Paragraph(f"<b>Practice / Domain:</b> {metadata.get('practice', 'N/A')}", table_cell_style),
        ],
        [
            Paragraph(f"<b>Standard / System:</b> {metadata.get('system', 'N/A')}", table_cell_style),
            Paragraph(f"<b>Publication Year:</b> {metadata.get('year', '2024')}", table_cell_style),
        ],
    ]
    meta_table = Table(meta_data, colWidths=[260, 272])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F1F5F9")),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 12))

    # Sections
    for sec in sections:
        if "h1" in sec:
            story.append(Paragraph(sec["h1"], h1_style))
        if "h2" in sec:
            story.append(Paragraph(sec["h2"], h2_style))
        if "body" in sec:
            for p in sec["body"]:
                story.append(Paragraph(p, body_style))
        if "callout" in sec:
            callout_data = [[Paragraph(f"<b>Key Takeaway:</b> {sec['callout']}", callout_style)]]
            c_table = Table(callout_data, colWidths=[532])
            c_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#EFF6FF")),
                ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#93C5FD")),
                ('LEFTPADDING', (0, 0), (-1, -1), 10),
                ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            story.append(c_table)
            story.append(Spacer(1, 6))
        if "table" in sec:
            headers = [Paragraph(f"<b>{h}</b>", table_header_style) for h in sec["table"]["headers"]]
            rows = []
            for row in sec["table"]["rows"]:
                rows.append([Paragraph(str(cell), table_cell_style) for cell in row])
            t_data = [headers] + rows
            col_widths = sec["table"].get("widths", [532 // len(headers)] * len(headers))
            content_table = Table(t_data, colWidths=col_widths)
            content_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1E293B")),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ]))
            story.append(content_table)
            story.append(Spacer(1, 8))

    doc.build(story)
    print(f"Generated: {pdf_path.name}")


def generate_all():
    print("Generating comprehensive Database Management System PDFs...")

    # ──────────────────────────────────────────────────────────────────────────
    # 1. Relational Model & SQL Reference
    # ──────────────────────────────────────────────────────────────────────────
    build_pdf(
        filename="01_DBMS_Relational_Model_and_SQL_Reference.pdf",
        title="Database Management Systems: Relational Model & SQL Architecture",
        subtitle="Foundations of Relational Algebra, Integrity Constraints, and Complex SQL Query Execution",
        metadata={
            "doc_id": "DBMS-RM-2024-001",
            "practice": "Relational Model & SQL",
            "system": "ANSI/ISO SQL:2023 & PostgreSQL Core",
            "year": 2024,
        },
        sections=[
            {
                "h1": "1. The Relational Data Model Foundations",
                "body": [
                    "The relational model, formally introduced by Edgar F. Codd in 1970, represents all database state as relations (tables) over mathematical domains. A relation instance r(R) over relation schema R(A1:D1, A2:D2, ..., An:Dn) is a subset of the Cartesian product of the domains D1 × D2 × ... × Dn.",
                    "Each element of a relation is a tuple (row), and each column corresponds to an attribute. A critical principle is the Information Principle: all data, including relationships between records, is represented exclusively by attribute values within relations, avoiding physical pointers.",
                ],
                "callout": "Relations are mathematical sets: duplicate tuples are prohibited by definition, and tuple ordering is undefined.",
            },
            {
                "h1": "2. Relational Integrity Constraints",
                "body": [
                    "Integrity constraints prevent database corruption and preserve semantics across state transitions. Modern relational DBMS engines enforce three foundational tiers of constraints:",
                    "1. <b>Domain Constraints:</b> Restrict attribute values to specified atomic data types, check ranges, and not-null restrictions.",
                    "2. <b>Entity Integrity:</b> No primary key attribute of any base relation may accept a NULL value, guaranteeing that every tuple remains uniquely identifiable.",
                    "3. <b>Referential Integrity:</b> A foreign key in referencing relation R1 must match a candidate key of referenced relation R2, or be completely NULL. Enforced actions include RESTRICT, CASCADE, SET NULL, and SET DEFAULT.",
                ],
                "table": {
                    "headers": ["Constraint Type", "Formal Definition", "Enforcement Engine Mechanism", "Violation Consequence"],
                    "widths": [110, 140, 150, 132],
                    "rows": [
                        ["Entity Integrity", "PK attribute PK(r) != NULL", "Unique index + NOT NULL metadata bit", "Transaction abort: SQLSTATE 23502"],
                        ["Referential Integrity", "FK(r1) in PK(r2) or FK is NULL", "Foreign key trigger / internal index lookup", "Constraint failure: SQLSTATE 23503"],
                        ["Unique Constraint", "Tuple uniqueness over subset U", "B-Tree unique search / duplicate rejection", "Unique violation: SQLSTATE 23505"],
                        ["Check Constraint", "Boolean predicate P(tuple) == TRUE", "Row-level expression validator on write", "Check violation: SQLSTATE 23514"],
                    ],
                },
            },
            {
                "h1": "3. Relational Algebra Operations",
                "body": [
                    "Relational algebra provides the theoretical underpinning for query execution and optimization. Fundamental operations include Selection (sigma), Projection (pi), Cartesian Product (x), Union (cup), Difference (-), and Rename (rho).",
                    "Derived operations include Theta Join, Equi-Join, Natural Join (bowtie), Division (/), and Outer Joins (left, right, full). The algebraic equivalence rules permit the query optimizer to rewrite user SQL queries into computationally minimal physical execution trees.",
                ],
            },
            {
                "h1": "4. Advanced SQL Dialect & Analytic Windows",
                "body": [
                    "Modern enterprise SQL combines standard relational algebra with multi-dimensional grouping, Common Table Expressions (CTEs), and window functions. Window functions perform calculations across a set of table rows related to the current row without collapsing the result set into an aggregation.",
                    "Common analytic window functions include ROW_NUMBER(), RANK(), DENSE_RANK(), NTILE(n), LAG(), LEAD(), and moving window aggregations using ROWS BETWEEN n PRECEDING AND CURRENT ROW.",
                ],
                "table": {
                    "headers": ["Window Function", "Partitioning Clause", "Ordering Requirement", "Primary Use Case"],
                    "widths": [110, 130, 140, 152],
                    "rows": [
                        ["ROW_NUMBER()", "PARTITION BY dept_id", "ORDER BY salary DESC", "Pagination, exact deduplication"],
                        ["DENSE_RANK()", "PARTITION BY dept_id", "ORDER BY score DESC", "Tied competition rank without gaps"],
                        ["LAG(offset, def)", "PARTITION BY account_id", "ORDER BY txn_time ASC", "Delta calculation from prior transaction"],
                        ["SUM() OVER()", "PARTITION BY user_id", "ORDER BY date ROWS UNBOUNDED", "Cumulative running financial total"],
                    ],
                },
            },
        ],
    )

    # ──────────────────────────────────────────────────────────────────────────
    # 2. Database Normalization & Schema Design
    # ──────────────────────────────────────────────────────────────────────────
    build_pdf(
        filename="02_DBMS_Normalization_and_Schema_Design.pdf",
        title="Database Schema Design: Functional Dependencies & Normalization",
        subtitle="Formal Theory of Lossless Decomposition, Dependency Preservation, and Normal Forms 1NF through 5NF",
        metadata={
            "doc_id": "DBMS-NORM-2024-002",
            "practice": "Schema Design & Normalization",
            "system": "Relational Database Theory & Architecture",
            "year": 2024,
        },
        sections=[
            {
                "h1": "1. Schema Design Anomalies & Functional Dependencies",
                "body": [
                    "Unnormalized schemas suffer from severe design anomalies that degrade performance and risk data corruption:",
                    "• <b>Update Anomaly:</b> Redundant data must be updated across multiple rows; failure to update all occurrences results in inconsistent state.",
                    "• <b>Insertion Anomaly:</b> Independent facts cannot be recorded without fabricating artificial parent records (e.g. cannot add a course without an enrolled student).",
                    "• <b>Deletion Anomaly:</b> Removing one entity inadvertently deletes unrelated information (e.g. deleting the last student enrolled in a department deletes the department record).",
                    "A Functional Dependency (FD) X -> Y asserts that whenever two tuples agree on attributes X, they must also agree on attributes Y.",
                ],
                "callout": "Armstrong's Axioms (Reflexivity, Augmentation, Transitivity) form a sound and complete inference system for computing the attribute closure X+ and canonical covers.",
            },
            {
                "h1": "2. Hierarchy of Normal Forms",
                "body": [
                    "Normalization progressively eliminates redundancies by decomposing relation schemas into narrower, focused relations that satisfy higher structural criteria.",
                ],
                "table": {
                    "headers": ["Normal Form", "Structural Requirement", "Primary Anomaly Eliminated", "Decomposition Guarantee"],
                    "widths": [90, 180, 150, 112],
                    "rows": [
                        ["1NF (First)", "All attribute values must be atomic; no repeating groups or arrays", "Nested relations, multi-attribute parsing", "Lossless-join decomposition"],
                        ["2NF (Second)", "In 1NF, and no non-prime attribute is partially dependent on any candidate key", "Partial key dependency anomalies", "Lossless-join decomposition"],
                        ["3NF (Third)", "In 2NF, and no non-prime attribute is transitively dependent on a candidate key", "Transitive dependency redundancy", "Lossless + Dependency Preserving"],
                        ["BCNF (Boyce-Codd)", "For every non-trivial FD X -> Y, X must be a superkey", "Overlapping candidate key redundancies", "Lossless-join (dep. may be lost)"],
                        ["4NF (Fourth)", "In BCNF, and relation has no non-trivial multi-valued dependencies X ->> Y", "Independent multi-attribute cartesian explosion", "Lossless-join decomposition"],
                    ],
                },
            },
            {
                "h1": "3. Lossless-Join Decomposition & Dependency Preservation",
                "body": [
                    "A decomposition of schema R into R1 and R2 is <b>Lossless-Join</b> if and only if the natural join of R1 and R2 recovers the exact original instance without spurious tuples. Formally, R1 cap R2 must functionally determine either R1 or R2 (i.e. (R1 cap R2) -> R1 or (R1 cap R2) -> R2).",
                    "A decomposition is <b>Dependency-Preserving</b> if the union of functional dependencies enforceable locally within R1 and R2 logically implies all original dependencies F. 3NF guarantees both lossless join and dependency preservation, whereas BCNF guarantees lossless join but may not preserve dependencies.",
                ],
            },
            {
                "h1": "4. Practical Industry Denormalization Trade-offs",
                "body": [
                    "While 3NF/BCNF is optimal for Online Transaction Processing (OLTP) to minimize write amplification and lock contention, Online Analytical Processing (OLAP) schemas deliberately introduce denormalization (Star Schema, Snowflake Schema) to eliminate multi-table joins during complex aggregations.",
                ],
                "table": {
                    "headers": ["Architecture Paradigm", "Target Normal Form", "Read Performance", "Write Amplification", "Typical Workload"],
                    "widths": [110, 110, 105, 105, 102],
                    "rows": [
                        ["OLTP Normalized", "3NF / BCNF", "Moderate (requires joins)", "Minimal (single row write)", "Banking, E-commerce transactions"],
                        ["Star Schema (OLAP)", "Denormalized Fact/Dim", "Ultra-fast aggregation", "High (batch ETL only)", "Enterprise Data Warehouses"],
                        ["Document NoSQL", "Embedded / Denormalized", "Instant single-key read", "High on shared entity updates", "Mobile feeds, user profiles"],
                    ],
                },
            },
        ],
    )

    # ──────────────────────────────────────────────────────────────────────────
    # 3. Storage, Indexing & File Structures
    # ──────────────────────────────────────────────────────────────────────────
    build_pdf(
        filename="03_DBMS_Storage_Indexing_and_File_Structures.pdf",
        title="DBMS Storage Engine Architecture: Physical Layout & Index Structures",
        subtitle="Slotted Pages, Buffer Management, B+ Tree Indexes, Hash Tables, and Log-Structured Merge (LSM) Trees",
        metadata={
            "doc_id": "DBMS-STORE-2024-003",
            "practice": "Storage & Indexing",
            "system": "PostgreSQL Page Layout, InnoDB & RocksDB",
            "year": 2024,
        },
        sections=[
            {
                "h1": "1. Physical Page Organization & Slotted Page Architecture",
                "body": [
                    "Database storage engines divide physical storage into fixed-size blocks termed pages (typically 8 KB in PostgreSQL, 16 KB in MySQL InnoDB). Within a page, the industry-standard layout is the <b>Slotted Page Architecture</b>.",
                    "A page header contains page metadata and an array of slot pointers growing from the top downward. Tuple records are written from the bottom of the page upward. A slot pointer stores the exact byte offset and length of each tuple. This decoupling allows tuples to be rearranged, updated, or compacted within the page without invalidating external Record Identifiers (Tuple IDs: Block Number + Slot Offset).",
                ],
                "callout": "Tuple ID (TID / RID) = (Page Number, Slot Index). Foreign keys and non-clustered indexes point to this slot, enabling internal page defragmentation with zero index modifications.",
            },
            {
                "h1": "2. Buffer Pool Management & Eviction Policies",
                "body": [
                    "The Buffer Pool is the dedicated in-memory region caching disk pages. A Buffer Frame Table maps physical disk page IDs to memory addresses and tracks the page's dirty status and pin count (concurrency latch).",
                    "Eviction policies decide which clean or flushed page to evict when all buffer frames are occupied:",
                    "• <b>LRU (Least Recently Used):</b> Evicts pages with oldest access timestamp. Susceptible to sequential scan pollution.",
                    "• <b>Clock Algorithm (Second Chance):</b> Approximates LRU with a circular buffer and single-bit usage flags, achieving O(1) eviction overhead.",
                    "• <b>2Q and ARC (Adaptive Replacement Cache):</b> Maintains separate FIFO and frequency queues, dynamically tuning between recency and frequency.",
                ],
                "table": {
                    "headers": ["Eviction Algorithm", "Scan Resistance", "Time Complexity", "Memory Overhead", "Implementation Engine"],
                    "widths": [115, 110, 100, 105, 102],
                    "rows": [
                        ["LRU Classic", "Poor (vulnerable to scans)", "O(1) with doubly-linked list", "High (pointer churn)", "Standard academic engines"],
                        ["Clock / Second Chance", "Moderate", "O(1) amortized circular sweep", "Minimal (1 bit per frame)", "PostgreSQL Buffer Manager"],
                        ["LRU-K / 2Q", "High (tracks Kth reference)", "O(log N)", "Moderate (multi-queue state)", "High-performance enterprise DBs"],
                        ["InnoDB Buffer Pool", "High (3/8 split midpoint)", "O(1) list splice", "Low (two-tier sublist)", "MySQL InnoDB Storage Engine"],
                    ],
                },
            },
            {
                "h1": "3. B+ Tree Index Architecture",
                "body": [
                    "B+ Trees are self-balancing search trees specifically optimized for block storage systems with high fanout (typically 100 to 500 children per node). All user data pointers or row tuples reside exclusively in leaf nodes. Internal nodes contain strictly search keys and child page pointers.",
                    "Leaf nodes are doubly linked sequentially, providing O(log_B N) point lookup time and O(log_B N + K) range scan performance, where B is the page fanout.",
                ],
                "table": {
                    "headers": ["Index Property", "B+ Tree", "Hash Index", "LSM Tree (Log-Structured)", "Full Table Scan"],
                    "widths": [110, 105, 105, 110, 102],
                    "rows": [
                        ["Point Query Cost", "O(log_B N) (3-4 I/Os)", "O(1) average", "O(log N) (with Bloom filter: 1-2)", "O(N) (all pages read)"],
                        ["Range Query Cost", "O(log_B N + K) (fast)", "Not supported / O(N)", "O(log N + K) (multi-SSTable merge)", "O(N)"],
                        ["Write Cost", "In-place page update / split", "Bucket lock / chained overflow", "Sequential append to WAL + MemTable", "O(1) append to heap"],
                        ["Storage Overhead", "Moderate (fill factor 67-100%)", "Low (hash table array)", "Low (compressed SSTables)", "Zero overhead"],
                    ],
                },
            },
            {
                "h1": "4. Log-Structured Merge (LSM) Trees",
                "body": [
                    "For write-intensive workloads (e.g. time-series, log ingestion, distributed key-value stores), LSM Trees convert random disk writes into sequential disk writes. Incoming writes append to an in-memory sorted MemTable and Write-Ahead Log. When the MemTable reaches its threshold, it is flushed sequentially to Level 0 SSTables (Sorted String Tables).",
                    "Background compaction merges and sorts SSTables into deeper levels, removing deleted keys (tombstones) and older versions. Bloom filters are stored per SSTable to avoid searching files that do not contain the requested key.",
                ],
            },
        ],
    )

    # ──────────────────────────────────────────────────────────────────────────
    # 4. Transaction Management & Concurrency Control
    # ──────────────────────────────────────────────────────────────────────────
    build_pdf(
        filename="04_DBMS_Transaction_Management_and_Concurrency_Control.pdf",
        title="DBMS Transaction Processing: ACID Properties & Concurrency Control",
        subtitle="Conflict Serializability, Two-Phase Locking (2PL), Deadlock Handling, and Multi-Version Concurrency Control (MVCC)",
        metadata={
            "doc_id": "DBMS-TX-2024-004",
            "practice": "Transactions & Concurrency",
            "system": "ACID Engine & Isolation Protocols",
            "year": 2024,
        },
        sections=[
            {
                "h1": "1. Transaction Concept & ACID Guarantees",
                "body": [
                    "A transaction is an atomic unit of database program execution consisting of one or more read/write operations. The database engine guarantees the ACID contract:",
                    "• <b>Atomicity:</b> All operations complete successfully, or all changes are rolled back completely. Maintained via Undo Logging / WAL.",
                    "• <b>Consistency:</b> Execution transforms the database from one valid state to another, satisfying all declared schema constraints and invariants.",
                    "• <b>Isolation:</b> Concurrent transactions execute without mutual interference, as if running in a serialized sequence. Maintained by Concurrency Control (Locking / MVCC).",
                    "• <b>Durability:</b> Committed transactions survive crashes, power cuts, and system failures permanently. Maintained via Redo Logging / Non-volatile storage.",
                ],
            },
            {
                "h1": "2. ANSI SQL Isolation Levels & Concurrency Anomalies",
                "body": [
                    "Concurrent interleaving of transactions without isolation generates severe data anomalies:",
                    "• <b>Dirty Read (G1):</b> Transaction T2 reads uncommitted modifications made by T1; T1 subsequently aborts.",
                    "• <b>Non-Repeatable Read (G2a):</b> T1 reads a row, T2 updates or deletes that row and commits; T1 re-reads the row and observes differing values.",
                    "• <b>Phantom Read (A3):</b> T1 reads rows satisfying a search predicate; T2 inserts or deletes rows matching that predicate and commits; T1 re-executes the predicate and sees a different set of rows.",
                    "• <b>Write Skew:</b> Under Snapshot Isolation, two transactions read overlapping sets and concurrently update disjoint subsets, violating a global cross-record invariant.",
                ],
                "table": {
                    "headers": ["Isolation Level", "Dirty Read", "Non-Repeatable Read", "Phantom Read", "Write Skew Anomaly"],
                    "widths": [115, 105, 110, 102, 100],
                    "rows": [
                        ["Read Uncommitted", "Permitted", "Permitted", "Permitted", "Permitted"],
                        ["Read Committed", "Prevented", "Permitted", "Permitted", "Permitted"],
                        ["Repeatable Read", "Prevented", "Prevented", "Permitted (ANSI) / Prevented (MVCC)", "Permitted"],
                        ["Snapshot Isolation", "Prevented", "Prevented", "Prevented (predicate snapshot)", "Permitted"],
                        ["Serializable", "Prevented", "Prevented", "Prevented", "Prevented"],
                    ],
                },
            },
            {
                "h1": "3. Two-Phase Locking (2PL) & Deadlock Resolution",
                "body": [
                    "Two-Phase Locking guarantees conflict serializability by constraining lock acquisitions and releases into two monotonic phases:",
                    "1. <b>Growing Phase:</b> A transaction may acquire locks (Shared S or Exclusive X), but cannot release any lock.",
                    "2. <b>Shrinking Phase:</b> A transaction may release locks, but cannot acquire any new lock.",
                    "<b>Strict 2PL (S2PL)</b> holds all exclusive locks until transaction commit/abort, preventing cascading rollbacks. <b>Rigorous 2PL (SS2PL)</b> holds both shared and exclusive locks until commit/abort.",
                    "Deadlocks occur when transactions form a cyclic dependency waiting for locks. Engines handle deadlocks via Wait-For Graphs (cycle detection running periodically) or Deadlock Prevention schemes: Wait-Die (non-preemptive based on transaction age) vs Wound-Wait (preemptive).",
                ],
                "table": {
                    "headers": ["Locking Protocol", "Serializability", "Prevents Cascading Aborts", "Deadlock Free", "Concurrency Throughput"],
                    "widths": [120, 105, 115, 92, 100],
                    "rows": [
                        ["Basic 2PL", "Guaranteed", "No (cascades possible)", "No", "High"],
                        ["Strict 2PL (S2PL)", "Guaranteed", "Yes (holds X locks to commit)", "No", "Moderate"],
                        ["Rigorous 2PL (SS2PL)", "Guaranteed", "Yes (holds S + X locks)", "No", "Lower"],
                        ["Wait-Die (Timestamps)", "Guaranteed", "Yes", "Yes (no deadlocks)", "High abort rate on young txns"],
                        ["Wound-Wait", "Guaranteed", "Yes", "Yes (no deadlocks)", "Lower abort rate than Wait-Die"],
                    ],
                },
            },
            {
                "h1": "4. Multi-Version Concurrency Control (MVCC)",
                "body": [
                    "MVCC allows readers to never block writers, and writers to never block readers. When a transaction updates a row, the engine creates a new version of the row tagged with transaction creation identifiers (xmin) and expiration identifiers (xmax).",
                    "A transaction reads the version of each row that was committed prior to its snapshot timestamp. In PostgreSQL, old versions are stored directly in data heap pages and purged by the background VACUUM worker. In MySQL InnoDB, old versions are stored in the UNDO log segment and reconstructed on the fly.",
                ],
            },
        ],
    )

    # ──────────────────────────────────────────────────────────────────────────
    # 5. Query Processing & Cost-Based Optimization
    # ──────────────────────────────────────────────────────────────────────────
    build_pdf(
        filename="05_DBMS_Query_Processing_and_Cost_Based_Optimization.pdf",
        title="DBMS Query Processing: Relational Algebra & Cost-Based Optimization",
        subtitle="Compilation Pipeline, Algebraic Equivalence Rules, Cardinality Estimation, and Join Algorithm Evaluation",
        metadata={
            "doc_id": "DBMS-OPT-2024-005",
            "practice": "Query Optimization & Execution",
            "system": "Cost-Based Query Optimizer Architecture",
            "year": 2024,
        },
        sections=[
            {
                "h1": "1. Query Processing Compilation Pipeline",
                "body": [
                    "A declarative SQL query undergoes four discrete stages before execution:",
                    "1. <b>Parser:</b> Validates SQL syntax against lexical grammar and constructs an Abstract Syntax Tree (AST).",
                    "2. <b>Catalog Binder / Rewriter:</b> Resolves table and column identifiers against database system catalogs, checks permissions, expands views, unnests subqueries, and transforms expressions using relational algebra equivalence rules.",
                    "3. <b>Cost-Based Optimizer (CBO):</b> Explores equivalent physical execution plans (join orders, access paths, join algorithms) and selects the plan with minimum estimated cost based on table statistics.",
                    "4. <b>Executor:</b> Interprets the physical plan using the Volcano Iterator model (open, next, close) or vectorized execution engines.",
                ],
            },
            {
                "h1": "2. Relational Algebra Equivalence Transformations",
                "body": [
                    "Heuristic query rewrite applies deterministic algebraic equivalence rules to shrink intermediate relation cardinality prior to join evaluation:",
                    "• <b>Predicate Pushdown:</b> Pushes selections as deep into the plan tree as possible: sigma_{A=5}(R bowtie S) equiv (sigma_{A=5}(R)) bowtie S.",
                    "• <b>Projection Pushdown:</b> Discards attributes not required by parent operators to reduce memory tuple size: pi_{R.A, S.B}(R bowtie S).",
                    "• <b>Join Associativity & Commutativity:</b> (R bowtie S) bowtie T equiv R bowtie (S bowtie T). Join reordering over N relations explores O((2N-2)! / (N-1)!) permutations, typically solved via System R dynamic programming or genetic algorithms.",
                ],
            },
            {
                "h1": "3. Physical Join Algorithms & I/O Cost Analysis",
                "body": [
                    "The query optimizer selects among three primary join algorithms based on relation cardinalities, available memory buffers B, and existing index structures.",
                ],
                "table": {
                    "headers": ["Join Algorithm", "Disk I/O Cost (Pages)", "Memory Requirement", "Sort / Index Required", "Best Workload Scenario"],
                    "widths": [115, 125, 95, 95, 102],
                    "rows": [
                        ["Block Nested Loop (BNLJ)", "M + (M / (B - 2)) * N", "B pages (at least 3)", "None required", "Small relations without indexes"],
                        ["Index Nested Loop (INLJ)", "M + (Records_M * C_index)", "Minimal (1-2 pages)", "Index on inner table S", "Outer table small, selective inner index"],
                        ["Sort-Merge Join (SMJ)", "3(M + N) (with 2-pass sort)", "sqrt(max(M, N)) pages", "Both inputs sorted on join key", "Medium-large tables, output needs sorting"],
                        ["Grace Hash Join", "3(M + N) (partition + probe)", "sqrt(min(M, N)) pages", "None (builds in-memory hash)", "Large equi-joins where neither fits in RAM"],
                    ],
                },
            },
            {
                "h1": "4. Cardinality Estimation & System Catalogs",
                "body": [
                    "Cost calculations depend entirely on Cardinality Estimation: predicting the number of output tuples for an operator. The database catalog maintains statistical summaries collected via ANALYZE:",
                    "• <b>Equi-Width vs Equi-Depth Histograms:</b> Equi-depth histograms maintain buckets with equal numbers of rows, providing bounded error for skewed attribute distributions.",
                    "• <b>Selectivity Factor (s):</b> For equality predicate A = c, selectivity s = 1 / DistinctValues(A). For range predicate A >= c, selectivity is interpolated across histogram buckets.",
                    "• <b>Attribute Value Independence (AVI) Assumption:</b> Optimizers multiply individual selectivities: s(A and B) = s(A) * s(B). Violations caused by correlated attributes (e.g. City and ZipCode) cause catastrophic plan regressions, mitigated by multi-column statistics (Extended Statistics in PostgreSQL).",
                ],
            },
        ],
    )

    # ──────────────────────────────────────────────────────────────────────────
    # 6. Database Recovery Mechanisms & Logging
    # ──────────────────────────────────────────────────────────────────────────
    build_pdf(
        filename="06_DBMS_Database_Recovery_and_Logging_Mechanisms.pdf",
        title="DBMS Failure Recovery: Write-Ahead Logging & The ARIES Framework",
        subtitle="Buffer Management Steal/Force Policies, Checkpoint Strategies, and The Three-Phase ARIES Recovery Algorithm",
        metadata={
            "doc_id": "DBMS-REC-2024-006",
            "practice": "Database Recovery & Logging",
            "system": "Storage Reliability & Crash Recovery Subsystem",
            "year": 2024,
        },
        sections=[
            {
                "h1": "1. Failure Classification & Buffer Pool Policies",
                "body": [
                    "Database recovery systems must restore consistent database state across three failure classifications: Transaction Failures (internal abort, deadlock), System Crashes (power failure, OS panic), and Media Failures (disk corruption).",
                    "The recovery architecture is dictated by buffer pool flush policies:",
                    "• <b>STEAL Policy:</b> The buffer manager is allowed to flush dirty pages belonging to uncommitted transactions to disk to free buffer frames. Requires an UNDO logging mechanism to reverse changes if the transaction aborts.",
                    "• <b>NO-STEAL Policy:</b> Uncommitted pages cannot be written to disk. Eliminates the need for UNDO, but restricts buffer memory capacity.",
                    "• <b>FORCE Policy:</b> All pages modified by a transaction must be flushed to disk before the commit returns. Eliminates the need for REDO, but generates severe random I/O bottlenecks.",
                    "• <b>NO-FORCE Policy:</b> A transaction commits as soon as its log records are flushed to non-volatile storage, without forcing data pages to disk. Requires REDO logging on crash recovery.",
                ],
                "callout": "Every high-performance commercial and open-source DBMS (PostgreSQL, MySQL InnoDB, Oracle, SQL Server) implements STEAL / NO-FORCE.",
            },
            {
                "h1": "2. Write-Ahead Logging (WAL) Protocol",
                "body": [
                    "The Write-Ahead Logging protocol enforces two mandatory invariants:",
                    "1. <b>Write-Ahead Invariant:</b> The log record describing an update must be flushed to non-volatile disk before the corresponding dirty data page is written to disk (ensures Atomicity under STEAL).",
                    "2. <b>Commit Invariant:</b> All log records for a transaction (including the COMMIT record) must be flushed to disk before the transaction commit is acknowledged to the client (ensures Durability under NO-FORCE).",
                    "Each log record is identified by a monotonically increasing Log Sequence Number (LSN). Each data page maintains a pageLSN recording the LSN of the latest update applied to that page.",
                ],
                "table": {
                    "headers": ["Log Record Field", "Data Type", "Architectural Purpose in WAL", "Usage in Recovery"],
                    "widths": [115, 95, 160, 162],
                    "rows": [
                        ["LSN", "Integer (8-byte)", "Unique monotonic sequence identifier", "Ordering and idempotency check"],
                        ["PrevLSN", "Integer (8-byte)", "Pointer to previous log record of same txn", "Enables backward scan during UNDO"],
                        ["TxnID", "Integer", "Transaction identifier performing update", "Tracks active loser transactions"],
                        ["Type", "Enum", "UPDATE, COMMIT, ABORT, CLR, CHECKPOINT", "Directs state machine transitions"],
                        ["PageID", "Integer (block#)", "Identifies modified physical database page", "Directs REDO to exact physical block"],
                        ["Redo / Undo Data", "Byte payload", "Physical or physiological diff values", "Reconstructs page / reverses mutations"],
                    ],
                },
            },
            {
                "h1": "3. The ARIES Recovery Algorithm",
                "body": [
                    "ARIES (Algorithms for Recovery and Isolation Exploiting Semantics), developed by C. Mohan at IBM, is the foundation of modern database crash recovery. Upon reboot after a system crash, ARIES executes three sequential phases:",
                    "• <b>Phase 1: Analysis Phase:</b> Scans the log forward from the most recent checkpoint. Reconstructs the internal state at crash time: the Transaction Table (identifies active 'loser' transactions) and the Dirty Page Table (identifies unwritten pages and smallest recLSN).",
                    "• <b>Phase 2: Redo Phase:</b> 'Repeats history' by scanning forward from the smallest recLSN found in the Dirty Page Table to the end of the log. Reapplies all logged actions (both committed and uncommitted transactions). If pageLSN on disk >= log record LSN, the update is skipped (idempotency).",
                    "• <b>Phase 3: Undo Phase:</b> Scans the log backward from the end, rolling back all active loser transactions identified in Analysis. For each undone update, it writes a Compensation Log Record (CLR) to ensure that recovery itself can survive repeated crashes without looping.",
                ],
                "table": {
                    "headers": ["ARIES Phase", "Scan Direction", "Starting Point", "Ending Point", "Core State Output"],
                    "widths": [100, 95, 115, 110, 112],
                    "rows": [
                        ["1. Analysis", "Forward (->)", "Checkpoint record", "End of log", "Active Txn Table & Dirty Page Table"],
                        ["2. Redo", "Forward (->)", "Minimum recLSN", "End of log", "Restores pre-crash state (history repeated)"],
                        ["3. Undo", "Backward (<-)", "End of log", "Oldest uncommitted update", "Reverses loser transactions + writes CLRs"],
                    ],
                },
            },
        ],
    )

    # ──────────────────────────────────────────────────────────────────────────
    # 7. Distributed Databases & Modern Architectures
    # ──────────────────────────────────────────────────────────────────────────
    build_pdf(
        filename="07_DBMS_Distributed_Databases_and_Modern_Architectures.pdf",
        title="Distributed Database Systems: Consensus, Replication & NoSQL Architectures",
        subtitle="CAP/PACELC Theorems, Two-Phase Commit (2PC), Quorum Consensus, Raft Protocol, and Distributed SQL Engines",
        metadata={
            "doc_id": "DBMS-DIST-2024-007",
            "practice": "Distributed Databases & NoSQL",
            "system": "Distributed Cloud Systems & Spanner Architecture",
            "year": 2024,
        },
        sections=[
            {
                "h1": "1. Distributed Data Foundations & Theoretical Limits",
                "body": [
                    "Distributed database architectures partition and replicate data across independent networked nodes to achieve horizontal scalability, fault tolerance, and low latency across geographies.",
                    "Two foundational theorems define the theoretical boundaries of distributed data systems:",
                    "• <b>CAP Theorem (Eric Brewer):</b> Under network partition (P), a distributed system must choose between Consistency (C - linearizability, every read receives the most recent write) and Availability (A - every non-failing node returns a non-error response).",
                    "• <b>PACELC Theorem (Daniel Abadi):</b> If there is a Partition (P), how does the system trade Availability (A) and Consistency (C); Else (E), when the system is running normally, how does it trade Latency (L) and Consistency (C)? E.g., Dynamo is PA/EL; Spanner and CockroachDB are PC/EC.",
                ],
            },
            {
                "h1": "2. Distributed Replication Strategies & Quorum Math",
                "body": [
                    "Data replication distributes redundant copies of records across multiple nodes:",
                    "• <b>Single-Leader (Primary-Replica):</b> All writes route to a designated leader, which streams replication logs to follower replicas. Replicas serve read-only queries. Asynchronous replication provides minimal write latency but risks replication lag and data loss on failover.",
                    "• <b>Multi-Leader:</b> Multiple nodes accept writes concurrently. Requires conflict resolution strategies (Last-Write-Wins, CRDTs - Conflict-free Replicated Data Types).",
                    "• <b>Leaderless (Dynamo-Style):</b> Clients write to and read from multiple replicas concurrently. Strict consistency requires the Quorum Condition: R + W > N, where N is the total replication factor, W is write quorum, and R is read quorum. This guarantees that the read set and write set overlap on at least one replica holding the latest version.",
                ],
                "table": {
                    "headers": ["Replication Model", "Write Scalability", "Read Scalability", "Consistency Guarantee", "Conflict Handling"],
                    "widths": [115, 105, 105, 105, 102],
                    "rows": [
                        ["Single-Leader (Sync)", "Single node bound", "High (read replicas)", "Strong (immediate)", "None required (serialized by leader)"],
                        ["Single-Leader (Async)", "Single node bound", "Ultra-high", "Eventual (replication lag)", "Replication stream / failover failover"],
                        ["Leaderless Quorum", "High (any node writes)", "High", "Tunable (Strong if R+W>N)", "Read repair, hinted handoff, Merkle trees"],
                        ["Multi-Leader Multi-Region", "Very high", "Very high", "Eventual / Causal", "CRDTs, LWW timestamps"],
                    ],
                },
            },
            {
                "h1": "3. Two-Phase Commit (2PC) & Consensus Protocols",
                "body": [
                    "Atomic commitment across distributed partitions requires the <b>Two-Phase Commit (2PC)</b> protocol:",
                    "1. <b>Prepare Phase:</b> The coordinator node sends a PREPARE query to all cohort participants. Cohorts write intent and undo/redo data to local WAL and reply YES (ready) or NO (abort).",
                    "2. <b>Commit Phase:</b> If all cohorts vote YES, coordinator writes COMMIT to its log and sends GLOBAL COMMIT to all cohorts. If any cohort votes NO or times out, coordinator sends GLOBAL ABORT.",
                    "A critical limitation of 2PC is that it is a <b>blocking protocol</b>: if the coordinator crashes during the commit phase after cohorts vote YES, cohorts remain blocked holding locks indefinitely.",
                    "Modern Distributed SQL engines replace fragile 2PC coordinators with fault-tolerant replicated state machines governed by consensus algorithms like <b>Raft</b> or <b>Multi-Paxos</b>, tolerating (N-1)/2 node failures.",
                ],
            },
            {
                "h1": "4. Modern NoSQL & Distributed SQL (NewSQL) Landscape",
                "body": [
                    "Modern database architectures specialize along distinct data models and consistency semantics:",
                ],
                "table": {
                    "headers": ["System Category", "Data Model", "Concurrency / Consistency", "Representative Engines", "Target Workload"],
                    "widths": [105, 105, 115, 105, 102],
                    "rows": [
                        ["Relational (RDBMS)", "Tables, Foreign Keys", "ACID / Strict Serializability", "PostgreSQL, MySQL, Oracle", "Transactional business records, billing"],
                        ["Key-Value Store", "Arbitrary byte blobs", "Eventual or Single-Key Strong", "Redis, AWS DynamoDB", "Caching, sessions, high-speed lookup"],
                        ["Document Store", "JSON / BSON Hierarchies", "Single-Document ACID", "MongoDB, Couchbase", "Content management, rapid prototyping"],
                        ["Wide-Column Store", "Sparse multidimensional", "Tunable Quorum / Eventual", "Apache Cassandra, ScyllaDB", "High-throughput telemetry, metrics, IoT"],
                        ["Distributed SQL", "Relational Schema + SQL", "Distributed ACID / Multi-Raft", "Google Spanner, CockroachDB", "Global financial transactions, high scale"],
                    ],
                },
            },
        ],
    )

    print("All 7 Database Management System reference PDFs generated successfully!")


if __name__ == "__main__":
    generate_all()
