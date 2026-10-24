"""
scripts/generate_os_docs.py
───────────────────────────
Generates 7 comprehensive, publication-grade Operating Systems (OS)
reference PDF documents in ./data for the OS databse rag retrieval system.

Topics covered:
  1. Processes, Threads & CPU Scheduling (PCB, Context Switching, CFS, MLFQ)
  2. Memory Management, Virtual Memory & Paging (Paging, TLB, Page Faults, LRU/Clock)
  3. Concurrency, Synchronization & Deadlocks (Mutex, Semaphores, Peterson's, Banker's)
  4. Storage, File Systems & Disk I/O (Inodes, VFS, Ext4, Journaling, Disk Scheduling)
  5. Kernel Architecture, System Calls & Security (Monolithic vs Microkernel, Rings, ASLR)
  6. Interprocess Communication & Distributed OS (Pipes, Shared Memory, Sockets, RPC)
  7. Virtualization, Containers & Resource Isolation (Hypervisors, cgroups v2, Namespaces)
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

    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#0F172A"),
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
        fontSize=13.5,
        leading=17,
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
        textColor=colors.HexColor("#1D4ED8"),
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
        leading=13,
        textColor=colors.HexColor("#1E3A8A"),
    )
    meta_style = ParagraphStyle(
        "MetaText",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#64748B"),
    )

    story = []

    # Title & Subtitle
    story.append(Paragraph(title, title_style))
    story.append(Paragraph(subtitle, subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#2563EB"), spaceAfter=8))

    # Metadata Bar
    meta_items = [f"<b>{k.replace('_', ' ').title()}:</b> {v}" for k, v in metadata.items()]
    meta_text = "  |  ".join(meta_items)
    story.append(Paragraph(meta_text, meta_style))
    story.append(Spacer(1, 10))

    # Content Sections
    for sec in sections:
        if "h1" in sec:
            story.append(Paragraph(sec["h1"], h1_style))
        if "h2" in sec:
            story.append(Paragraph(sec["h2"], h2_style))
        if "body" in sec:
            for p in sec["body"]:
                story.append(Paragraph(p, body_style))

        # Tables
        if "table" in sec:
            tbl_data = sec["table"]
            cell_style = ParagraphStyle(
                "TableCell",
                parent=styles["Normal"],
                fontName="Helvetica",
                fontSize=8.5,
                leading=11,
                textColor=colors.HexColor("#1E293B"),
            )
            header_cell_style = ParagraphStyle(
                "HeaderCell",
                parent=styles["Normal"],
                fontName="Helvetica-Bold",
                fontSize=8.5,
                leading=11,
                textColor=colors.HexColor("#FFFFFF"),
            )

            hdr = [Paragraph(str(h), header_cell_style) for h in tbl_data["headers"]]
            rows = [[Paragraph(str(c), cell_style) for c in row] for row in tbl_data["rows"]]
            all_rows = [hdr] + rows

            col_widths = tbl_data.get("widths", [532 // len(tbl_data["headers"])] * len(tbl_data["headers"]))
            t = Table(all_rows, colWidths=col_widths, repeatRows=1)
            t.setStyle(
                TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E293B")),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#FFFFFF"), colors.HexColor("#F8FAFC")]),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                ])
            )
            story.append(Spacer(1, 4))
            story.append(KeepTogether(t))
            story.append(Spacer(1, 8))

        # Callouts
        if "callout" in sec:
            callout_p = Paragraph(sec["callout"], callout_style)
            box = Table([[callout_p]], colWidths=[532])
            box.setStyle(
                TableStyle([
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#EFF6FF")),
                    ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#3B82F6")),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                    ("LEFTPADDING", (0, 0), (-1, -1), 10),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ])
            )
            story.append(Spacer(1, 4))
            story.append(box)
            story.append(Spacer(1, 8))

    doc.build(story)
    print(f"Created: {filename}")


def generate_all():
    # ──────────────────────────────────────────────────────────────────────────
    # 1. Processes, Threads & CPU Scheduling
    # ──────────────────────────────────────────────────────────────────────────
    build_pdf(
        filename="01_OS_Processes_Threads_and_CPU_Scheduling.pdf",
        title="Operating Systems: Processes, Threads & CPU Scheduling Algorithms",
        subtitle="Process Control Blocks (PCB), Context Switching Mechanics, Completely Fair Scheduler (CFS), and MLFQ",
        metadata={
            "doc_id": "OS-SCHED-2024-001",
            "practice": "CPU Scheduling & Concurrency",
            "system": "Linux CFS, POSIX pthreads, Windows Kernel Executive",
            "year": 2024,
        },
        sections=[
            {
                "h1": "1. Process Lifecycle and Process Control Block (PCB)",
                "body": [
                    "A process is an instance of a program in execution, encapsulating an address space, execution state, and system resources. In modern operating systems, the kernel manages processes through a primary kernel data structure termed the <b>Process Control Block (PCB)</b> (in Linux, <code>struct task_struct</code>).",
                    "The PCB stores all essential state needed to suspend and resume process execution:",
                    "• <b>Process Identifier (PID):</b> Unique integer identifying the process within the namespace.",
                    "• <b>Process State:</b> State transitions among NEW, READY, RUNNING, WAITING (blocked on I/O or event), and TERMINATED (zombie until reaped).",
                    "• <b>Program Counter (PC) & CPU Registers:</b> The instruction address and contents of data/pointer registers (RAX, RSP, RBP, CR3).",
                    "• <b>Memory Management Information:</b> Page table base pointers, segment tables, and virtual memory boundaries.",
                    "• <b>Accounting & Scheduling Information:</b> CPU time consumed, priority (nice value from -20 to +19), virtual runtime (vruntime), and scheduling class.",
                    "• <b>I/O Status & Open File Descriptors:</b> Array of pointers to open file table entries (stdin 0, stdout 1, stderr 2).",
                ],
                "callout": "Context Switch Cost: A hardware context switch saves CPU registers to kernel stack, swaps CR3 (flushing non-global TLB entries unless PCID is supported), and loads new registers, incurring 1.2 to 3.5 microseconds of direct overhead plus subsequent cache cold-miss penalties.",
            },
            {
                "h1": "2. Threads vs. Processes: Architectural Trade-Offs",
                "body": [
                    "A thread is the smallest schedulable execution unit within a process. Multiple threads within the same process share code, global data, open file descriptors, and heap memory, but each thread maintains its own private Thread Control Block (TCB), Program Counter, stack frame, and register state.",
                ],
                "table": {
                    "headers": ["Dimension", "Process (fork)", "Kernel Thread (pthread_create)", "User-Level Green Thread / Coroutine"],
                    "widths": [115, 135, 142, 140],
                    "rows": [
                        ["Address Space", "Isolated (Private MMU mapping)", "Shared with parent process", "Shared within single thread"],
                        ["Creation Latency", "High (copy-on-write page tables)", "Moderate (~10-25 μs)", "Ultra-low (~0.1-0.5 μs)"],
                        ["Context Switch Cost", "1.5 - 3.8 μs (TLB flush / PCID reload)", "0.4 - 1.1 μs (no MMU page table reload)", "0.02 - 0.08 μs (user-space registers only)"],
                        ["Communication (IPC)", "Pipes, Shared Memory, Sockets", "Direct shared memory + mutexes", "Channels or shared objects"],
                        ["OS Schedulability", "Independently scheduled by kernel", "Independently scheduled on cores", "Multiplexed M:N on kernel threads"],
                    ],
                },
            },
            {
                "h1": "3. CPU Scheduling Algorithms: Comparative Evaluation",
                "body": [
                    "CPU scheduling determines which READY process receives the CPU core when the running task yields, blocks on I/O, or exceeds its timeslice quantum.",
                    "Key evaluation metrics include: <b>Turnaround Time</b> (completion minus arrival), <b>Waiting Time</b> (time spent in READY queue), <b>Response Time</b> (first CPU dispatch minus arrival), and <b>Throughput</b> (processes completed per unit time).",
                ],
                "table": {
                    "headers": ["Algorithm", "Preemptive?", "Target Optimization", "Turnaround Time", "Risk / Failure Mode"],
                    "widths": [110, 80, 115, 110, 117],
                    "rows": [
                        ["First-Come First-Served (FCFS)", "No", "Simplicity & FIFO ordering", "High (convoy effect)", "Convoy effect on long CPU burst"],
                        ["Shortest Job First (SJF)", "No", "Minimum average wait time", "Optimal (non-preemptive)", "Starvation of long jobs, burst unpredictable"],
                        ["Shortest Remaining Time First (SRTF)", "Yes", "Minimum turnaround time", "Optimal (preemptive)", "High context switch overhead & starvation"],
                        ["Round Robin (RR)", "Yes", "Interactive response time", "Moderate (depends on quantum)", "Degrades to FCFS if quantum too large"],
                        ["Priority Scheduling", "Both", "Differentiated QoS classes", "Varied by priority rank", "Priority inversion and indefinite starvation"],
                        ["Multilevel Feedback Queue (MLFQ)", "Yes", "Separates I/O vs CPU bound", "Near-optimal dynamic", "Complex tuning of decay and boost intervals"],
                        ["Linux Completely Fair Scheduler (CFS)", "Yes", "Fair CPU time proportion", "Proportional fair share", "Slight scheduling latency jitter for micro-threads"],
                    ],
                },
            },
            {
                "h1": "4. Linux Completely Fair Scheduler (CFS) Mechanics",
                "body": [
                    "The Linux Completely Fair Scheduler (CFS) does not use fixed timeslice quantums. Instead, it maintains a red-black tree indexed by each task's <b>virtual runtime (vruntime)</b>.",
                    "Virtual runtime tracks the normalized amount of CPU time a process has executed:",
                    "• <code>vruntime += delta_exec * (NICE_0_LOAD / task_weight)</code>",
                    "• A task with nice value 0 has weight 1024. A task with nice -5 has weight 3121 (its vruntime advances slower, giving it ~3x more physical CPU time).",
                    "• The kernel always selects the leftmost node in the red-black tree (minimum vruntime) for the next CPU dispatch, ensuring proportional fairness and self-balancing scheduling in O(log N) insertion and O(1) lookup.",
                ],
            },
        ],
    )

    # ──────────────────────────────────────────────────────────────────────────
    # 2. Memory Management, Virtual Memory & Paging
    # ──────────────────────────────────────────────────────────────────────────
    build_pdf(
        filename="02_OS_Memory_Management_and_Virtual_Memory.pdf",
        title="Operating Systems: Memory Management & Virtual Memory Architecture",
        subtitle="Paging, Multi-Level Page Tables, TLB Translation, Page Faults, and Replacement Algorithms",
        metadata={
            "doc_id": "OS-MEM-2024-002",
            "practice": "Memory Management & Virtual Memory",
            "system": "x86-64 MMU, Linux Virtual Memory Subsystem, Page Cache",
            "year": 2024,
        },
        sections=[
            {
                "h1": "1. Virtual Address Translation & Multi-Level Page Tables",
                "body": [
                    "Virtual memory provides each process with the illusion of a contiguous, private address space, decoupling logical addresses from fragmented physical DRAM frames.",
                    "On x86-64 architectures, standard 48-bit virtual addressing is mapped to physical memory via 4-level paging (PML4 -> PDPT -> PD -> PT -> 4KB Physical Page Frame).",
                    "• <b>Paging Overhead:</b> Each translation traversal through all 4 page table levels requires 4 sequential memory reads. To mitigate this latency, hardware incorporates the <b>Translation Lookaside Buffer (TLB)</b>, a fast associative cache.",
                    "• <b>Huge Pages:</b> To reduce TLB miss pressure on memory-intensive workloads, modern OS support 2MB (Level 2) and 1GB (Level 1) Huge Pages.",
                ],
                "table": {
                    "headers": ["Paging Structure", "Page Size", "Virtual Bits Covered", "Table Entries", "TLB Coverage / Entry"],
                    "widths": [115, 95, 115, 95, 112],
                    "rows": [
                        ["Standard Page (4-Level)", "4 KB", "Bits [11:0] offset", "512 entries per level", "4 KB per TLB slot"],
                        ["Transparent Huge Page (THP)", "2 MB", "Bits [20:0] offset", "Bypasses Page Table L1", "2 MB (512x standard coverage)"],
                        ["Gigabyte Huge Page", "1 GB", "Bits [29:0] offset", "Bypasses PD and PT", "1 GB (262,144x standard coverage)"],
                        ["5-Level Paging (PAGING57)", "4 KB", "57-bit address space", "Adds PML5 level", "Enables up to 128 PB virtual memory"],
                    ],
                },
            },
            {
                "h1": "2. Page Fault Handling and Demand Paging Workflow",
                "body": [
                    "Under demand paging, pages are only loaded into physical DRAM when referenced by the processor:",
                    "1. The CPU attempts memory access at virtual address; MMU checks TLB. On TLB miss, page table walk occurs.",
                    "2. The valid/present bit in the Page Table Entry (PTE) is 0 -> MMU triggers hardware Interrupt 14 (<b>Page Fault Exception</b>).",
                    "3. CPU switches to kernel mode ring 0, pushes faulting address to CR2 register, and executes page fault handler <code>do_page_fault()</code>.",
                    "4. Kernel verifies memory reference against Virtual Memory Areas (VMA). If invalid -> sends SIGSEGV.",
                    "5. If valid reference, kernel allocates free physical frame. If physical memory is full, a page replacement algorithm chooses a victim frame and writes back to swap if dirty.",
                    "6. Kernel schedules non-volatile disk I/O to read the required page into the frame.",
                    "7. Once I/O completes, PTE is updated with physical frame address and valid bit set to 1. The instruction is re-executed transparently.",
                ],
                "callout": "Access Latency Comparison: L1 Cache Hit: ~1 ns (4 cycles) | TLB Hit: ~1.5 ns | Main Memory DRAM Access: ~60-80 ns | SSD Page Fault Swap: ~50,000-100,000 ns (50-100 μs) | HDD Page Fault Swap: ~8,000,000 ns (8 ms). A single page fault incurs a 100,000x latency penalty!",
            },
            {
                "h1": "3. Page Replacement Algorithms: Fault Rates and Belady's Anomaly",
                "body": [
                    "When physical memory is exhausted, the OS replacement policy selects which frame to evict.",
                    "<b>Belady's Anomaly:</b> The phenomenon where increasing the number of physical page frames results in an INCREASE in the number of page faults. FIFO is susceptible to Belady's Anomaly, whereas stack algorithms (LRU, Optimal) are mathematically immune.",
                ],
                "table": {
                    "headers": ["Algorithm", "Hardware Overhead", "Page Fault Rate", "Susceptible to Belady's?", "Implementation Approach"],
                    "widths": [115, 105, 105, 105, 102],
                    "rows": [
                        ["Optimal (MIN / Clairvoyant)", "Impossible (requires future knowledge)", "Minimum theoretical", "No (Stack algorithm)", "Benchmark baseline for offline trace analysis"],
                        ["Least Recently Used (LRU)", "High (timestamp / hardware doubly linked list)", "Near-optimal", "No (Stack algorithm)", "Maintains exact access recency order"],
                        ["Clock / Second-Chance", "Low (1 reference bit per PTE)", "Very close to LRU", "No", "Circular buffer pointer; clears ref bit on sweep"],
                        ["First-In, First-Out (FIFO)", "Minimal (FIFO queue of arrival)", "Poor / Unstable", "Yes (demonstrated with 3 vs 4 frames)", "Evicts oldest loaded page regardless of usage"],
                        ["Least Frequently Used (LFU)", "High (frequency counter per page)", "Poor under phase changes", "No", "Evicts lowest reference count; suffers from history"],
                        ["Two-Queue (2Q / Linux Page Cache)", "Low (Active + Inactive LRU lists)", "Superior scan resistance", "No", "Filters one-time sequential scans into inactive list"],
                    ],
                },
            },
            {
                "h1": "4. Thrashing and The Working Set Model",
                "body": [
                    "If the sum of working sets across all active processes exceeds available physical DRAM (Σ WSS_i > Total RAM), processes spend more time paging in and out than executing actual instructions. This condition is termed <b>Thrashing</b>.",
                    "• The CPU utilization plummets toward zero as all cores become blocked waiting for swap disk I/O.",
                    "• The OS resolves thrashing using the <b>Working Set Model (Peter Denning)</b>: monitor process reference string over parameter window Δ. If process cannot fit its Working Set Size into assigned frames, the OS suspends the process entirely and swaps its entire state out to restore system stability.",
                ],
            },
        ],
    )

    # ──────────────────────────────────────────────────────────────────────────
    # 3. Concurrency, Synchronization & Deadlocks
    # ──────────────────────────────────────────────────────────────────────────
    build_pdf(
        filename="03_OS_Concurrency_Synchronization_and_Deadlocks.pdf",
        title="Operating Systems: Concurrency, Synchronization & Deadlock Prevention",
        subtitle="Race Conditions, Mutual Exclusion, Semaphores, Monitors, and Banker's Safety Algorithm",
        metadata={
            "doc_id": "OS-SYNC-2024-003",
            "practice": "Concurrency, Locks & Deadlocks",
            "system": "POSIX Mutexes, Linux Futex, Dijkstra Semaphores",
            "year": 2024,
        },
        sections=[
            {
                "h1": "1. Critical Section Problem and Synchronization Criteria",
                "body": [
                    "A critical section is a sequence of instructions accessing shared state that must not be concurrently executed by more than one thread.",
                    "A valid solution to the critical section problem must satisfy three mandatory criteria:",
                    "1. <b>Mutual Exclusion:</b> If process P is executing in its critical section, no other processes can execute in their critical sections.",
                    "2. <b>Progress:</b> If no process is executing in its critical section and some processes wish to enter, only those processes not executing in their remainder sections can participate in deciding who enters next, and this selection cannot be postponed indefinitely.",
                    "3. <b>Bounded Waiting:</b> There must exist a bound on the number of times other processes are allowed to enter their critical sections after a process has made a request to enter and before that request is granted.",
                ],
                "callout": "Peterson's Algorithm: Provides a mathematical, software-only mutual exclusion guarantee for two processes using shared variables 'flag[2]' and 'turn'. On modern out-of-order superscalar CPUs, hardware memory barriers (MFENCE) are required to prevent speculative instruction reordering from violating mutual exclusion.",
            },
            {
                "h1": "2. Hardware Synchronization Primitives vs. Software Primitives",
                "body": [
                    "Modern multiprocessor systems provide atomic hardware instructions that execute atomically across cache-coherent memory:",
                ],
                "table": {
                    "headers": ["Primitive", "Level", "Blocking Behavior", "Best Use Case", "Overhead / Notes"],
                    "widths": [115, 80, 115, 115, 107],
                    "rows": [
                        ["Test-and-Set / CAS", "Hardware instruction", "Non-blocking / Atomic", "Lock-free algorithms & spinlocks", "x86 LOCK CMPXCHG; cache line contention"],
                        ["Spinlock", "Kernel / Low-level", "Busy-waits (spins on CPU core)", "Short critical sections (< 1 μs)", "Wastes CPU cycles; illegal in user space on single-core"],
                        ["Mutex (Mutual Exclusion)", "OS / Library", "Blocks thread (sleeps in runqueue)", "General critical section protection", "Context switches sleeping thread; Linux futex optimized"],
                        ["Counting Semaphore", "OS primitive", "Integer counter with wait/signal", "Resource pool of N units", "Dijkstra P() and V() operations; general signaling"],
                        ["Binary Semaphore", "OS primitive", "Restricted integer (0 or 1)", "Mutual exclusion / Signaling", "Differs from mutex: semaphore has no ownership"],
                        ["Condition Variable", "Language / Library", "Releases lock & sleeps atomically", "Event notification / Producer-Consumer", "Must always be paired with a mutex in a while loop"],
                    ],
                },
            },
            {
                "h1": "3. Deadlocks: The Four Coffman Conditions",
                "body": [
                    "A deadlock is a state where a set of processes are blocked because each process holds a resource and waits for another resource held by another process in the same set.",
                    "A deadlock can arise if and only if all four <b>Coffman Conditions</b> hold simultaneously:",
                    "• <b>1. Mutual Exclusion:</b> At least one resource must be held in a non-shareable mode.",
                    "• <b>2. Hold and Wait:</b> A process must be concurrently holding at least one resource and requesting additional resources held by other processes.",
                    "• <b>3. No Preemption:</b> Resources cannot be forcibly preempted from a process holding them; they can only be released voluntarily.",
                    "• <b>4. Circular Wait:</b> A closed chain of processes exists: P_0 waits for resource held by P_1, P_1 waits for P_2, ..., P_k waits for P_0.",
                ],
            },
            {
                "h1": "4. Deadlock Handling Strategies and Banker's Algorithm",
                "body": [
                    "Operating systems manage deadlocks via three primary strategies: Deadlock Prevention, Deadlock Avoidance, and Deadlock Detection & Recovery (or the Ostrich algorithm of ignoring it).",
                    "<b>Banker's Algorithm (Edsger Dijkstra):</b> An avoidance algorithm testing for safe states before granting resource requests.",
                    "• Let <code>Available[m]</code> be available instances of resource types, <code>Max[n][m]</code> be max demand, <code>Allocation[n][m]</code> be currently held, and <code>Need[i][j] = Max[i][j] - Allocation[i][j]</code>.",
                    "• A state is <b>SAFE</b> if there exists a safe execution sequence <P_0, P_1, ..., P_n> such that for each P_i, the resources that P_i can still request can be satisfied by current Available plus resources held by all preceding processes.",
                ],
                "table": {
                    "headers": ["Strategy", "Mechanism", "Pros", "Cons", "Adoption in Modern OS"],
                    "widths": [115, 120, 105, 110, 82],
                    "rows": [
                        ["Deadlock Prevention", "Disallow 1 of 4 Coffman conditions (e.g. strict global resource numbering)", "Guarantees no deadlocks", "Low resource utilization, restrictive", "Strict lock ranking used in Linux kernel"],
                        ["Deadlock Avoidance", "Banker's Algorithm: evaluate safety on every allocation request", "Dynamic, flexible allocation", "Requires knowing future maximum requests", "Impractical for general-purpose OS"],
                        ["Detection & Recovery", "Wait-For Graph cycle detection; abort thread or preempt resource", "Optimistic; allows high resource usage", "Recovery aborts transaction or causes data loss", "Standard in database systems (DBMS)"],
                        ["Ostrich Algorithm", "Ignore problem entirely; rely on user/watchdog restart", "Zero runtime overhead", "System may freeze if deadlock occurs", "Standard approach in Linux, Windows, macOS"],
                    ],
                },
            },
        ],
    )

    # ──────────────────────────────────────────────────────────────────────────
    # 4. Storage, File Systems & Disk I/O
    # ──────────────────────────────────────────────────────────────────────────
    build_pdf(
        filename="04_OS_Storage_File_Systems_and_Disk_IO.pdf",
        title="Operating Systems: File Systems Architecture & Disk I/O Management",
        subtitle="Inodes, Directory Structures, Virtual File System (VFS), Journaling, and Disk Scheduling",
        metadata={
            "doc_id": "OS-FS-2024-004",
            "practice": "File Systems & Block I/O Subsystem",
            "system": "Linux VFS, ext4, ZFS, NVMe I/O Subsystem",
            "year": 2024,
        },
        sections=[
            {
                "h1": "1. Inode Architecture and File Allocation Schemes",
                "body": [
                    "In UNIX-derived file systems, files are represented by an <b>Index Node (Inode)</b>. The inode stores all file metadata (file size, permissions, owner UID/GID, timestamps atime/mtime/ctime, reference link count) and block address pointers, separating metadata from filename directory mappings.",
                    "• <b>Direct and Indirect Blocks:</b> Traditional UFS/ext2 inodes used 12 direct block pointers, 1 single-indirect pointer, 1 double-indirect pointer, and 1 triple-indirect pointer.",
                    "• <b>Extents (ext4):</b> Replaces individual block pointers with extents <code>(start_block, block_count)</code>. A single extent can address up to 128 MB of contiguous disk blocks, reducing metadata fragmentation and tree depth.",
                    "• <b>Hard Links vs. Soft (Symbolic) Links:</b> A hard link is another directory entry pointing directly to the existing inode number (increments link count; file data persists until link count is 0). A soft link is an independent file whose data payload contains the text path to the target file.",
                ],
                "table": {
                    "headers": ["Feature", "Contiguous Allocation", "Linked List Allocation", "Indexed (Inode) Allocation", "Extent-Based (ext4 / XFS)"],
                    "widths": [115, 105, 105, 105, 102],
                    "rows": [
                        ["Sequential Read Speed", "Maximum (contiguous sectors)", "Moderate (follows block pointers)", "High (block pointers in memory)", "Ultra-High (contiguous multi-megabyte)"],
                        ["Random Access Speed", "O(1) direct block offset", "O(N) traverse block links", "O(1) through pointer tree", "O(1) through extent B-tree"],
                        ["External Fragmentation", "Severe (requires compaction)", "None", "None", "Low (addressed by preallocation)"],
                        ["File Size Growth", "Difficult (must move or allocate max)", "Simple (append new block)", "Simple (allocate indirect blocks)", "Efficient (grow extent)"],
                        ["Reliability / Corruption", "High", "Critical (broken pointer loses file)", "Robust (inode integrity checks)", "High (checksummed extent trees)"],
                    ],
                },
            },
            {
                "h1": "2. Virtual File System (VFS) Layer",
                "body": [
                    "The Virtual File System (VFS) provides an object-oriented kernel abstraction layer allowing standard POSIX syscalls (<code>open</code>, <code>read</code>, <code>write</code>, <code>close</code>) to operate seamlessly across heterogeneous file systems (ext4, XFS, NFS, procfs, sysfs).",
                    "The VFS defines four core primary data structures:",
                    "1. <b>Superblock Object:</b> Represents an entire mounted file system (block size, total blocks, magic number, root dentry).",
                    "2. <b>Inode Object:</b> Represents a specific file or directory metadata entity.",
                    "3. <b>Dentry (Directory Entry) Object:</b> Represents a directory entry linking a pathname string component to its inode. Managed in an in-memory <b>dentry cache (dcache)</b> for rapid path lookups.",
                    "4. <b>File Object:</b> Represents an open file instance created upon <code>open()</code>, storing the current file offset pointer (f_pos), access modes, and pointer to the dentry.",
                ],
            },
            {
                "h1": "3. File System Journaling and Crash Consistency",
                "body": [
                    "A crash occurring during a multi-block file write (e.g. data block written, but inode size not yet updated) causes file system corruption.",
                    "Journaling file systems maintain a dedicated circular write-ahead log (journal) on disk to ensure atomic metadata transitions:",
                    "• <b>Journal Mode:</b> Both metadata and file payload data are written to the journal before being committed to the main file system. Highest integrity, lowest throughput.",
                    "• <b>Ordered Mode (ext4 default):</b> File payload data is flushed to disk first; once complete, metadata updates are logged to the journal. Prevents garbage data exposure on crash with near-metadata speed.",
                    "• <b>Writeback Mode:</b> Only metadata is journaled; data order is unconstrained. High speed, but crash can leave newly allocated blocks with old data.",
                ],
                "table": {
                    "headers": ["Journaling Mode", "Crash Recovery Guarantee", "Write Amplification", "Throughput Relative to Raw Disk", "Default System"],
                    "widths": [115, 125, 100, 110, 82],
                    "rows": [
                        ["Full Journal", "Zero data loss; atomic data + metadata", "2.0x (every byte written twice)", "45 - 55%", "Specialized audit / safety logs"],
                        ["Ordered Mode", "Metadata consistency; no stale data leaks", "1.0x data + small metadata journal", "88 - 94%", "Linux ext4, ext3 default"],
                        ["Writeback Mode", "Metadata consistency only; data may corrupt", "1.0x data + minimal metadata journal", "95 - 99%", "High-performance scratch disks"],
                        ["Copy-on-Write (ZFS / Btrfs)", "Always consistent; no in-place overwrite", "Variable (tree commit updates)", "85 - 92%", "Enterprise storage pools / snapshots"],
                    ],
                },
            },
            {
                "h1": "4. Disk Scheduling Algorithms: Rotational and SSD I/O",
                "body": [
                    "Disk scheduling reorders pending block I/O requests to minimize physical seek time and rotational latency:",
                    "• <b>SSTF (Shortest Seek Time First):</b> Selects request closest to current head position. Minimizes average response time, but risks starving distant tracks.",
                    "• <b>SCAN (Elevator Algorithm):</b> Arm moves in one direction servicing all requests until it reaches the outer end, then reverses direction.",
                    "• <b>C-SCAN (Circular SCAN):</b> Moves in one direction servicing requests; upon reaching the end, immediately returns to the start without servicing on return, providing uniform wait time distribution.",
                    "• <b>NVMe / SSD Schedulers:</b> Solid-State Drives have zero mechanical seek time. Schedulers like Linux <code>none</code> / <code>mq-deadline</code> bypass rotational reordering in favor of multi-queue parallel hardware completion rings (up to 64K queues with 64K depth each).",
                ],
            },
        ],
    )

    # ──────────────────────────────────────────────────────────────────────────
    # 5. Kernel Architecture, System Calls & Security
    # ──────────────────────────────────────────────────────────────────────────
    build_pdf(
        filename="05_OS_Kernel_Architecture_Syscalls_and_Security.pdf",
        title="Operating Systems: Kernel Architectures, System Calls & Security Mechanisms",
        subtitle="Monolithic vs Microkernels, Dual-Mode Execution, Trap Dispatchers, ASLR, and Linux Security Modules",
        metadata={
            "doc_id": "OS-KERN-2024-005",
            "practice": "Kernel Internals & OS Security",
            "system": "Linux Monolithic Kernel, seL4 Microkernel, eBPF Engine",
            "year": 2024,
        },
        sections=[
            {
                "h1": "1. Kernel Architectural Paradigms: Monolithic vs. Microkernel",
                "body": [
                    "The operating system kernel runs with supervisor hardware privileges (x86 Ring 0), managing all memory, device I/O, and CPU scheduling.",
                    "Two contrasting design philosophies govern kernel structure:",
                    "• <b>Monolithic Kernel (Linux, FreeBSD):</b> All core OS services (scheduler, memory manager, file systems, device drivers, network stack) run in a unified, single privileged address space. High performance due to direct function calls without IPC context switches, but a single driver crash can panic the entire operating system.",
                    "• <b>Microkernel (Mach, seL4, Minix):</b> Only bare essentials (address space management, thread scheduling, and interprocess communication) reside in Ring 0. Device drivers, file systems, and network stacks execute as isolated user-space daemons in Ring 3. Failure in a driver does not crash the kernel, but IPC message-passing overhead degrades performance by 10-30%.",
                    "• <b>Hybrid Kernel (Windows NT, macOS XNU):</b> Combines microkernel modularity with monolithic execution performance by running critical subsystems in kernel space.",
                ],
                "table": {
                    "headers": ["Architectural Metric", "Monolithic (Linux)", "Microkernel (seL4 / Minix)", "Hybrid (Windows NT)"],
                    "widths": [125, 135, 137, 135],
                    "rows": [
                        ["Privileged Code Base", "Huge (30M+ lines of code)", "Tiny (< 15,000 lines of code)", "Substantial (15M+ lines of code)"],
                        ["Crash Fault Isolation", "Low (driver bug can crash system)", "High (driver restarted in user space)", "Moderate (user/kernel driver split)"],
                        ["Inter-Subsystem Speed", "Zero-overhead direct C function calls", "Message-passing IPC & context switches", "Optimized kernel LPC / direct calls"],
                        ["Formally Verified Core", "No (too large to verify mathematically)", "Yes (seL4 mathematically proven)", "No"],
                        ["Extensibility", "Loadable Kernel Modules (LKM), eBPF", "Add/replace user-space services", "Executive subsystem drivers"],
                    ],
                },
            },
            {
                "h1": "2. Dual-Mode Execution and System Call Mechanics",
                "body": [
                    "To protect hardware and memory from unauthorized user manipulation, CPUs enforce <b>Dual-Mode Operation</b>:",
                    "• <b>User Mode (Ring 3):</b> Restricted instruction set. Memory access constrained to process page tables; direct I/O port instructions (IN/OUT) and privileged control register mutations (CR0, CR3) raise hardware traps.",
                    "• <b>Kernel Mode (Ring 0):</b> Unrestricted execution access to all CPU instructions, hardware registers, and physical address space.",
                    "<b>System Call Dispatch Sequence:</b>",
                    "1. User process loads syscall number into register (RAX on x86-64) and argument parameters into RDI, RSI, RDX, R10, R8, R9.",
                    "2. User code issues the <code>SYSCALL</code> instruction (transitioning from Ring 3 to Ring 0).",
                    "3. CPU switches to kernel stack, saves return program counter to RCX and processor flags to R11, and jumps to entry point defined in <code>MSR_LSTAR</code> register.",
                    "4. Kernel checks syscall number against <code>sys_call_table</code> bounds. If valid, jumps to kernel function pointer.",
                    "5. After execution, result code is saved in RAX, and <code>SYSRET</code> restores Ring 3 user mode.",
                ],
                "callout": "System Call Overhead: A modern hardware SYSCALL instruction requires ~50-70 ns, but security mitigations against speculative execution vulnerabilities (Spectre/Meltdown KPTI - Kernel Page Table Isolation) increased context switch and syscall overhead by 15-25% on legacy hardware.",
            },
            {
                "h1": "3. OS Memory Protection & Exploitation Defenses",
                "body": [
                    "Modern operating systems deploy layered security primitives against arbitrary code execution exploits:",
                    "• <b>Address Space Layout Randomization (ASLR):</b> Randomizes base addresses of stack, heap, shared libraries, and code segment on every execution, preventing attackers from jumping to fixed buffer overflow shellcode offsets.",
                    "• <b>Data Execution Prevention (DEP / W^X):</b> MMU enforces Write XOR Execute permission bits on all page tables. Memory pages marked writable cannot be executed, neutralizing stack injection attacks.",
                    "• <b>Stack Canaries:</b> Compiler places a random integer sentinel value between local stack buffers and saved frame pointer/return address; checked before function return to detect stack smashing.",
                    "• <b>Linux Security Modules (LSM):</b> Hook architecture in the Linux kernel mediating access to critical kernel objects (inodes, tasks, files) to enforce Mandatory Access Control (MAC) policies via SELinux and AppArmor.",
                ],
            },
        ],
    )

    # ──────────────────────────────────────────────────────────────────────────
    # 6. Interprocess Communication & Distributed OS
    # ──────────────────────────────────────────────────────────────────────────
    build_pdf(
        filename="06_OS_Interprocess_Communication_and_Distributed_OS.pdf",
        title="Operating Systems: Interprocess Communication (IPC) & Distributed Foundations",
        subtitle="Pipes, UNIX Domain Sockets, POSIX Shared Memory, Message Queues, and RPC Mechanisms",
        metadata={
            "doc_id": "OS-IPC-2024-006",
            "practice": "IPC, Distributed OS & Sockets",
            "system": "Linux POSIX IPC, gRPC / Protocol Buffers, UNIX Domain Sockets",
            "year": 2024,
        },
        sections=[
            {
                "h1": "1. IPC Taxonomy and Communication Models",
                "body": [
                    "Interprocess Communication (IPC) enables isolated processes with independent virtual address spaces to exchange data and synchronize actions.",
                    "IPC models divide into two fundamental architectures:",
                    "1. <b>Shared Memory Architecture:</b> Processes map the identical physical memory frames into their respective virtual address spaces. Once established, data transfers occur at raw memory bus speed without kernel intervention. Synchronization via mutexes or semaphores is strictly required.",
                    "2. <b>Message Passing Architecture:</b> Data is encapsulated in explicit message payloads transferred through kernel-managed buffers via system calls. Eliminates user synchronization requirements, but incurs double-copy kernel overhead.",
                ],
                "table": {
                    "headers": ["IPC Mechanism", "Data Paradigm", "Cross-Host?", "Kernel Involvement on Transfer", "Benchmark Bandwidth / Latency"],
                    "widths": [115, 105, 80, 115, 117],
                    "rows": [
                        ["Anonymous Pipe", "Byte stream (FIFO)", "No", "High (kernel buffer copy)", "~2.5 GB/s  |  1.8 μs"],
                        ["Named Pipe (FIFO)", "Byte stream (filesystem node)", "No", "High (kernel buffer copy)", "~2.4 GB/s  |  2.0 μs"],
                        ["POSIX Message Queue", "Discrete structured messages", "No", "High (kernel queue management)", "~1.8 GB/s  |  2.4 μs"],
                        ["POSIX Shared Memory", "Raw shared address space", "No", "Zero (direct DRAM read/write)", "~35.0 GB/s  |  0.08 μs"],
                        ["UNIX Domain Socket", "Stream or Datagram", "No", "Moderate (socket buffer copy)", "~4.2 GB/s  |  1.2 μs"],
                        ["TCP / UDP Sockets", "Network packet stream", "Yes", "High (TCP/IP network stack)", "~1.1 GB/s  |  25 - 45 μs"],
                        ["gRPC / Remote Call (RPC)", "Typed protobuf serialized RPC", "Yes", "High (serialization + network)", "~0.4 GB/s  |  120 - 250 μs"],
                    ],
                },
            },
            {
                "h1": "2. Detailed Analysis of Pipes and Sockets",
                "body": [
                    "<b>Anonymous Pipes:</b> Created via <code>pipe(int fd[2])</code>, returning a read descriptor <code>fd[0]</code> and write descriptor <code>fd[1]</code>. Unidirectional communication strictly between related processes sharing parent-child ancestry. Bounded kernel buffer (typically 64 KB on Linux); write blocks if pipe buffer is full, read blocks if pipe buffer is empty.",
                    "<b>UNIX Domain Sockets (AF_UNIX):</b> Bidirectional stream (SOCK_STREAM) or datagram (SOCK_DGRAM) endpoints addressed by filesystem pathnames. Bypasses all IP checksumming, routing, and packet encapsulation logic of TCP/IP, delivering over 3x the throughput of loopback TCP (127.0.0.1) with support for passing open file descriptors across process boundaries via <code>SCM_RIGHTS</code>.",
                ],
            },
            {
                "h1": "3. Remote Procedure Call (RPC) & Distributed Primitives",
                "body": [
                    "Remote Procedure Calls (RPC) abstract network communication so that invoking a procedure on a remote server has the syntactic interface of a local subroutine call.",
                    "<b>RPC Execution Flow:</b>",
                    "1. Client code calls local <b>Client Stub</b> with standard function arguments.",
                    "2. Client Stub marshals (serializes) parameters into a network-neutral canonical format (Protocol Buffers, JSON, XDR).",
                    "3. Client Stub invokes OS transport layer to transmit message packet over TCP/UDP to remote server.",
                    "4. Remote OS delivers packet to <b>Server Stub</b>, which unmarshals parameters and invokes the actual server procedure.",
                    "5. Server execution produces return values; Server Stub marshals results and sends network reply packet.",
                    "6. Client Stub receives reply, unmarshals return value, and returns to client caller transparently.",
                ],
                "callout": "Distributed Failure Semantics: Unlike local function calls which guarantee exactly-once execution, distributed RPCs operate over unreliable networks and must handle dropped packets and crashes using: At-Least-Once (retry on timeout), At-Most-Once (idempotency tokens / deduplication), or Exactly-Once (transactional distributed logging).",
            },
        ],
    )

    # ──────────────────────────────────────────────────────────────────────────
    # 7. Virtualization, Containers & Resource Isolation
    # ──────────────────────────────────────────────────────────────────────────
    build_pdf(
        filename="07_OS_Virtualization_Containers_and_Resource_Isolation.pdf",
        title="Operating Systems: Virtualization, Containers & Resource Isolation",
        subtitle="Hardware Hypervisors (Type 1 vs Type 2), Linux cgroups v2, Namespaces, and OverlayFS",
        metadata={
            "doc_id": "OS-VIRT-2024-007",
            "practice": "Virtualization, Cloud OS & Containers",
            "system": "KVM Hypervisor, Docker, Linux cgroups v2, Namespaces",
            "year": 2024,
        },
        sections=[
            {
                "h1": "1. Virtualization Foundations: Type 1 vs. Type 2 Hypervisors",
                "body": [
                    "Virtualization multiplexes physical machine hardware among multiple isolated guest operating system environments.",
                    "The Virtual Machine Monitor (VMM) or Hypervisor enforces CPU, memory, and device isolation:",
                    "• <b>Type 1 (Bare-Metal) Hypervisors (KVM, VMware ESXi, Xen):</b> Execute directly on physical hardware without a host OS intermediate layer. Guest OS executes in hardware-virtualized rings. Maximum performance, low latency overhead, standard in enterprise cloud datacenters.",
                    "• <b>Type 2 (Hosted) Hypervisors (VirtualBox, VMware Workstation):</b> Run as standard application processes on top of a conventional host OS (Windows, macOS). Hardware requests pass through host OS driver stack, incurring additional abstraction layers and context switch overhead.",
                ],
                "table": {
                    "headers": ["Architecture", "Host OS Required?", "Hardware CPU Access", "I/O Virtualization Path", "Benchmark CPU Overhead"],
                    "widths": [115, 95, 115, 115, 92],
                    "rows": [
                        ["Type 1 (Bare-Metal / KVM)", "No (or embedded Linux kernel)", "Intel VT-x / AMD-V hardware assist", "Virtio paravirtualized / SR-IOV direct", "1.2 - 2.5%"],
                        ["Type 2 (Hosted / VirtualBox)", "Yes (e.g. Windows, macOS)", "Hardware assist via host driver", "Emulated software device layer", "6.5 - 12.0%"],
                        ["OS Container (Docker / Podman)", "Shared host Linux kernel", "Direct native host core execution", "Native host kernel block & net drivers", "0.1 - 0.5%"],
                    ],
                },
            },
            {
                "h1": "2. Linux Container Primitives: Namespaces and Control Groups (cgroups)",
                "body": [
                    "Containers are NOT lightweight virtual machines; they do not virtualize hardware. A container is a standard Linux process governed by two core Linux kernel isolation primitives:",
                    "<b>1. Linux Namespaces (Resource Visibility Isolation):</b> Restricts what a process can see across 7 subsystem namespaces:",
                    "• <b>PID Namespace:</b> Isolates process ID tree. The container entrypoint process is PID 1 inside the container, but maps to a normal PID on the host.",
                    "• <b>NET Namespace:</b> Private virtual network interface, loopback, routing table, and iptables firewall rules.",
                    "• <b>MNT Namespace:</b> Private filesystem mount points, isolating root directory view (pivot_root).",
                    "• <b>IPC Namespace:</b> Isolated POSIX message queues, semaphores, and shared memory segments.",
                    "• <b>UTS Namespace:</b> Private hostname and domain name.",
                    "• <b>USER Namespace:</b> Maps container root UID 0 to an unprivileged non-root UID 10001 on the host for defense-in-depth.",
                    "<b>2. Control Groups (cgroups v2 - Resource Quantity Allocation):</b> Restricts how much of a resource a process group can consume:",
                    "• <code>cpu.max</code>: Enforces bandwidth quota limits (e.g. 200000 100000 specifies max 2 CPU cores per 100ms period).",
                    "• <code>memory.max</code>: Hard upper limit on physical DRAM. If exceeded, kernel invokes Out-Of-Memory (OOM) killer on container processes.",
                    "• <code>io.max</code>: Enforces read/write bytes-per-second and IOPS throttles on block devices.",
                ],
            },
            {
                "h1": "3. Storage Layering: OverlayFS Mechanics",
                "body": [
                    "Containers achieve fast image startup and minimal disk footprint through Copy-on-Write (CoW) union filesystems, primarily <b>OverlayFS</b>.",
                    "An OverlayFS mount combines three directory hierarchies:",
                    "• <b>Lower Directory (lowerdir):</b> Read-only base container image layers. Multiple running containers share the identical read-only lowerdir layers in host storage.",
                    "• <b>Upper Directory (upperdir):</b> Read-write ephemeral container layer. All file modifications, creations, and deletions are recorded here.",
                    "• <b>Merged Directory (merged):</b> The unified unified mount point presented to the container process.",
                    "<b>Copy-on-Write (CoW) Behavior:</b> When a container process modifies an existing file residing in lowerdir, the kernel copies the entire file up to upperdir before applying writes. Unmodified files are read directly from shared lower layers with zero memory duplication.",
                ],
                "table": {
                    "headers": ["Action", "Source Location", "Operation Performed", "Upperdir Effect", "Latency Impact"],
                    "widths": [105, 105, 120, 110, 92],
                    "rows": [
                        ["Read Existing File", "lowerdir", "Direct read from page cache", "No change", "Zero overhead"],
                        ["Create New File", "upperdir", "Direct write in upper directory", "File created in upperdir", "Native write speed"],
                        ["Modify Existing File", "lowerdir", "Copy-on-Write duplicate to upperdir", "Full copy created in upperdir", "One-time copy latency penalty"],
                        ["Delete Existing File", "lowerdir", "Create whiteout character device (0,0)", "Whiteout node masks lowerdir", "Fast metadata record"],
                    ],
                },
            },
        ],
    )

    print("All 7 Operating System reference PDFs generated successfully!")


if __name__ == "__main__":
    generate_all()
