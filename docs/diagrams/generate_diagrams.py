#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to generate 3 UML diagrams for Practical Work 2:
1. Use Case Diagram
2. Class Diagram
3. Sequence Diagram
"""

import os
import subprocess

OUT_DIR = "/Users/rocke/prog/MySearchEngine/docs/diagrams"
os.makedirs(OUT_DIR, exist_ok=True)

# -------------------------------------------------------------
# 1. USE CASE DIAGRAM
# -------------------------------------------------------------
use_case_dot = """digraph UseCaseDiagram {
    graph [rankdir=LR, dpi=300, fontname="Helvetica", bgcolor="white", compound=true, pad="0.3", nodesep="0.4", ranksep="0.8"];
    node [fontname="Helvetica", fontsize=10];
    edge [fontname="Helvetica", fontsize=9, color="#424242"];

    // Actors
    subgraph cluster_actors_left {
        style=invis;
        user [shape=none, margin=0, label=<<table border="0" cellborder="0" cellspacing="0">
            <tr><td><font point-size="11"><b>«actor»</b></font></td></tr>
            <tr><td bgcolor="#E3F2FD" border="1" color="#1E88E5" cellpadding="8"><b>Пользователь</b><br/>(Студент / Исследователь)</td></tr>
        </table>>];
    }

    subgraph cluster_actors_right {
        style=invis;
        fs [shape=none, margin=0, label=<<table border="0" cellborder="0" cellspacing="0">
            <tr><td><font point-size="11"><b>«actor»</b></font></td></tr>
            <tr><td bgcolor="#ECEFF1" border="1" color="#607D8B" cellpadding="8"><b>Файловая система</b><br/>(ОС / Локальный диск)</td></tr>
        </table>>];
    }

    // System Boundary
    subgraph cluster_system {
        label = "Подсистема MySearchEngine (Консольное приложение)";
        fontname = "Helvetica-Bold";
        fontsize = 12;
        color = "#90CAF9";
        style = "dashed,rounded";
        bgcolor = "#F8FAFC";
        margin = 25;

        // Use cases
        uc_repl [label="Ввести поисковый\\nзапрос в REPL (UR-1, FR-4)", shape=ellipse, style="filled", fillcolor="#E3F2FD", color="#1565C0", penwidth=1.5];
        uc_spellcheck [label="«extend»\\nАвтоисправление\\nопечатки (FR-5, UR-2)", shape=ellipse, style="filled", fillcolor="#FFF3E0", color="#EF6C00", penwidth=1.2];
        uc_rank [label="«include»\\nРанжирование результатов\\nпо релевантности (FR-6, UR-3)", shape=ellipse, style="filled", fillcolor="#FFFFFF", color="#1976D2", penwidth=1.2];
        uc_snippets [label="«include»\\nФормирование сниппетов\\nи путей (FR-6, UR-5)", shape=ellipse, style="filled", fillcolor="#FFFFFF", color="#1976D2", penwidth=1.2];

        uc_rescan [label="Индексация / переиндексация\\nпо команде rescan (UR-4, FR-1, FR-3)\\n[добавление, изменение, удаление]", shape=ellipse, style="filled", fillcolor="#E8F5E9", color="#2E7D32", penwidth=1.5];
        uc_specify_dir [label="«include»\\nУказать путь\\nк директории", shape=ellipse, style="filled", fillcolor="#FFFFFF", color="#43A047", penwidth=1.2];
        uc_scan [label="«include»\\nРекурсивное сканирование\\nфайлов .txt (FR-1)", shape=ellipse, style="filled", fillcolor="#FFFFFF", color="#43A047", penwidth=1.2];
        uc_preprocess [label="«include»\\nПредобработка текста\\n(UTF-8, токенизация) (FR-2)", shape=ellipse, style="filled", fillcolor="#FFFFFF", color="#43A047", penwidth=1.2];
        uc_build_index [label="«include»\\nПостроение / перестроение\\nиндекса в RAM (FR-3)", shape=ellipse, style="filled", fillcolor="#FFFFFF", color="#43A047", penwidth=1.2];

        uc_exit [label="Завершить работу (:q)\\n(UR-6)", shape=ellipse, style="filled", fillcolor="#FFEBEE", color="#C62828", penwidth=1.5];
    }

    // Associations User
    user -> uc_repl [color="#1E88E5", penwidth=1.3];
    user -> uc_rescan [color="#2E7D32", penwidth=1.3];
    user -> uc_exit [color="#C62828", penwidth=1.3];

    // Internal UC relationships
    uc_rescan -> uc_specify_dir [style="dashed", arrowhead="open", label="«include»", color="#2E7D32"];
    uc_rescan -> uc_scan [style="dashed", arrowhead="open", label="«include»", color="#2E7D32"];
    uc_rescan -> uc_preprocess [style="dashed", arrowhead="open", label="«include»", color="#2E7D32"];
    uc_rescan -> uc_build_index [style="dashed", arrowhead="open", label="«include»", color="#2E7D32"];

    uc_repl -> uc_spellcheck [style="dashed", arrowhead="open", label="«extend»\\n[слово не найдено]", color="#EF6C00"];
    uc_repl -> uc_rank [style="dashed", arrowhead="open", label="«include»", color="#1565C0"];
    uc_repl -> uc_snippets [style="dashed", arrowhead="open", label="«include»", color="#1565C0"];

    // Associations External System
    uc_scan -> fs [color="#607D8B", penwidth=1.3, style="solid"];
}
"""

with open(f"{OUT_DIR}/use_case_diagram.dot", "w", encoding="utf-8") as f:
    f.write(use_case_dot)

subprocess.run(["dot", "-Tpng", "-Gdpi=300", f"{OUT_DIR}/use_case_diagram.dot", "-o", f"{OUT_DIR}/use_case_diagram.png"], check=True)
print("Use Case diagram generated.")

# -------------------------------------------------------------
# 2. CLASS DIAGRAM
# -------------------------------------------------------------
class_dot = """digraph ClassDiagram {
    graph [rankdir=BT, dpi=300, fontname="Helvetica", bgcolor="white", compound=true, pad="0.3", nodesep="0.6", ranksep="0.7"];
    node [shape=plaintext, fontname="Helvetica", fontsize=9];
    edge [fontname="Helvetica", fontsize=8, color="#37474F"];

    // REPL
    REPL [label=<<table border="1" cellborder="0" cellspacing="0" cellpadding="4" bgcolor="#FFFFFF" color="#5E35B1">
        <tr><td bgcolor="#EDE7F6" align="center"><b>«presentation»<br/>REPL</b></td></tr>
        <hr/>
        <tr><td align="left">- engine: SearchEngine&amp;</td></tr>
        <tr><td align="left">- isRunning: bool</td></tr>
        <hr/>
        <tr><td align="left">+ run(): void</td></tr>
        <tr><td align="left">- processCommand(cmd: string): void</td></tr>
        <tr><td align="left">- displayResults(res: vector&lt;SearchResult&gt;): void</td></tr>
        <tr><td align="left">- printHelp(): void</td></tr>
    </table>>];

    // SearchEngine
    SearchEngine [label=<<table border="1" cellborder="0" cellspacing="0" cellpadding="4" bgcolor="#FFFFFF" color="#2E7D32">
        <tr><td bgcolor="#E8F5E9" align="center"><b>«service»<br/>SearchEngine</b></td></tr>
        <hr/>
        <tr><td align="left">- docStore: DocumentStore</td></tr>
        <tr><td align="left">- index: InvertedIndex</td></tr>
        <tr><td align="left">- spellChecker: SpellChecker</td></tr>
        <hr/>
        <tr><td align="left">+ rescan(dirPath: string): IndexReport</td></tr>
        <tr><td align="left">+ search(query: string, maxResults: int): vector&lt;SearchResult&gt;</td></tr>
        <tr><td align="left">- extractSnippets(docId: int, term: wstring): vector&lt;string&gt;</td></tr>
        <tr><td align="left">- rankResults(matches: PostingList): vector&lt;SearchResult&gt;</td></tr>
    </table>>];

    // DocumentStore
    DocumentStore [label=<<table border="1" cellborder="0" cellspacing="0" cellpadding="4" bgcolor="#FFFFFF" color="#1565C0">
        <tr><td bgcolor="#E3F2FD" align="center"><b>«entity»<br/>DocumentStore</b></td></tr>
        <hr/>
        <tr><td align="left">- documents: unordered_map&lt;int, DocumentMetadata&gt;</td></tr>
        <tr><td align="left">- nextDocId: int</td></tr>
        <hr/>
        <tr><td align="left">+ addDocument(path: string, sents: vector&lt;wstring&gt;): int</td></tr>
        <tr><td align="left">+ updateDocument(docId: int, sents: vector&lt;wstring&gt;): void</td></tr>
        <tr><td align="left">+ removeDocument(path: string): void</td></tr>
        <tr><td align="left">+ getDocument(docId: int): const DocumentMetadata&amp;</td></tr>
        <tr><td align="left">+ getSentence(docId: int, sIdx: int): wstring</td></tr>
        <tr><td align="left">+ getTotalDocs(): size_t</td></tr>
    </table>>];

    // DocumentMetadata
    DocumentMetadata [label=<<table border="1" cellborder="0" cellspacing="0" cellpadding="4" bgcolor="#FFFFFF" color="#1565C0">
        <tr><td bgcolor="#E3F2FD" align="center"><b>«struct»<br/>DocumentMetadata</b></td></tr>
        <hr/>
        <tr><td align="left">+ docId: int</td></tr>
        <tr><td align="left">+ filePath: string</td></tr>
        <tr><td align="left">+ sentences: vector&lt;wstring&gt;</td></tr>
        <tr><td align="left">+ wordCount: size_t</td></tr>
    </table>>];

    // InvertedIndex
    InvertedIndex [label=<<table border="1" cellborder="0" cellspacing="0" cellpadding="4" bgcolor="#FFFFFF" color="#C2185B">
        <tr><td bgcolor="#FCE4EC" align="center"><b>«entity»<br/>InvertedIndex</b></td></tr>
        <hr/>
        <tr><td align="left">- table: unordered_map&lt;wstring, PostingList&gt;</td></tr>
        <tr><td align="left">- vocabulary: vector&lt;wstring&gt;</td></tr>
        <hr/>
        <tr><td align="left">+ addTerm(term: wstring, docId: int, sIdx: int): void</td></tr>
        <tr><td align="left">+ removeDocumentTerms(docId: int): void</td></tr>
        <tr><td align="left">+ lookup(term: wstring): const PostingList*</td></tr>
        <tr><td align="left">+ contains(term: wstring): bool</td></tr>
        <tr><td align="left">+ getVocabulary(): const vector&lt;wstring&gt;&amp;</td></tr>
    </table>>];

    // PostingList
    PostingList [label=<<table border="1" cellborder="0" cellspacing="0" cellpadding="4" bgcolor="#FFFFFF" color="#C2185B">
        <tr><td bgcolor="#FCE4EC" align="center"><b>«entity»<br/>PostingList</b></td></tr>
        <hr/>
        <tr><td align="left">- postings: unordered_map&lt;int, Posting&gt;</td></tr>
        <hr/>
        <tr><td align="left">+ addOccurrence(docId: int, sIdx: int): void</td></tr>
        <tr><td align="left">+ getPostings(): const unordered_map&lt;int, Posting&gt;&amp;</td></tr>
        <tr><td align="left">+ getTermFrequency(docId: int): int</td></tr>
        <tr><td align="left">+ getDocumentCount(): size_t</td></tr>
    </table>>];

    // Posting
    Posting [label=<<table border="1" cellborder="0" cellspacing="0" cellpadding="4" bgcolor="#FFFFFF" color="#C2185B">
        <tr><td bgcolor="#FCE4EC" align="center"><b>«struct»<br/>Posting</b></td></tr>
        <hr/>
        <tr><td align="left">+ docId: int</td></tr>
        <tr><td align="left">+ termFrequency: int</td></tr>
        <tr><td align="left">+ sentenceIndices: vector&lt;int&gt;</td></tr>
    </table>>];

    // SpellChecker
    SpellChecker [label=<<table border="1" cellborder="0" cellspacing="0" cellpadding="4" bgcolor="#FFFFFF" color="#EF6C00">
        <tr><td bgcolor="#FFF3E0" align="center"><b>«service»<br/>SpellChecker</b></td></tr>
        <hr/>
        <tr><td align="left">- maxDistance: int</td></tr>
        <hr/>
        <tr><td align="left">+ suggest(term: wstring, vocab: vector&lt;wstring&gt;): wstring</td></tr>
        <tr><td align="left">+ damerauLevenshtein(s1: wstring, s2: wstring): int</td></tr>
    </table>>];

    // TextProcessor
    TextProcessor [label=<<table border="1" cellborder="0" cellspacing="0" cellpadding="4" bgcolor="#FFFFFF" color="#00838F">
        <tr><td bgcolor="#E0F7FA" align="center"><b>«utility»<br/>TextProcessor</b></td></tr>
        <hr/>
        <tr><td align="left">+ splitSentences(raw: wstring): vector&lt;wstring&gt;</td></tr>
        <tr><td align="left">+ tokenize(sent: wstring): vector&lt;wstring&gt;</td></tr>
        <tr><td align="left">+ normalize(token: wstring): wstring</td></tr>
        <tr><td align="left">+ utf8ToWstring(s: string): wstring</td></tr>
        <tr><td align="left">+ wstringToUtf8(ws: wstring): string</td></tr>
    </table>>];

    // SearchResult
    SearchResult [label=<<table border="1" cellborder="0" cellspacing="0" cellpadding="4" bgcolor="#FFFFFF" color="#546E7A">
        <tr><td bgcolor="#ECEFF1" align="center"><b>«data»<br/>SearchResult</b></td></tr>
        <hr/>
        <tr><td align="left">+ docId: int</td></tr>
        <tr><td align="left">+ filePath: string</td></tr>
        <tr><td align="left">+ score: int</td></tr>
        <tr><td align="left">+ snippets: vector&lt;string&gt;</td></tr>
        <tr><td align="left">+ wasCorrected: bool</td></tr>
        <tr><td align="left">+ correctedTerm: string</td></tr>
    </table>>];

    // Relationships
    // REPL -> SearchEngine (Association)
    SearchEngine -> REPL [arrowhead="none", headlabel="1", taillabel="1", color="#5E35B1", label="  использует"];

    // SearchEngine *-- DocumentStore (Composition)
    DocumentStore -> SearchEngine [arrowtail="diamond", dir="back", label="1", color="#2E7D32"];

    // DocumentStore *-- DocumentMetadata (Composition)
    DocumentMetadata -> DocumentStore [arrowtail="diamond", dir="back", label="*", color="#1565C0"];

    // SearchEngine *-- InvertedIndex (Composition)
    InvertedIndex -> SearchEngine [arrowtail="diamond", dir="back", label="1", color="#2E7D32"];

    // InvertedIndex *-- PostingList (Composition)
    PostingList -> InvertedIndex [arrowtail="diamond", dir="back", label="*", color="#C2185B"];

    // PostingList *-- Posting (Composition)
    Posting -> PostingList [arrowtail="diamond", dir="back", label="*", color="#C2185B"];

    // SearchEngine *-- SpellChecker (Composition)
    SpellChecker -> SearchEngine [arrowtail="diamond", dir="back", label="1", color="#2E7D32"];

    // SearchEngine ..> TextProcessor (Dependency)
    TextProcessor -> SearchEngine [style="dashed", arrowhead="vee", label="«use»", color="#00838F"];

    // SearchEngine ..> SearchResult (Dependency)
    SearchResult -> SearchEngine [style="dashed", arrowhead="vee", label="«creates»", color="#546E7A"];
}
"""

with open(f"{OUT_DIR}/class_diagram.dot", "w", encoding="utf-8") as f:
    f.write(class_dot)

subprocess.run(["dot", "-Tpng", "-Gdpi=300", f"{OUT_DIR}/class_diagram.dot", "-o", f"{OUT_DIR}/class_diagram.png"], check=True)
print("Class diagram generated.")

# -------------------------------------------------------------
# 3. SEQUENCE DIAGRAM
# -------------------------------------------------------------
# We create a sequence diagram using ranks and lifelines
seq_dot = """digraph SequenceDiagram {
    graph [rankdir=TB, dpi=300, fontname="Helvetica", bgcolor="white", compound=true, pad="0.4", nodesep="0.3", ranksep="0.4"];
    node [fontname="Helvetica", fontsize=9];
    edge [fontname="Helvetica", fontsize=8, color="#37474F"];

    // Lifeline headers
    subgraph cluster_headers {
        style=invis;
        u_top [label="User\\n(Пользователь)", shape=box, style="filled,rounded", fillcolor="#E3F2FD", color="#1E88E5", width=1.5];
        r_top [label="repl: REPL", shape=box, style="filled,rounded", fillcolor="#EDE7F6", color="#5E35B1", width=1.4];
        e_top [label="engine: SearchEngine", shape=box, style="filled,rounded", fillcolor="#E8F5E9", color="#2E7D32", width=1.7];
        p_top [label="proc: TextProcessor", shape=box, style="filled,rounded", fillcolor="#E0F7FA", color="#00838F", width=1.6];
        i_top [label="index: InvertedIndex", shape=box, style="filled,rounded", fillcolor="#FCE4EC", color="#C2185B", width=1.6];
        s_top [label="spell: SpellChecker", shape=box, style="filled,rounded", fillcolor="#FFF3E0", color="#EF6C00", width=1.5];
        d_top [label="store: DocumentStore", shape=box, style="filled,rounded", fillcolor="#ECEFF1", color="#546E7A", width=1.6];
    }

    // Invisible nodes on lifelines per time step
    node [shape=point, width=0.01, label=""];

    // Step 0: Initial
    { rank=same; u0; r0; e0; p0; i0; s0; d0; }
    // Step 1: User enters query
    { rank=same; u1; r1; e1; p1; i1; s1; d1; }
    // Step 2: REPL calls engine.search()
    { rank=same; u2; r2; e2; p2; i2; s2; d2; }
    // Step 3: Engine calls normalize()
    { rank=same; u3; r3; e3; p3; i3; s3; d3; }
    // Step 4: TextProcessor returns normalized word
    { rank=same; u4; r4; e4; p4; i4; s4; d4; }
    // Step 5: Engine lookups word in index
    { rank=same; u5; r5; e5; p5; i5; s5; d5; }
    // Step 6: Index returns nullptr (miss)
    { rank=same; u6; r6; e6; p6; i6; s6; d6; }
    // Step 7: Engine requests spelling suggestion
    { rank=same; u7; r7; e7; p7; i7; s7; d7; }
    // Step 8: SpellChecker computes Damerau-Levenshtein
    { rank=same; u8; r8; e8; p8; i8; s8; d8; }
    // Step 9: SpellChecker returns corrected candidate
    { rank=same; u9; r9; e9; p9; i9; s9; d9; }
    // Step 10: Engine searches index for corrected word
    { rank=same; u10; r10; e10; p10; i10; s10; d10; }
    // Step 11: Index returns PostingList
    { rank=same; u11; r11; e11; p11; i11; s11; d11; }
    // Step 12: Engine ranks documents
    { rank=same; u12; r12; e12; p12; i12; s12; d12; }
    // Step 13: Engine gets sentence snippets from store
    { rank=same; u13; r13; e13; p13; i13; s13; d13; }
    // Step 14: Store returns text snippets
    { rank=same; u14; r14; e14; p14; i14; s14; d14; }
    // Step 15: Engine returns results to REPL
    { rank=same; u15; r15; e15; p15; i15; s15; d15; }
    // Step 16: REPL displays results to User
    { rank=same; u16; r16; e16; p16; i16; s16; d16; }

    // Connect lifelines vertically
    u_top -> u0 [style=dashed, color="#9E9E9E", arrowhead=none];
    u0 -> u1 -> u2 -> u3 -> u4 -> u5 -> u6 -> u7 -> u8 -> u9 -> u10 -> u11 -> u12 -> u13 -> u14 -> u15 -> u16 [style=dashed, color="#9E9E9E", arrowhead=none];

    r_top -> r0 [style=dashed, color="#9E9E9E", arrowhead=none];
    r0 -> r1 -> r2 -> r3 -> r4 -> r5 -> r6 -> r7 -> r8 -> r9 -> r10 -> r11 -> r12 -> r13 -> r14 -> r15 -> r16 [style=dashed, color="#9E9E9E", arrowhead=none];

    e_top -> e0 [style=dashed, color="#9E9E9E", arrowhead=none];
    e0 -> e1 -> e2 -> e3 -> e4 -> e5 -> e6 -> e7 -> e8 -> e9 -> e10 -> e11 -> e12 -> e13 -> e14 -> e15 -> e16 [style=dashed, color="#9E9E9E", arrowhead=none];

    p_top -> p0 [style=dashed, color="#9E9E9E", arrowhead=none];
    p0 -> p1 -> p2 -> p3 -> p4 -> p5 -> p6 -> p7 -> p8 -> p9 -> p10 -> p11 -> p12 -> p13 -> p14 -> p15 -> p16 [style=dashed, color="#9E9E9E", arrowhead=none];

    i_top -> i0 [style=dashed, color="#9E9E9E", arrowhead=none];
    i0 -> i1 -> i2 -> i3 -> i4 -> i5 -> i6 -> i7 -> i8 -> i9 -> i10 -> i11 -> i12 -> i13 -> i14 -> i15 -> i16 [style=dashed, color="#9E9E9E", arrowhead=none];

    s_top -> s0 [style=dashed, color="#9E9E9E", arrowhead=none];
    s0 -> s1 -> s2 -> s3 -> s4 -> s5 -> s6 -> s7 -> s8 -> s9 -> s10 -> s11 -> s12 -> s13 -> s14 -> s15 -> s16 [style=dashed, color="#9E9E9E", arrowhead=none];

    d_top -> d0 [style=dashed, color="#9E9E9E", arrowhead=none];
    d0 -> d1 -> d2 -> d3 -> d4 -> d5 -> d6 -> d7 -> d8 -> d9 -> d10 -> d11 -> d12 -> d13 -> d14 -> d15 -> d16 [style=dashed, color="#9E9E9E", arrowhead=none];

    // Message calls
    u1 -> r1 [label=" 1: Ввод запроса ('програмирование')", color="#1E88E5", penwidth=1.2];
    r2 -> e2 [label=" 2: search('програмирование', max=10)", color="#5E35B1", penwidth=1.2];
    e3 -> p3 [label=" 3: normalize('програмирование')", color="#00838F", penwidth=1.2];
    p4 -> e4 [label=" 4: L'програмирование'", style=dashed, color="#00838F", arrowhead="open"];
    e5 -> i5 [label=" 5: lookup(L'програмирование')", color="#C2185B", penwidth=1.2];
    i6 -> e6 [label=" 6: nullptr (Слово не найдено)", style=dashed, color="#C2185B", arrowhead="open"];
    e7 -> s7 [label=" 7: suggest(L'програмирование', vocab)", color="#EF6C00", penwidth=1.2];
    s8 -> s8 [label=" 8: damerauLevenshtein(query, w)", color="#EF6C00", penwidth=1.2];
    s9 -> e9 [label=" 9: L'программирование' (dist=1)", style=dashed, color="#EF6C00", arrowhead="open"];
    e10 -> i10 [label=" 10: lookup(L'программирование')", color="#C2185B", penwidth=1.2];
    i11 -> e11 [label=" 11: PostingList {docId: 1, 2, ...}", style=dashed, color="#C2185B", arrowhead="open"];
    e12 -> e12 [label=" 12: rankByFrequency()", color="#2E7D32", penwidth=1.2];
    e13 -> d13 [label=" 13: getSentence(docId, sIdx)", color="#546E7A", penwidth=1.2];
    d14 -> e14 [label=" 14: vector<wstring> snippets", style=dashed, color="#546E7A", arrowhead="open"];
    e15 -> r15 [label=" 15: vector<SearchResult> (ранжировано)", style=dashed, color="#2E7D32", arrowhead="open"];
    r16 -> u16 [label=" 16: Форматированный вывод (пути, сниппеты, опечатка)", style=dashed, color="#1E88E5", arrowhead="open"];
}
"""

with open(f"{OUT_DIR}/sequence_diagram.dot", "w", encoding="utf-8") as f:
    f.write(seq_dot)

subprocess.run(["dot", "-Tpng", "-Gdpi=300", f"{OUT_DIR}/sequence_diagram.dot", "-o", f"{OUT_DIR}/sequence_diagram.png"], check=True)
print("Sequence diagram generated.")
