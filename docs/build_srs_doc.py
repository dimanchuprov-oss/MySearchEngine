#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Production script to generate the Software Requirements Specification (SRS)
for Practical Assignment #2 ("Технологии индустриального программирования").
Formatted according to ГОСТ 7.32-2017 and doc-style.
"""

import os
import subprocess
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn, nsdecls

DOCX_PATH = "/Users/rocke/prog/MySearchEngine/MySearchEngine_Практическое_занятие_2_ТИП.docx"
PDF_PATH = "/Users/rocke/prog/MySearchEngine/MySearchEngine_Практическое_занятие_2_ТИП.pdf"
DIAGRAMS_DIR = "/Users/rocke/prog/MySearchEngine/docs/diagrams"

def set_russian_language(doc):
    rPr = doc.styles['Normal'].element.get_or_add_rPr()
    rPr.append(parse_xml(f'<w:lang {nsdecls("w")} w:val="ru-RU"/>'))

def add_page_number_to_footer(section):
    footer = section.footer
    p = footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run()
    run.font.name = 'Times New Roman'
    run.font.size = Pt(10)
    run.font.color.rgb = RGBColor(100, 100, 100)
    fldSimple = OxmlElement('w:fldSimple')
    fldSimple.set(qn('w:instr'), 'PAGE')
    run._r.append(fldSimple)

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:val="clear" w:color="auto" w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=120, bottom=120, left=160, right=160):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def set_table_borders(table, color="B0BEC5", sz="4", val="single"):
    tblPr = table._tbl.tblPr
    borders = parse_xml(f'''
        <w:tblBorders {nsdecls("w")}>
            <w:top w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>
            <w:left w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>
            <w:bottom w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>
            <w:right w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>
            <w:insideH w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>
            <w:insideV w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>
        </w:tblBorders>
    ''')
    tblPr.append(borders)

def setup_table_pagination(table):
    header_tr = table.rows[0]._tr.get_or_add_trPr()
    header_tr.append(OxmlElement('w:tblHeader'))
    for row in table.rows:
        trPr = row._tr.get_or_add_trPr()
        trPr.append(OxmlElement('w:cantSplit'))

def add_body_p(doc, text, bold_prefix="", italic_prefix=""):
    p = doc.add_paragraph()
    p.paragraph_format.first_line_indent = Cm(1.25)
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.1
    if bold_prefix:
        r_b = p.add_run(bold_prefix)
        r_b.font.name = 'Times New Roman'
        r_b.font.size = Pt(11)
        r_b.font.bold = True
    if italic_prefix:
        r_i = p.add_run(italic_prefix)
        r_i.font.name = 'Times New Roman'
        r_i.font.size = Pt(12)
        r_i.font.italic = True
    r = p.add_run(text)
    r.font.name = 'Times New Roman'
    r.font.size = Pt(11)
    return p

def add_h1(doc, text, page_break_before=False):
    if page_break_before:
        doc.add_page_break()
    h = doc.add_heading(level=1)
    h.paragraph_format.first_line_indent = Cm(0)
    h.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
    h.paragraph_format.space_before = Pt(16)
    h.paragraph_format.space_after = Pt(8)
    h.paragraph_format.keep_with_next = True
    r = h.add_run(text)
    r.font.name = 'Times New Roman'
    r.font.size = Pt(16)
    r.font.bold = True
    r.font.color.rgb = RGBColor(26, 54, 93)  # Navy
    return h

def add_h2(doc, text, page_break_before=False):
    if page_break_before:
        doc.add_page_break()
    h = doc.add_heading(level=2)
    h.paragraph_format.first_line_indent = Cm(0)
    h.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
    h.paragraph_format.space_before = Pt(12)
    h.paragraph_format.space_after = Pt(6)
    h.paragraph_format.keep_with_next = True
    r = h.add_run(text)
    r.font.name = 'Times New Roman'
    r.font.size = Pt(14)
    r.font.bold = True
    r.font.color.rgb = RGBColor(43, 108, 176)  # Blue
    return h

def add_h3(doc, text):
    h = doc.add_heading(level=3)
    h.paragraph_format.first_line_indent = Cm(0)
    h.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
    h.paragraph_format.space_before = Pt(8)
    h.paragraph_format.space_after = Pt(4)
    h.paragraph_format.keep_with_next = True
    r = h.add_run(text)
    r.font.name = 'Times New Roman'
    r.font.size = Pt(12.5)
    r.font.bold = True
    r.font.color.rgb = RGBColor(45, 55, 72)
    return h

def add_bullet_item(doc, bold_prefix, text):
    p = doc.add_paragraph()
    p.paragraph_format.first_line_indent = Cm(-0.6)
    p.paragraph_format.left_indent = Cm(1.85)
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.1
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    
    r_bullet = p.add_run("— ")
    r_bullet.font.name = 'Times New Roman'
    r_bullet.font.size = Pt(12)
    r_bullet.font.bold = True
    
    if bold_prefix:
        r_b = p.add_run(bold_prefix)
        r_b.font.name = 'Times New Roman'
        r_b.font.size = Pt(11)
        r_b.font.bold = True
    r = p.add_run(text)
    r.font.name = 'Times New Roman'
    r.font.size = Pt(11)
    return p

def add_figure(doc, img_path, caption_text, width_cm=10.5):
    p_img = doc.add_paragraph()
    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_img.paragraph_format.space_before = Pt(4)
    p_img.paragraph_format.space_after = Pt(3)
    p_img.paragraph_format.first_line_indent = Cm(0)
    p_img.paragraph_format.keep_with_next = True
    run = p_img.add_run()
    run.add_picture(img_path, width=Cm(width_cm))

    p_cap = doc.add_paragraph()
    p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap.paragraph_format.space_before = Pt(2)
    p_cap.paragraph_format.space_after = Pt(6)
    p_cap.paragraph_format.first_line_indent = Cm(0)
    r_cap = p_cap.add_run(caption_text)
    r_cap.font.name = 'Times New Roman'
    r_cap.font.size = Pt(10.5)
    r_cap.font.bold = True
    r_cap.font.color.rgb = RGBColor(50, 50, 50)

def add_table_title(doc, text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.first_line_indent = Cm(0)
    p.paragraph_format.keep_with_next = True
    r = p.add_run(text)
    r.font.name = 'Times New Roman'
    r.font.size = Pt(11)
    r.font.bold = True
    r.font.color.rgb = RGBColor(40, 40, 40)
    return p

def create_styled_table(doc, headers, data, col_widths=None):
    table = doc.add_table(rows=len(data) + 1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(table)
    setup_table_pagination(table)

    # Style Header Row
    hdr_cells = table.rows[0].cells
    for i, title in enumerate(headers):
        hdr_cells[i].text = title
        set_cell_background(hdr_cells[i], "1A365D")  # Dark Navy
        set_cell_margins(hdr_cells[i], top=140, bottom=140, left=140, right=140)
        p = hdr_cells[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.first_line_indent = Cm(0)
        for r in p.runs:
            r.font.name = 'Times New Roman'
            r.font.size = Pt(10)
            r.font.bold = True
            r.font.color.rgb = RGBColor(255, 255, 255)

    # Fill data rows
    for r_idx, row_data in enumerate(data):
        row_cells = table.rows[r_idx + 1].cells
        bg_color = "F7FAFC" if r_idx % 2 == 1 else "FFFFFF"
        for c_idx, cell_value in enumerate(row_data):
            row_cells[c_idx].text = str(cell_value)
            set_cell_background(row_cells[c_idx], bg_color)
            set_cell_margins(row_cells[c_idx], top=100, bottom=100, left=130, right=130)
            p = row_cells[c_idx].paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.first_line_indent = Cm(0)
            p.paragraph_format.line_spacing = 1.1
            if c_idx == 0 or len(str(cell_value)) <= 6:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            else:
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            for r in p.runs:
                r.font.name = 'Times New Roman'
                r.font.size = Pt(9.5)

    if col_widths:
        for row in table.rows:
            for idx, width in enumerate(col_widths):
                row.cells[idx].width = width

    p_after = doc.add_paragraph()
    p_after.paragraph_format.space_before = Pt(0)
    p_after.paragraph_format.space_after = Pt(6)
    p_after.paragraph_format.first_line_indent = Cm(0)
    return table

def build_document():
    doc = Document()
    set_russian_language(doc)

    # Page setup: A4, Margins: Top 2cm, Bottom 2cm, Left 3cm, Right 1.5cm
    section = doc.sections[0]
    section.page_width = Cm(21.0)
    section.page_height = Cm(29.7)
    section.top_margin = Cm(2.0)
    section.bottom_margin = Cm(2.0)
    section.left_margin = Cm(3.0)
    section.right_margin = Cm(1.5)

    # Unlink first page header/footer for title page
    section.different_first_page_header_footer = True
    add_page_number_to_footer(section)

    # -------------------------------------------------------------
    # ТИТУЛЬНЫЙ ЛИСТ
    # -------------------------------------------------------------
    p_top = doc.add_paragraph()
    p_top.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_top.paragraph_format.space_before = Pt(0)
    p_top.paragraph_format.space_after = Pt(2)
    p_top.paragraph_format.first_line_indent = Cm(0)
    r1 = p_top.add_run("МИНИСТЕРСТВО НАУКИ И ВЫСШЕГО ОБРАЗОВАНИЯ РОССИЙСКОЙ ФЕДЕРАЦИИ\n")
    r1.font.name = 'Times New Roman'
    r1.font.size = Pt(10)
    r1.font.bold = True
    r2 = p_top.add_run("ФЕДЕРАЛЬНОЕ ГОСУДАРСТВЕННОЕ БЮДЖЕТНОЕ ОБРАЗОВАТЕЛЬНОЕ УЧРЕЖДЕНИЕ\nВЫСШЕГО ОБРАЗОВАНИЯ\n")
    r2.font.name = 'Times New Roman'
    r2.font.size = Pt(10)
    r2.font.bold = True
    r3 = p_top.add_run("«МИРЭА — Российский технологический университет»\n(РТУ МИРЭА)\n")
    r3.font.name = 'Times New Roman'
    r3.font.size = Pt(11)
    r3.font.bold = True

    p_inst = doc.add_paragraph()
    p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_inst.paragraph_format.space_before = Pt(8)
    p_inst.paragraph_format.space_after = Pt(22)
    p_inst.paragraph_format.first_line_indent = Cm(0)
    r_inst = p_inst.add_run("Институт перспективных технологий и индустриального программирования\nКафедра индустриального программирования")
    r_inst.font.name = 'Times New Roman'
    r_inst.font.size = Pt(11)

    p_disc = doc.add_paragraph()
    p_disc.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_disc.paragraph_format.space_before = Pt(20)
    p_disc.paragraph_format.space_after = Pt(6)
    p_disc.paragraph_format.first_line_indent = Cm(0)
    r_disc = p_disc.add_run("Дисциплина: «Технологии индустриального программирования»")
    r_disc.font.name = 'Times New Roman'
    r_disc.font.size = Pt(12)
    r_disc.font.italic = True

    p_theme = doc.add_paragraph()
    p_theme.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_theme.paragraph_format.space_before = Pt(12)
    p_theme.paragraph_format.space_after = Pt(8)
    p_theme.paragraph_format.first_line_indent = Cm(0)
    r_prak = p_theme.add_run("ПРАКТИЧЕСКОЕ ЗАНЯТИЕ № 2\n")
    r_prak.font.name = 'Times New Roman'
    r_prak.font.size = Pt(14)
    r_prak.font.bold = True
    r_th = p_theme.add_run("ТЕХНИЧЕСКАЯ ДОКУМЕНТАЦИЯ ПРОЕКТА (SRS)\nИ ВИЗУАЛЬНОЕ МОДЕЛИРОВАНИЕ UML\n")
    r_th.font.name = 'Times New Roman'
    r_th.font.size = Pt(15)
    r_th.font.bold = True
    r_th.font.color.rgb = RGBColor(26, 54, 93)

    p_proj = doc.add_paragraph()
    p_proj.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_proj.paragraph_format.space_before = Pt(6)
    p_proj.paragraph_format.space_after = Pt(36)
    p_proj.paragraph_format.first_line_indent = Cm(0)
    r_proj = p_proj.add_run("Тема проекта: «MySearchEngine — локальная высокоскоростная поисковая система с нечетким поиском»")
    r_proj.font.name = 'Times New Roman'
    r_proj.font.size = Pt(12.5)
    r_proj.font.bold = True

    p_meta = doc.add_paragraph()
    p_meta.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_meta.paragraph_format.space_before = Pt(36)
    p_meta.paragraph_format.space_after = Pt(45)
    p_meta.paragraph_format.first_line_indent = Cm(0)
    p_meta.paragraph_format.line_spacing = 1.25
    r_meta = p_meta.add_run(
        "Выполнил(а):\n"
        "Студент: Чупров Д. / Счётчиков О.\n"
        "Группа: ЭФБО-03-25\n\n"
        "Проверил:\n"
        "Преподаватель:\n"
        "Афонин Сергей Александрович\n"
        "Учебный год: 2026–2027 гг.\n"
    )
    r_meta.font.name = 'Times New Roman'
    r_meta.font.size = Pt(11)

    p_bot = doc.add_paragraph()
    p_bot.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_bot.paragraph_format.space_before = Pt(24)
    p_bot.paragraph_format.space_after = Pt(0)
    p_bot.paragraph_format.first_line_indent = Cm(0)
    r_bot = p_bot.add_run("Москва, 2026 г.")
    r_bot.font.name = 'Times New Roman'
    r_bot.font.size = Pt(11)

    # -------------------------------------------------------------
    # СОДЕРЖАНИЕ
    # -------------------------------------------------------------
    doc.add_page_break()
    p_toc_h = doc.add_paragraph()
    p_toc_h.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_toc_h.paragraph_format.space_before = Pt(12)
    p_toc_h.paragraph_format.space_after = Pt(16)
    p_toc_h.paragraph_format.first_line_indent = Cm(0)
    r_toc = p_toc_h.add_run("СОДЕРЖАНИЕ")
    r_toc.font.name = 'Times New Roman'
    r_toc.font.size = Pt(16)
    r_toc.font.bold = True
    r_toc.font.color.rgb = RGBColor(26, 54, 93)

    toc_items = [
        ("1. ВВЕДЕНИЕ", "3", True),
        ("  1.1. Цель документа и проекта", "3", False),
        ("  1.2. Область действия (Scope)", "3", False),
        ("  1.3. Термины, определения и сокращения", "4", False),
        ("2. ОБЩЕЕ ОПИСАНИЕ СИСТЕМЫ", "6", True),
        ("  2.1. Контекст и архитектурное окружение продукта", "6", False),
        ("  2.2. Основные функции продукта", "6", False),
        ("  2.3. Характеристики и квалификация пользователей", "6", False),
        ("  2.4. Предположения и зависимости", "6", False),
        ("3. СПЕЦИФИКАЦИЯ ТРЕБОВАНИЙ", "8", True),
        ("  3.1. Методология выявления и анализа требований", "8", False),
        ("  3.2. Бизнес-требования (Business Requirements)", "8", False),
        ("  3.3. Пользовательские требования (User Requirements)", "9", False),
        ("  3.4. Функциональные требования (Functional Requirements)", "11", False),
        ("  3.5. Нефункциональные требования (Non-Functional Requirements)", "12", False),
        ("4. АРХИТЕКТУРНЫЕ UML-ДИАГРАММЫ", "15", True),
        ("  4.1. Диаграмма вариантов использования (Use Case Diagram)", "15", False),
        ("  4.2. Диаграмма классов (Class Diagram)", "17", False),
        ("  4.3. Диаграмма последовательности (Sequence Diagram)", "18", False),
        ("5. ЗАКЛЮЧЕНИЕ", "19", True),
    ]

    toc_table = doc.add_table(rows=len(toc_items), cols=2)
    toc_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for r_idx, (sec_name, page_num, is_major) in enumerate(toc_items):
        c0, c1 = toc_table.rows[r_idx].cells
        c0.text = sec_name
        c1.text = page_num
        p0 = c0.paragraphs[0]
        p1 = c1.paragraphs[0]
        p0.paragraph_format.first_line_indent = Cm(0)
        p1.paragraph_format.first_line_indent = Cm(0)
        p0.paragraph_format.space_before = Pt(2)
        p0.paragraph_format.space_after = Pt(2)
        p1.paragraph_format.space_before = Pt(2)
        p1.paragraph_format.space_after = Pt(2)
        p0.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p1.alignment = WD_ALIGN_PARAGRAPH.RIGHT

        set_cell_margins(c0, top=40, bottom=40, left=40, right=40)
        set_cell_margins(c1, top=40, bottom=40, left=40, right=40)

        for run in p0.runs:
            run.font.name = 'Times New Roman'
            run.font.size = Pt(11)
            run.font.bold = is_major
            if is_major:
                run.font.color.rgb = RGBColor(26, 54, 93)
        for run in p1.runs:
            run.font.name = 'Times New Roman'
            run.font.size = Pt(11)
            run.font.bold = is_major

    for row in toc_table.rows:
        row.cells[0].width = Cm(14.5)
        row.cells[1].width = Cm(2.0)

    # -------------------------------------------------------------
    # РАЗДЕЛ 1. ВВЕДЕНИЕ
    # -------------------------------------------------------------
    add_h1(doc, "1. Введение", page_break_before=True)

    add_h2(doc, "1.1. Цель документа и проекта")
    add_body_p(
        doc,
        "Настоящий документ представляет собой Спецификацию требований к программному обеспечению "
        "(Software Requirements Specification, SRS) для проектирования и разработки локальной высокоскоростной "
        "поисковой системы «MySearchEngine». Документ разработан в строгом соответствии с требованиями практического "
        "задания по дисциплине «Технологии индустриального программирования» и предназначен для фиксации полного набора "
        "архитектурных, функциональных и эксплуатационных спецификаций, обеспечивающих однозначное понимание рамок и "
        "результатов проекта между разработчиками, тестировщиками и контролирующим преподавателем."
    )
    add_body_p(
        doc,
        "Главной целью программного проекта «MySearchEngine» является создание автономного, отказоустойчивого и "
        "высокопроизводительного консольного поискового движка на языке программирования C++, способного выполнять "
        "мгновенную индексацию локальных неструктурированных текстовых массивов данных, обеспечивать непрерывный "
        "диалоговый поиск в интерактивном консольном режиме (REPL) и реализовывать интеллектуальное исправление "
        "пользовательских опечаток на русском и английском языках без привлечения внешних СУБД или готовых коммерческих движков."
    )

    add_h2(doc, "1.2. Область действия (Scope)")
    add_body_p(
        doc,
        "Программная система «MySearchEngine» ориентирована на локальное использование на рабочих станциях пользователей. "
        "В границы проектируемой системы входят следующие ключевые возможности и компоненты:"
    )
    add_bullet_item(doc, "Модуль обхода файловой структуры и индексации: ", "рекурсивное обнаружение и чтение всех текстовых файлов с расширением .txt в заданной директории по явной команде пользователя rescan с поддержкой добавления, изменения и удаления документов;")
    add_bullet_item(doc, "Модуль лингвистической предобработки: ", "сегментация текста на предложения, токенизация на отдельные слова, удаление пунктуационных знаков, спецсимволов и цифр, нормализация регистра букв для кириллицы и латиницы в стандарте UTF-8;")
    add_bullet_item(doc, "Модуль инвертированного индексирования: ", "построение и актуализация компактной хэш-таблицы в оперативной памяти (In-Memory Inverted Index), связывающей уникальные термы с идентификаторами документов (DocID) и номерами содержащих их предложений (SentenceIdx);")
    add_bullet_item(doc, "Модуль интеллектуального исправления опечаток: ", "вычисление расстояния Дамерау-Левенштейна между ошибочно введенным термом и словарем индекса методом динамического программирования с оптимизацией по памяти;")
    add_bullet_item(doc, "Модуль ранжирования и сниппетирования: ", "вычисление частоты совпадений термов (Term Frequency), упорядочивание результатов по убыванию релевантности и формирование контекстных превью (1–3 предложения с найденными словами);")
    add_bullet_item(doc, "Пользовательский интерфейс: ", "интерактивная консольная среда (REPL-цикл), поддерживающая многократные запросы, команды управления каталогом и запуска индексации (rescan), а также корректное завершение работы по управляющей команде :q.")

    add_body_p(
        doc,
        "В рамки текущей версии системы намеренно не входят: обработка проприетарных бинарных форматов (.pdf, .docx), "
        "графический интерфейс (GUI), сетевое клиент-серверное взаимодействие, распределенная кластеризация данных и "
        "применение внешних реляционных или нереляционных СУБД (PostgreSQL, Elasticsearch, Lucene и др.)."
    )

    add_h2(doc, "1.3. Термины, определения и сокращения")
    add_body_p(
        doc,
        "В таблице 1 представлены ключевые термины, определения, алгоритмические понятия и аббревиатуры, "
        "используемые в настоящей спецификации и исходном коде проекта."
    )

    add_table_title(doc, "Таблица 1 — Глоссарий терминов и определений предметной области")
    glossary_headers = ["Термин / Аббревиатура", "Определение и семантическое значение в системе"]
    glossary_data = [
        ("Поисковый запрос (Query)", "Строка текста (одно или несколько слов), вводимая пользователем через интерактивный консольный интерфейс для обнаружения содержащих эти слова документов."),
        ("Релевантный документ", "Документ корпуса, содержимое которого соответствует поисковому запросу. Степень релевантности рассчитывается математически на основе частоты встречаемости слов запроса."),
        ("Токен (Token)", "Минимальная смысловая единица (последовательность символов, как правило, отдельное слово), полученная в результате лексического анализа текста."),
        ("Токенизация / Парсинг", "Процесс разделения исходного неструктурированного текста на предложения и отдельные элементарные токены (слова)."),
        ("Лингвистическая предобработка (Нормализация)", "Приведение токенов к стандартной форме: очистка от пунктуации, спецсимволов и цифр, а также приведение к нижнему регистру (Case Insensitivity) с поддержкой кириллицы и латиницы."),
        ("Инвертированный индекс (Inverted Index)", "Ключевая структура данных поискового движка. Представляет собой ассоциативный массив (хэш-таблицу), где ключом выступает уникальное нормализованное слово, а значением — список вхождений (постинг-лист) с идентификаторами документов и координатами предложений."),
        ("Сниппет (Snippet)", "Контекстный фрагмент текста документа (в системе — 1–3 предложения), содержащий искомое слово. Позволяет пользователю мгновенно оценить контекст файла без его открытия."),
        ("Ранжирование (Ranking)", "Алгоритмический процесс сортировки документов по степени соответствия запросу. Документы с большим количеством совпадений получают высший ранг и выводятся первыми."),
        ("Расстояние Дамерау-Левенштейна", "Метрика редактирования строк, определяющая минимальное число операций (вставка, удаление, замена символа, перестановка двух соседних символов — транспозиция), необходимых для преобразования одной строки в другую."),
        ("REPL (Read-Eval-Print Loop)", "Консольный интерактивный цикл «чтение-вычисление-вывод», в котором система непрерывно принимает запросы, производит поиск, выводит результаты и ожидает следующий ввод без перезапуска программы."),
        ("DocID (Document Identifier)", "Уникальный целочисленный идентификатор, присваиваемый документу при первичном сканировании каталога для компактной адресации в инвертированном индексе."),
        ("SentenceIdx", "Порядковый индекс предложения в документе, используемый для точной привязки терма к контексту и быстрого извлечения сниппета."),
        ("SOLID", "Пять фундаментальных принципов объектно-ориентированного программирования и проектирования (Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion), обеспечивающих расширяемость и сопровождаемость кодовой базы."),
        ("UTF-8", "Стандарт кодирования Unicode переменной длины, используемый для корректного представления и обработки русскоязычного и англоязычного текста."),
        ("SRS", "Software Requirements Specification — Спецификация требований к программному обеспечению.")
    ]
    create_styled_table(doc, glossary_headers, glossary_data, [Cm(5.0), Cm(11.5)])

    # -------------------------------------------------------------
    # РАЗДЕЛ 2. ОБЩЕЕ ОПИСАНИЕ СИСТЕМЫ
    # -------------------------------------------------------------
    add_h1(doc, "2. Общее описание системы", page_break_before=True)

    add_h2(doc, "2.1. Контекст и архитектурное окружение продукта")
    add_body_p(
        doc,
        "Программный продукт «MySearchEngine» спроектирован как автономное высокопроизводительное консольное приложение (CLI), "
        "функционирующее непосредственно в среде операционной системы (macOS, Linux, Windows) и не зависящее от сторонних "
        "серверов приложений или СУБД. Взаимодействие с пользователем организовано через стандартные потоки ввода-вывода (std::cin, std::cout) "
        "терминала, что обеспечивает минимальные накладные расходы и возможность работы на серверах без графической оболочки."
    )
    add_body_p(
        doc,
        "Архитектура системы строится на принципах слабой связанности (Low Coupling) и высокой зацепленности (High Cohesion). "
        "Исходный код разделен на заголовочные интерфейсы в директории include/ (engine.hpp, spellchecker.hpp) и реализацию в src/ (main.cpp). "
        "Все структуры данных размещаются в оперативной памяти (In-Memory Processing), что гарантирует максимальное быстродействие "
        "при обработке запросов."
    )

    add_h2(doc, "2.2. Основные функции продукта")
    add_body_p(
        doc,
        "Система предоставляет пользователю следующий набор базовых макрофункций:"
    )
    add_bullet_item(doc, "Индексация файлового хранилища по команде: ", "сканирование, фильтрация и структурирование всех .txt файлов в указанном пользователем каталоге по явной команде rescan; поддержка полной переиндексации при добавлении, изменении и удалении документов с выводом суммарного отчета;")
    add_bullet_item(doc, "Точный полнотекстовый поиск: ", "мгновенное сопоставление нормализованных слов запроса со словарем инвертированного индекса за время O(1);")
    add_bullet_item(doc, "Нечеткий поиск (Fuzzy Search): ", "интеллектуальный подбор ближайшего словарного аналога при наличии опечаток с последующим автоматическим выполнением поиска по исправленному терму;")
    add_bullet_item(doc, "Релевантная выдача: ", "сортировка найденных документов по числу совпадений с формированием информативных блоков, включающих абсолютный путь к файлу и релевантные цитаты (сниппеты);")
    add_bullet_item(doc, "Управление диалоговой сессией: ", "интерактивное взаимодействие в цикле REPL с возможностью повторных запросов без повторной ресурсоемкой индексации и быстрый выход по команде :q.")

    add_h2(doc, "2.3. Характеристики и квалификация пользователей")
    add_body_p(
        doc,
        "Целевыми пользователями системы являются студенты, инженеры-разработчики, системные администраторы и исследователи, "
        "которым требуется оперативный поиск информации по локальным архивам текстовой документации, конспектов, технических отчетов "
        "или программных логов. От пользователя требуется минимальный уровень компьютерной грамотности: умение запускать исполняемые "
        "файлы в терминале, указывать относительные и абсолютные пути к директориям файловой системы и вводить текстовые команды."
    )

    add_h2(doc, "2.4. Предположения и зависимости")
    add_body_p(
        doc,
        "Успешное функционирование поискового движка базируется на следующих системных предположениях и зависимостях:"
    )
    add_bullet_item(doc, "Аппаратная среда: ", "объем оперативной памяти рабочей станции должен быть достаточен для удержания инвертированного индекса и текста предложений (для текстовых корпусов объемом до 500 МБ требуется не менее 1 ГБ свободной RAM);")
    add_bullet_item(doc, "Программная среда: ", "наличие компилятора с поддержкой стандарта C++17 или новее (GCC 9+, Clang 10+, MSVC 2019+), поддержка стандартной библиотеки std::filesystem и локали UTF-8;")
    add_bullet_item(doc, "Кодировка данных: ", "все исходные индексируемые текстовые файлы должны быть сохранены в кодировке UTF-8 или ASCII;")
    add_bullet_item(doc, "Права доступа: ", "пользователь, запускающий приложение, должен обладать правами на чтение целевой директории и всех содержащихся в ней поддиректорий и файлов.")

    # -------------------------------------------------------------
    # РАЗДЕЛ 3. СПЕЦИФИКАЦИЯ ТРЕБОВАНИЙ
    # -------------------------------------------------------------
    add_h1(doc, "3. Спецификация требований", page_break_before=True)

    add_h2(doc, "3.1. Методология выявления и анализа требований")
    add_body_p(
        doc,
        "В рамках выполнения практического задания сбор и структурирование требований производились на основе признанной "
        "в промышленной программной инженерии методологии Карла Вигерса (Karl Wiegers). Согласно данной иерархической модели, "
        "требования декомпозируются на четыре последовательных и взаимоувязанных уровня:"
    )
    add_bullet_item(doc, "1. Бизнес-требования (Business Requirements): ", "определяют стратегические цели создания продукта, критерии рыночного или учебного успеха и основные ресурсные ограничения;")
    add_bullet_item(doc, "2. Пользовательские требования (User Requirements): ", "описывают цели и задачи, которые конечный пользователь может решать с помощью программной системы (в форме сценариев использования и прецедентов);")
    add_bullet_item(doc, "3. Функциональные требования (Functional Requirements): ", "детализируют конкретное поведение и логику программных модулей системы при выполнении пользовательских задач;")
    add_bullet_item(doc, "4. Нефункциональные требования (Non-Functional Requirements): ", "задают качественные атрибуты системы: архитектурные шаблоны, быстродействие, алгоритмическую сложность, надежность и поддержку стандартов локализации.")

    add_body_p(
        doc,
        "Дополнительно при формулировании требований применялся анализ предметной области (Domain Analysis) теории информационного "
        "поиска (Information Retrieval) и методы проектирования прецедентов (Use Case Analysis), позволившие точно разграничить зоны "
        "ответственности каждого программного компонента."
    )

    add_h2(doc, "3.2. Бизнес-требования (Business Requirements)")
    add_body_p(
        doc,
        "Бизнес-требования отражают базовую концепцию проекта и зафиксированы в таблице 2."
    )

    add_table_title(doc, "Таблица 2 — Спецификация бизнес-требований проекта")
    br_headers = ["Идентификатор", "Категория", "Формулировка требования", "Критерий приемки"]
    br_data = [
        ("BR-1", "Бизнес-цель", "Ускорение поиска информации по текстовым файлам, с исправлением опечаток.", "Существенное сокращение времени пользователя на поиск информации по текстовым архивам; моментальная локальная выдача релевантных совпадений и автоматическая коррекция опечаток в запросах на русском и английском языках."),
        ("BR-2", "Критерии успеха", "Получение рабочего консольного приложения, способного быстро обрабатывать текстовые файлы и находить релевантную информацию, экономя время пользователя на ручной поиск.", "Время ответа на поисковый запрос по массиву проиндексированных документов не превышает 50 миллисекунд."),
        ("BR-3", "Бизнес-ограничения", "Разработка ведется в рамках учебной дисциплины силами студентов. Требуется самостоятельная реализация ключевых алгоритмов (инвертированный индекс, расчет расстояния редактирования) на языке C++ без использования сторонних СУБД или готовых полнотекстовых движков.", "Отсутствие зависимостей от сторонних СУБД и сторонних поисковых библиотек. Чистая реализация на C++17/STL.")
    ]
    create_styled_table(doc, br_headers, br_data, [Cm(2.2), Cm(3.2), Cm(6.6), Cm(4.5)])

    add_h2(doc, "3.3. Пользовательские требования (User Requirements)")
    add_body_p(
        doc,
        "Пользовательские требования специфицируют функциональные ожидания пользователя от взаимодействия с системой "
        "через диалоговый терминал. Сценарий работы пользователя строится следующим образом: пользователь запускает программу, "
        "указывает путь к рабочей директории с файлами. Индексация не выполняется автоматически при старте — процесс "
        "индексирования запускается строго по явной команде пользователя rescan. В ходе дальнейшей работы при модификации "
        "содержимого директории (добавление новых файлов, изменение существующих или удаление файлов) пользователь "
        "повторно вводит команду rescan, запуская полную переиндексацию без необходимости перезапуска приложения."
    )
    add_body_p(
        doc,
        "В рамках модели взаимодействия формализованы пять ключевых путей пользователя (User Journeys):"
    )
    add_bullet_item(doc, "1-й путь пользователя (Поиск): ", "интерактивный ввод поисковых запросов в терминале (REPL-цикл) без перезапуска программы;")
    add_bullet_item(doc, "2-й путь пользователя (Автоисправление): ", "интеллектуальный поиск с автоисправлением опечаток на русском и английском языках;")
    add_bullet_item(doc, "3-й путь пользователя (Выдача): ", "получение ранжированных результатов по релевантности с абсолютными путями к файлам и превью-сниппетами;")
    add_bullet_item(doc, "4-й путь пользователя (Индексация): ", "указание пути к директории и запуск индексации/переиндексации по команде rescan с обязательной поддержкой добавления, изменения и удаления документов;")
    add_bullet_item(doc, "5-й путь пользователя (Завершение): ", "корректное освобождение ресурсов и выход из приложения по управляющей команде :q.")

    add_body_p(
        doc,
        "Спецификация требований пользователей с указанием приоритетов по методологии MoSCoW и сценариев использования "
        "представлена в таблице 3."
    )

    add_table_title(doc, "Таблица 3 — Спецификация пользовательских требований")
    ur_headers = ["ID", "Требование пользователя", "Приоритет (MoSCoW)", "Сценарий использования"]
    ur_data = [
        ("UR-1", "Пользователь должен иметь возможность непрерывно вводить поисковые запросы через интерактивную консоль (REPL) без необходимости перезапуска программы.", "Must Have", "После завершения поиска система выводит приглашение ко вводу следующего запроса."),
        ("UR-2", "Если пользователь допускает опечатку в запросе, он должен всё равно получать корректные результаты поиска по наиболее близкому исправленному слову.", "Must Have", "При вводе ошибочного терма система уведомляет: «Возможно, вы имели в виду: ...» и отображает результаты."),
        ("UR-3", "Пользователь должен получать список результатов, отсортированный по релевантности (по количеству совпадений).", "Must Have", "Документы с максимальной плотностью совпадений выводятся первыми в списке выдачи."),
        ("UR-4", "Пользователь должен иметь возможность указать путь к директории и вручную запустить индексацию по команде rescan. Система обязана поддерживать полную переиндексацию: удаление, добавление и изменение документов.", "Must Have", "Пользователь заходит в программу, указывает директорию и вводит команду rescan. Система актуализирует инвертированный индекс с учетом всех изменений."),
        ("UR-5", "Для понимания контекста найденного совпадения пользователь должен видеть в выдаче абсолютный путь к файлу и превью-сниппеты (до 3 предложений из текста документа).", "Should Have", "Для каждого документа отображаются путь и до 3 цитат с подсветкой или указанием контекста."),
        ("UR-6", "Пользователь должен иметь возможность корректно завершить работу приложения вводом управляющей команды (например, :q или exit).", "Must Have", "При вводе :q или exit ресурсы освобождаются, и процесс штатно завершается с кодом 0.")
    ]
    create_styled_table(doc, ur_headers, ur_data, [Cm(1.8), Cm(6.5), Cm(2.8), Cm(5.4)])

    add_h2(doc, "3.4. Функциональные требования (Functional Requirements)")
    add_body_p(
        doc,
        "Функциональные требования определяют поведение программных компонентов движка при обработке данных (таблица 4)."
    )

    add_table_title(doc, "Таблица 4 — Спецификация функциональных требований")
    fr_headers = ["ID", "Функция системы", "Детальное описание алгоритмического поведения", "Входные и выходные данные"]
    fr_data = [
        ("FR-1", "Сканирование файловой структуры по команде rescan", "Система осуществляет рекурсивный обход выбранного пользователем каталога с помощью std::filesystem::recursive_directory_iterator только по явной команде пользователя rescan, отбирая только регулярные файлы с расширением .txt и определяя добавленные, измененные и удаленные файлы.", "Вход: путь к каталогу, команда rescan.\nВыход: вектор путей к актуальным .txt файлам."),
        ("FR-2", "Лингвистическая предобработка текста", "Система разбивает сырой текст документов на предложения, очищает слова от знаков пунктуации, спецсимволов и цифр, выполняет перевод всех символов в нижний регистр (Case Folding) для кириллицы и латиницы.", "Вход: сырой текст файла.\nВыход: нормализованные токены и структурированные предложения."),
        ("FR-3", "Построение и перестроение инвертированного индекса", "Система строит инвертированный индекс в оперативной памяти (Term -> PostingList). При выполнении команды rescan система осуществляет полную переиндексацию: удаляет устаревшие записи удаленных файлов, индексирует новые и обновляет измененные документы.", "Вход: поток токенов документов.\nВыход: актуализированная структура InvertedIndex в RAM."),
        ("FR-4", "Поддержка REPL-цикла и управляющих команд", "Система поддерживает интерактивный цикл «чтение-вычисление-вывод», ожидая строковый ввод от пользователя, парсит введенную строку на команды (указание директории, команда rescan, выход :q) или поисковые термы.", "Вход: ввод из std::cin (команды или термы).\nВыход: передача управления модулю индексации, поиска или выхода."),
        ("FR-5", "Автоисправление опечаток", "При отсутствии терма в словаре индекса система активирует расчет расстояния Дамерау-Левенштейна между запросом и всеми словами словаря. Выбирается слово с минимальным расстоянием, не превышающим порог (<= 2).", "Вход: отсутствующий терм, словарь.\nВыход: исправленный терм-кандидат."),
        ("FR-6", "Ранжирование и формирование выдачи", "Система производит агрегацию вхождений найденных документов, сортирует массив совпадений по убыванию Term Frequency и извлекает до 3 предложений для каждого релевантного документа.", "Вход: PostingList совпадений.\nВыход: консольный отчет с путями и сниппетами.")
    ]
    create_styled_table(doc, fr_headers, fr_data, [Cm(1.8), Cm(3.8), Cm(6.5), Cm(4.4)])

    add_h2(doc, "3.5. Нефункциональные требования (Non-Functional Requirements)")
    add_body_p(
        doc,
        "Нефункциональные требования формулируют критерии качества программной реализации, ограничения производительности, "
        "надежности и архитектурные паттерны (таблица 5)."
    )

    add_table_title(doc, "Таблица 5 — Спецификация нефункциональных требований")
    nfr_headers = ["ID", "Категория", "Спецификация требования", "Механизм технической реализации"]
    nfr_data = [
        ("NFR-1", "Архитектура и качество кода (SOLID)", "Проектирование и реализация системы должны опираться на принципы объектно-ориентированного дизайна SOLID. Каждый класс имеет строго одну зону ответственности (SRP), интерфейсы изолированы.", "Разделение на независимые классы: SearchEngine, InvertedIndex, SpellChecker, DocumentStore, TextProcessor, REPL."),
        ("NFR-2", "Производительность индекса и переиндексации", "Инвертированный индекс обеспечивает поиск точного слова за время O(1) в среднем. Время ответа <= 50 мс.\nПроизводительность:\n- [ ] Полная переиндексация (удаление, добавление, изменение): модуль индексации по команде rescan гарантирует высокую скорость актуализации индекса без перезапуска приложения.", "Хэш-таблица std::unordered_map<std::wstring, PostingList> с эффективной хэш-функцией; быстрое обновление списков постингов и реестра DocumentStore."),
        ("NFR-3", "Алгоритмическая оптимизация памяти", "Алгоритм нечеткого сопоставления должен реализовывать метрику Дамерау-Левенштейна методом динамического программирования с экономией памяти O(min(M, N)).", "Использование двух строк рабочей матрицы размером min(M, N) вместо хранения всей двумерной таблицы M x N."),
        ("NFR-4", "Надежность и отказоустойчивость", "Система должна корректно игнорировать нетекстовые файлы, поврежденные кодировки, ошибки ввода несуществующих директорий и пустые поисковые строки без аварийного падения (Crash-free).", "Блоки try-catch, валидация путей через std::filesystem::exists, проверка регулярности файлов, информативные сообщения об ошибках."),
        ("NFR-5", "Локализация и кодировки", "Полная и корректная обработка кириллических и латинских символов во всех вычислительных модулях (чтение, токенизация, расчет расстояния редактирования).", "Применение широких строк std::wstring, перевод через std::wstring_convert и локаль ru_RU.UTF-8 (std::towlower, std::iswpunct).")
    ]
    create_styled_table(doc, nfr_headers, nfr_data, [Cm(1.8), Cm(3.2), Cm(6.2), Cm(5.3)])

    # -------------------------------------------------------------
    # РАЗДЕЛ 4. ДИАГРАММЫ UML
    # -------------------------------------------------------------
    add_h1(doc, "4. Архитектурные UML-диаграммы", page_break_before=True)
    add_body_p(
        doc,
        "В соответствии с заданием на практическое занятие, в данном разделе представлены три ключевые диаграммы "
        "унифицированного языка моделирования (UML 2.5), описывающие систему в трех различных проекциях: "
        "функциональной (Use Case Diagram), структурной (Class Diagram) и поведенческой во времени (Sequence Diagram)."
    )

    # 4.1. Use Case Diagram
    add_h2(doc, "4.1. Диаграмма вариантов использования (Use Case Diagram)")
    add_body_p(
        doc,
        "Диаграмма вариантов использования визуализирует границы проектируемой системы MySearchEngine, взаимодействующих "
        "с ней акторов и реализуемые прецеденты (рисунок 1). В системе выделены два актора:"
    )
    add_bullet_item(doc, "Пользователь (первичный актор): ", "студент, аналитик или разработчик, указывающий путь к директории, запускающий индексацию/переиндексацию по явной команде rescan (4-й путь пользователя), выполняющий поисковые запросы через интерактивную консоль и завершающий сеанс работы; ")
    add_bullet_item(doc, "Файловая система (вторичный актор / внешняя среда): ", "подсистема операционной системы, предоставляющая доступ к древовидной структуре файлов и текстовым потокам .txt.")

    add_figure(
        doc,
        f"{DIAGRAMS_DIR}/use_case_diagram.png",
        "Рисунок 1 — Диаграмма вариантов использования подсистемы MySearchEngine",
        width_cm=16.0
    )

    add_body_p(
        doc,
        "Диаграмма демонстрирует декомпозицию основных прецедентов с использованием стандартных отношений UML:"
    )
    add_bullet_item(doc, "Отношение включения «include»: ", "прецедент «Индексация / переиндексация по команде rescan» безусловно включает в себя шаги «Указать путь к директории», «Рекурсивное сканирование файлов .txt», «Предобработка текста» и «Построение / перестроение индекса в RAM» (с поддержкой удаления, добавления и изменения документов). Аналогично, прецедент «Ввод поискового запроса» включает «Ранжирование результатов» и «Формирование контекстных сниппетов»; ")
    add_bullet_item(doc, "Отношение расширения «extend»: ", "прецедент «Автоисправление опечатки» активируется только при выполнении условия расширения: запрашиваемый терм отсутствует в инвертированном индексе, что инициирует алгоритмический подбор ближайшего словарного аналога.")

    # 4.2. Class Diagram
    add_h2(doc, "4.2. Диаграмма классов (Class Diagram)", page_break_before=True)
    add_body_p(
        doc,
        "Диаграмма классов представляет статическую объектно-ориентированную структуру системы MySearchEngine, "
        "демонстрируя основные сущности, их атрибуты, методы, области видимости (+ public, - private) и межклассовые "
        "отношения (рисунок 2)."
    )

    add_figure(
        doc,
        f"{DIAGRAMS_DIR}/class_diagram.png",
        "Рисунок 2 — Диаграмма классов программной архитектуры поисковой системы",
        width_cm=10.2
    )

    add_body_p(
        doc,
        "Архитектура системы включает следующие ключевые классы и структуры данных:"
    )
    add_bullet_item(doc, "REPL (Presentation Layer): ", "управляет циклом взаимодействия с пользователем в терминале, считывает строки запросов и команд (путь, команда rescan, выход), вызывает методы движка SearchEngine и выводит форматированные отчеты выдачи; ")
    add_bullet_item(doc, "SearchEngine (Facade & Coordinator): ", "центральный фасад системы, координирующий работу хранилища документов, инвертированного индекса и модуля исправления опечаток. Реализует метод rescan() для полной переиндексации корпуса; ")
    add_bullet_item(doc, "DocumentStore: ", "хранилище нормализованных текстовых документов и их метаданных (DocumentMetadata). Отвечает за сопоставление DocID с физическим путем к файлу, выдачу предложений и операции добавления, модификации и удаления файлов при переиндексации; ")
    add_bullet_item(doc, "InvertedIndex: ", "высокопроизводительный ассоциативный индекс на базе std::unordered_map<std::wstring, PostingList>. Обеспечивает мгновенный доступ к постинг-листам по строковому ключу терма и удаление устаревших термов при переиндексации; ")
    add_bullet_item(doc, "PostingList и Posting: ", "структуры, содержащие списки идентификаторов документов (docId), частоту встречаемости терма (termFrequency) и список порядковых номеров предложений (sentenceIndices); ")
    add_bullet_item(doc, "SpellChecker: ", "сервисный класс, реализующий оптимизированный алгоритм расчета расстояния Дамерау-Левенштейна и подбор наиболее правдоподобных исправлений из словаря; ")
    add_bullet_item(doc, "TextProcessor: ", "статический утилитный класс (Utility Class), инкапсулирующий строковые алгоритмы разбиения на предложения, токенизации, фильтрации знаков препинания и конвертации между std::string (UTF-8) и std::wstring; ")
    add_bullet_item(doc, "SearchResult: ", "структура данных передачи результата (DTO), содержащая путь к документу, вычисленный ранг релевантности, сниппеты и флаг произведенного автоисправления.")

    # 4.3. Sequence Diagram
    add_h2(doc, "4.3. Диаграмма последовательности (Sequence Diagram)", page_break_before=True)
    add_body_p(
        doc,
        "Диаграмма последовательности детализирует динамику выполнения наиболее критического и сложного пользовательского "
        "сценария: «Обработка поискового запроса с нечетким поиском (исправлением опечатки), ранжированием и генерацией сниппетов» "
        "(рисунок 3)."
    )

    add_figure(
        doc,
        f"{DIAGRAMS_DIR}/sequence_diagram.png",
        "Рисунок 3 — Диаграмма последовательности обработки поискового запроса с автоисправлением",
        width_cm=10.5
    )

    add_body_p(
        doc,
        "Хронологическая последовательность обмена сообщениями между объектами включает 16 последовательных шагов:"
    )
    add_bullet_item(doc, "Шаги 1–2: ", "пользователь вводит в интерактивном терминале поисковый запрос со случайной опечаткой («програмирование»). Класс REPL считывает строку и инициирует вызов engine.search(\"програмирование\", 10); ")
    add_bullet_item(doc, "Шаги 3–4: ", "SearchEngine передает сырую строку в TextProcessor::normalize, где происходит приведение к нижнему регистру и конвертация в UTF-8/wstring; ")
    add_bullet_item(doc, "Шаги 5–6: ", "SearchEngine выполняет запрос index.lookup(L\"програмирование\"). Поскольку слово содержит опечатку, InvertedIndex возвращает nullptr (промах в индексе); ")
    add_bullet_item(doc, "Шаги 7–9: ", "SearchEngine обнаруживает промах и делегирует поиск ошибки классу SpellChecker, передавая ошибочный терм и словарь индекса index.getVocabulary(). SpellChecker циклически рассчитывает расстояние Дамерау-Левенштейна, находит ближайшего кандидата («программирование» с расстоянием 1) и возвращает его движку; ")
    add_bullet_item(doc, "Шаги 10–11: ", "SearchEngine повторно запрашивает инвертированный индекс с исправленным словом: index.lookup(L\"программирование\"). Индекс возвращает соответствующий PostingList с коллекцией документов и позициями; ")
    add_bullet_item(doc, "Шаг 12: ", "SearchEngine производит ранжирование документов по количеству найденных совпадений (Term Frequency Ranking); ")
    add_bullet_item(doc, "Шаги 13–14: ", "для документов, вошедших в итоговый топ выдачи, SearchEngine запрашивает у DocumentStore исходные предложения по сохраненным SentenceIdx и формирует контекстные превью (сниппеты); ")
    add_bullet_item(doc, "Шаги 15–16: ", "SearchEngine упаковывает сформированные SearchResult (включая уведомление о подстановке исправленного слова) и возвращает в REPL, который осуществляет форматированный вывод информации на терминал пользователя.")

    # -------------------------------------------------------------
    # РАЗДЕЛ 5. ЗАКЛЮЧЕНИЕ
    # -------------------------------------------------------------
    add_h1(doc, "5. Заключение", page_break_before=True)
    add_body_p(
        doc,
        "В ходе выполнения Практического занятия № 2 была успешно разработана исчерпывающая спецификация требований "
        "к программному обеспечению (SRS) для поисковой системы «MySearchEngine» на основе требований, собранных на "
        "предшествующем этапе проектирования."
    )
    add_body_p(
        doc,
        "В документе в строгом соответствии с академическими стандартами и методологией Карла Вигерса структурированы "
        "бизнес-требования, требования пользователей, функциональные и нефункциональные характеристики системы. "
        "Создан полный комплект архитектурных UML-диаграмм (Use Case Diagram, Class Diagram, Sequence Diagram), "
        "детализирующих функциональные прецеденты, внутреннюю статическую структуру объектно-ориентированных классов C++ "
        "и динамическое поведение компонентов при обработке поисковых запросов с исправлением опечаток."
    )
    add_body_p(
        doc,
        "Подготовленная документация служит надежной проектной основой для последующей кодогенерации, модульного тестирования "
        "и внедрения системы в рамках дисциплины «Технологии индустриального программирования»."
    )

    doc.save(DOCX_PATH)
    print(f"Document successfully created at: {DOCX_PATH}")

    # Convert to PDF using LibreOffice soffice
    soffice_cmd = ["/opt/homebrew/bin/soffice", "--headless", "--convert-to", "pdf", "--outdir", "/Users/rocke/prog/MySearchEngine", DOCX_PATH]
    res = subprocess.run(soffice_cmd, capture_output=True, text=True)
    if res.returncode == 0 and os.path.exists(PDF_PATH):
        print(f"PDF successfully compiled at: {PDF_PATH}")
    else:
        print(f"PDF compilation error: {res.stderr}")

if __name__ == "__main__":
    build_document()
