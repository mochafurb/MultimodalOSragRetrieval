# Test Questions — OS databse rag retrieval

Sample questions to test the Operating Systems RAG application. Based on the 7 OS reference PDFs in `data/`.
Ask them one at a time, in order in the same chat session (so follow-ups work).

---

## 1. Basic Fact Questions (plain text answer, no table/chart)

1. What information is stored inside a Process Control Block (PCB)?
2. How does the Linux Completely Fair Scheduler (CFS) calculate virtual runtime (vruntime)?
3. What is a Translation Lookaside Buffer (TLB) and how does it speed up memory translation?
4. What are the four Coffman conditions required for a deadlock to occur?
5. What is the difference between a hard link and a soft (symbolic) link in an inode-based file system?
6. What is Belady's Anomaly and which page replacement algorithm is susceptible to it?
7. What are the three mandatory criteria that any valid solution to the critical section problem must satisfy?
8. Explain the difference between Type 1 and Type 2 hypervisors.
9. What are the two core Linux kernel primitives that power Docker containers?

---

## 2. Table Questions (should render a markdown table)

10. Show a table comparing processes, kernel threads, and user-level green threads across address space, creation latency, context switch cost, and scheduling.
11. Create a table comparing CPU scheduling algorithms (FCFS, SJF, SRTF, Round Robin, Priority, MLFQ, and CFS) showing preemption, optimization goal, and main failure mode/risk.
12. Show a table of page replacement algorithms (Optimal, LRU, Clock, FIFO, LFU, 2Q) comparing hardware overhead, fault rate, susceptibility to Belady's anomaly, and implementation approach.
13. Create a comparison table of Interprocess Communication (IPC) mechanisms showing data paradigm, whether cross-host is supported, kernel copy involvement, and typical bandwidth.
14. Show a table comparing file allocation schemes: Contiguous, Linked List, Inode-Indexed, and Extent-Based.

---

## 3. Chart Questions (should generate a real chart grounded in the docs)

15. Show a bar chart comparing the benchmark bandwidth (GB/s) of common OS IPC mechanisms: POSIX Shared Memory, UNIX Domain Sockets, Anonymous Pipes, POSIX Message Queues, and TCP loopback.
16. Chart the memory access latencies across the memory hierarchy (L1 Cache Hit, TLB Hit, DRAM Access, SSD Swap Fault, HDD Swap Fault) in nanoseconds.
17. Chart something that has no numerical backing in the documents, e.g.: "Chart how happy kernel developers are." *(should refuse — no numeric data exists for this)*

---

## 4. Follow-up Questions (ask right after a previous answer, referencing it)

Ask #10 first, then:
18. From the threads vs processes table you just gave me, why is a thread context switch so much faster than a process context switch?
19. Based on that same comparison, when would you choose multi-processing over multi-threading despite the higher overhead?

Ask #11 first, then:
20. Out of the CPU scheduling algorithms listed, which one is best suited for interactive desktop workloads and why?
21. Why does Shortest Job First (SJF) have the risk of starvation?

Ask #6 (basic fact) first, then:
22. You mentioned that FIFO suffers from Belady's anomaly — why are LRU and Optimal immune to it?

---

## 5. Comparison / Synthesis Questions

23. Compare Monolithic kernels vs Microkernels: what are the reliability vs performance trade-offs?
24. Explain the difference between Deadlock Prevention, Deadlock Avoidance (Banker's Algorithm), and Deadlock Detection.
25. How does a Copy-on-Write (CoW) union filesystem like OverlayFS optimize container image startup and disk footprint?

---

## 6. Chitchat / Meta Questions (should NOT trigger retrieval)

26. Hi, what can you help me with?
27. Thanks, that explanation of CFS was really clear!
28. What Operating System topics do you have documents on?

---

## 7. Out-of-Scope Questions (should say it's not in the knowledge base)

29. What is the current stock price of Microsoft Corporation?
30. Who won the 2024 Olympic marathon?
