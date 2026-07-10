# -*- coding: utf-8 -*-
"""
Backend Engineer 4-Week Intensive Roadmap — PDF builder (reportlab)
Built incrementally: this file is appended to section-by-section, then
doc.multiBuild(story) is called once at the very end.
"""
import re
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.fonts import addMapping
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle,
    PageBreak, NextPageTemplate, ListFlowable, ListItem, HRFlowable, KeepTogether,
    CondPageBreak, FrameBreak
)
from reportlab.platypus.tableofcontents import TableOfContents

# ----------------------------------------------------------------------------
# FONTS  (DejaVu Sans -> full Unicode coverage: bullets, arrows, check marks)
# ----------------------------------------------------------------------------
FDIR = "/usr/share/fonts/truetype/dejavu/"
pdfmetrics.registerFont(TTFont("DejaVuSans", FDIR + "DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("DejaVuSans-Bold", FDIR + "DejaVuSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("DejaVuSans-Oblique", FDIR + "DejaVuSans-Oblique.ttf"))
pdfmetrics.registerFont(TTFont("DejaVuSans-BoldOblique", FDIR + "DejaVuSans-BoldOblique.ttf"))
addMapping("DejaVuSans", 0, 0, "DejaVuSans")
addMapping("DejaVuSans", 1, 0, "DejaVuSans-Bold")
addMapping("DejaVuSans", 0, 1, "DejaVuSans-Oblique")
addMapping("DejaVuSans", 1, 1, "DejaVuSans-BoldOblique")

pdfmetrics.registerFont(TTFont("DejaVuSansMono", FDIR + "DejaVuSansMono.ttf"))
pdfmetrics.registerFont(TTFont("DejaVuSansMono-Bold", FDIR + "DejaVuSansMono-Bold.ttf"))
addMapping("DejaVuSansMono", 0, 0, "DejaVuSansMono")
addMapping("DejaVuSansMono", 1, 0, "DejaVuSansMono-Bold")

# ----------------------------------------------------------------------------
# COLOR SYSTEM
# ----------------------------------------------------------------------------
NAVY      = colors.HexColor("#0B1220")
NAVY_2    = colors.HexColor("#121A2E")
INDIGO    = colors.HexColor("#4F46E5")
INDIGO_D  = colors.HexColor("#3730A3")
INDIGO_L  = colors.HexColor("#A5B4FC")
AMBER     = colors.HexColor("#B45309")
AMBER_BG  = colors.HexColor("#FFF7ED")
GREEN     = colors.HexColor("#047857")
GREEN_BG  = colors.HexColor("#ECFDF5")
RED       = colors.HexColor("#B91C1C")
RED_BG    = colors.HexColor("#FEF2F2")
INDIGO_BG = colors.HexColor("#EEF2FF")
GRAY_50   = colors.HexColor("#F8FAFC")
GRAY_100  = colors.HexColor("#F1F5F9")
GRAY_200  = colors.HexColor("#E2E8F0")
GRAY_300  = colors.HexColor("#CBD5E1")
GRAY_400  = colors.HexColor("#94A3B8")
GRAY_500  = colors.HexColor("#64748B")
GRAY_700  = colors.HexColor("#334155")
INK       = colors.HexColor("#1E293B")
WHITE     = colors.white

# ----------------------------------------------------------------------------
# PAGE GEOMETRY
# ----------------------------------------------------------------------------
PAGE_W, PAGE_H = A4
MARGIN_X   = 1.7 * cm
TOP_MARGIN = 2.0 * cm
BOT_MARGIN = 2.1 * cm
CONTENT_W  = PAGE_W - 2 * MARGIN_X

# ----------------------------------------------------------------------------
# TEXT HELPER — lightweight markdown -> reportlab XML markup
# ----------------------------------------------------------------------------
def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def md(text):
    t = esc(text)
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"`(.+?)`", r'<font face="DejaVuSansMono" color="#3730A3" size="8.6">\1</font>', t)
    t = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<i>\1</i>", t)
    return t

def code_escape(code_text):
    lines = code_text.strip("\n").split("\n")
    out = []
    for line in lines:
        stripped = line.lstrip(" ")
        n = len(line) - len(stripped)
        out.append("&nbsp;" * n + esc(stripped))
    return "<br/>".join(out)

# ----------------------------------------------------------------------------
# PARAGRAPH STYLES
# ----------------------------------------------------------------------------
ST = {}
ST["H1"] = ParagraphStyle("H1", fontName="DejaVuSans-Bold", fontSize=18.5, textColor=INDIGO_D,
                           spaceBefore=0, spaceAfter=13, leading=22)
ST["H2"] = ParagraphStyle("H2", fontName="DejaVuSans-Bold", fontSize=13.2, textColor=NAVY,
                           spaceBefore=15, spaceAfter=7, leading=16)
ST["H3"] = ParagraphStyle("H3", fontName="DejaVuSans-Bold", fontSize=10.8, textColor=INDIGO_D,
                           spaceBefore=10, spaceAfter=5, leading=13.5)
ST["Body"] = ParagraphStyle("Body", fontName="DejaVuSans", fontSize=9.6, textColor=INK,
                             leading=13.6, spaceAfter=6, alignment=TA_LEFT)
ST["BodyTight"] = ParagraphStyle("BodyTight", parent=ST["Body"], spaceAfter=2)
ST["Small"] = ParagraphStyle("Small", fontName="DejaVuSans", fontSize=8.2, textColor=GRAY_500, leading=11)
ST["SmallCenter"] = ParagraphStyle("SmallCenter", parent=ST["Small"], alignment=TA_CENTER)
ST["TableHead"] = ParagraphStyle("TableHead", fontName="DejaVuSans-Bold", fontSize=8.6, textColor=WHITE, leading=11)
ST["TableCell"] = ParagraphStyle("TableCell", fontName="DejaVuSans", fontSize=8.6, textColor=INK, leading=11.5)
ST["TableCellB"] = ParagraphStyle("TableCellB", fontName="DejaVuSans-Bold", fontSize=8.6, textColor=NAVY, leading=11.5)
ST["CalloutLabel"] = ParagraphStyle("CalloutLabel", fontName="DejaVuSans-Bold", fontSize=8.1, leading=10, spaceAfter=3)
ST["CalloutBody"] = ParagraphStyle("CalloutBody", fontName="DejaVuSans", fontSize=9.2, textColor=INK, leading=13)
ST["Code"] = ParagraphStyle("Code", fontName="DejaVuSansMono", fontSize=8.1, textColor=colors.HexColor("#E2E8F0"), leading=12)
ST["Kicker"] = ParagraphStyle("Kicker", fontName="DejaVuSans-Bold", fontSize=10, textColor=INDIGO_L, leading=13)
ST["CoverTitle"] = ParagraphStyle("CoverTitle", fontName="DejaVuSans-Bold", fontSize=33, textColor=WHITE, leading=37)
ST["CoverSub"] = ParagraphStyle("CoverSub", fontName="DejaVuSans", fontSize=13, textColor=GRAY_300, leading=18, spaceBefore=10)
ST["CoverFoot"] = ParagraphStyle("CoverFoot", fontName="DejaVuSans", fontSize=8.6, textColor=GRAY_400, leading=12)
ST["Tag"] = ParagraphStyle("Tag", fontName="DejaVuSans-Bold", fontSize=8, textColor=WHITE, alignment=TA_CENTER, leading=10)
ST["DayTitle"] = ParagraphStyle("DayTitle", fontName="DejaVuSans-Bold", fontSize=11, textColor=WHITE, leading=13)
ST["DayTime"] = ParagraphStyle("DayTime", fontName="DejaVuSans", fontSize=8, textColor=INDIGO_L, leading=10)
ST["WeekBanner"] = ParagraphStyle("WeekBanner", fontName="DejaVuSans-Bold", fontSize=10, textColor=INDIGO_L, leading=13)
ST["TOC1"] = ParagraphStyle("TOC1", fontName="DejaVuSans-Bold", fontSize=11.5, textColor=NAVY, leftIndent=0, spaceBefore=9, leading=15)
ST["TOC2"] = ParagraphStyle("TOC2", fontName="DejaVuSans", fontSize=9.4, textColor=GRAY_700, leftIndent=16, spaceBefore=3, leading=12.5)

# ----------------------------------------------------------------------------
# CONTENT HELPER FUNCTIONS
# ----------------------------------------------------------------------------
def h1(text):
    return Paragraph(md(text), ST["H1"])

def h2(text):
    return Paragraph(md(text), ST["H2"])

def h3(text):
    return Paragraph(md(text), ST["H3"])

def p(text, style="Body"):
    return Paragraph(md(text), ST[style])

def sp(height=8):
    return Spacer(1, height)

def divider(color=GRAY_200, thick=0.7, before=4, after=10):
    return HRFlowable(width="100%", thickness=thick, color=color, spaceBefore=before, spaceAfter=after)

def bullets(items, style="Body"):
    return ListFlowable(
        [ListItem(Paragraph(md(it), ST[style]), spaceAfter=3, bulletColor=INDIGO) for it in items],
        bulletType="bullet", start="circle", leftIndent=15, bulletFontSize=5.6,
    )

def numbered(items, style="Body"):
    return ListFlowable(
        [ListItem(Paragraph(md(it), ST[style]), spaceAfter=4) for it in items],
        bulletType="1", leftIndent=18, bulletColor=INDIGO_D,
        bulletFontName="DejaVuSans-Bold", bulletFontSize=9,
    )

def checklist(items):
    rows = [[" ", Paragraph(md(it), ST["Body"])] for it in items]
    t = Table(rows, colWidths=[15, CONTENT_W - 15])
    cmds = [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (0, -1), 1),
        ("LEFTPADDING", (1, 0), (1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ]
    for i in range(len(rows)):
        cmds.append(("BOX", (0, i), (0, i), 1.1, INDIGO))
        cmds.append(("TOPPADDING", (0, i), (0, i), 6))
    t.setStyle(TableStyle(cmds))
    return t

CALLOUTS = {
    "tip":      (INDIGO_BG, INDIGO_D, "TIP"),
    "note":     (GRAY_100,  GRAY_700, "NOTE"),
    "warning":  (AMBER_BG,  AMBER,    "WARNING"),
    "mistake":  (RED_BG,    RED,      "MISTAKE TO AVOID"),
    "interview":(GREEN_BG,  GREEN,    "INTERVIEW INSIGHT"),
}

def callout(kind, text, label=None):
    bg, accent, default_label = CALLOUTS[kind]
    lbl = label or default_label
    inner = [
        Paragraph(f'<font color="{accent.hexval()[2:] if hasattr(accent,"hexval") else ""}"><b>{esc(lbl)}</b></font>'
                  if False else f'<b>{esc(lbl)}</b>', ParagraphStyle("cl", parent=ST["CalloutLabel"], textColor=accent)),
        Paragraph(md(text), ST["CalloutBody"]),
    ]
    t = Table([[inner]], colWidths=[CONTENT_W])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg),
        ("LINEBEFORE", (0, 0), (0, -1), 3, accent),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
        ("LEFTPADDING", (0, 0), (-1, -1), 13),
        ("RIGHTPADDING", (0, 0), (-1, -1), 11),
    ]))
    return KeepTogether([sp(4), t, sp(4)])

def code_block(code_text):
    para = Paragraph(code_escape(code_text), ST["Code"])
    t = Table([[para]], colWidths=[CONTENT_W])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), NAVY),
        ("TOPPADDING", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
        ("LEFTPADDING", (0, 0), (-1, -1), 13),
        ("RIGHTPADDING", (0, 0), (-1, -1), 13),
    ]))
    return KeepTogether([sp(3), t, sp(6)])

def simple_table(headers, rows, col_widths=None, align_center_from=None):
    data = [[Paragraph(md(hd), ST["TableHead"]) for hd in headers]]
    for r in rows:
        data.append([Paragraph(md(str(c)), ST["TableCell"]) for c in r])
    if col_widths is None:
        col_widths = [CONTENT_W / len(headers)] * len(headers)
    t = Table(data, colWidths=col_widths, repeatRows=1)
    cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("LINEBELOW", (0, 0), (-1, -1), 0.5, GRAY_200),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, GRAY_50]),
    ]
    t.setStyle(TableStyle(cmds))
    return t

def day_card(day_label, title, time_estimate, tasks, extra_flowables=None):
    header_cell = Table(
        [[Paragraph(md(f"{day_label} &#8212; {title}"), ST["DayTitle"]),
          Paragraph(md(time_estimate), ST["DayTime"])]],
        colWidths=[CONTENT_W - 90, 90],
    )
    header_cell.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), INDIGO_D),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LEFTPADDING", (0, 0), (0, -1), 12),
        ("RIGHTPADDING", (1, 0), (1, -1), 12),
        ("ALIGN", (1, 0), (1, 0), "RIGHT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    task_flows = [checklist(tasks)]
    if extra_flowables:
        task_flows.extend(extra_flowables)
    body_cell = Table([[f] for f in task_flows], colWidths=[CONTENT_W - 24])
    body_cell.setStyle(TableStyle([
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
    ]))
    outer = Table([[header_cell], [body_cell]], colWidths=[CONTENT_W])
    outer.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 1, GRAY_300),
        ("TOPPADDING", (0, 1), (-1, 1), 10),
        ("BOTTOMPADDING", (0, 1), (-1, 1), 12),
        ("LEFTPADDING", (0, 1), (-1, 1), 12),
        ("RIGHTPADDING", (0, 1), (-1, 1), 12),
        ("TOPPADDING", (0, 0), (-1, 0), 0),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 0),
        ("LEFTPADDING", (0, 0), (-1, 0), 0),
        ("RIGHTPADDING", (0, 0), (-1, 0), 0),
    ]))
    return KeepTogether([outer, sp(12)])

def week_banner(week_no, title, goal):
    toc_title_style = ParagraphStyle("H1", fontName="DejaVuSans-Bold", fontSize=20, textColor=WHITE, leading=24, spaceBefore=3)
    inner = Table(
        [[Paragraph(md(f"WEEK {week_no}"), ST["WeekBanner"])],
         [Paragraph(md(f"Week {week_no}: {title}"), toc_title_style)],
         [Paragraph(md(f"**Goal:** {goal}"), ParagraphStyle("wg", fontName="DejaVuSans", fontSize=10, textColor=GRAY_300, leading=14, spaceBefore=6))]],
        colWidths=[CONTENT_W],
    )
    inner.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), NAVY),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 18),
        ("RIGHTPADDING", (0, 0), (-1, -1), 18),
        ("TOPPADDING", (0, 0), (-1, 0), 16),
        ("BOTTOMPADDING", (0, -1), (-1, -1), 16),
    ]))
    return KeepTogether([inner, sp(14)])

def tag_grid(items, per_row=4):
    rows = [items[i:i + per_row] for i in range(0, len(items), per_row)]
    col_w = CONTENT_W / per_row
    data, styles_cmds = [], []
    for row_i, row in enumerate(rows):
        cells = []
        for col_i in range(per_row):
            if col_i < len(row):
                cells.append(Paragraph(esc(row[col_i]), ST["Tag"]))
            else:
                cells.append("")
        data.append(cells)
    t = Table(data, colWidths=[col_w] * per_row)
    cmds = [
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]
    for r in range(len(data)):
        for c in range(per_row):
            cmds.append(("BACKGROUND", (c, r), (c, r), INDIGO_D if (r + c) % 2 == 0 else colors.HexColor("#312E81")))
    t.setStyle(TableStyle(cmds))
    return t

def section_break():
    return [NextPageTemplate("Content"), PageBreak()]

ST["QLabel"] = ParagraphStyle("QLabel", parent=ST["Body"], textColor=INDIGO_D, spaceAfter=3)
ST["ALabel"] = ParagraphStyle("ALabel", parent=ST["Body"], spaceAfter=3)
ST["ExDone"] = ParagraphStyle("ExDone", parent=ST["Body"], spaceAfter=9)

def qa(question, answer):
    q = Paragraph(f"<b>Q:</b> {md(question)}", ST["QLabel"])
    a = Paragraph(f"<b>A:</b> {md(answer)}", ST["ALabel"])
    return KeepTogether([q, a])

def mini_exercise(text):
    return callout("tip", text, label="MINI EXERCISE")

def motivation_note(week_no, text):
    return callout("interview", text, label=f"MOTIVATION — END OF WEEK {week_no}")

# ----------------------------------------------------------------------------
# PAGE TEMPLATES  (Cover = full-bleed navy, Content = normal page w/ footer)
# ----------------------------------------------------------------------------
DOC_TITLE = "Backend Engineer — 4-Week Intensive Roadmap"

def draw_cover(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(NAVY)
    canvas.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    canvas.setFillColor(INDIGO)
    canvas.rect(0, 0, 0.9 * cm, PAGE_H, fill=1, stroke=0)
    canvas.setFillColor(colors.HexColor("#312E81"))
    canvas.rect(PAGE_W - 0.35 * cm, 0, 0.35 * cm, PAGE_H, fill=1, stroke=0)
    canvas.restoreState()

def draw_content(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(GRAY_200)
    canvas.setLineWidth(0.6)
    canvas.line(MARGIN_X, BOT_MARGIN - 10, PAGE_W - MARGIN_X, BOT_MARGIN - 10)
    canvas.setFont("DejaVuSans", 7.6)
    canvas.setFillColor(GRAY_400)
    canvas.drawString(MARGIN_X, BOT_MARGIN - 22, DOC_TITLE)
    canvas.setFont("DejaVuSans-Bold", 8.5)
    canvas.setFillColor(GRAY_500)
    canvas.drawRightString(PAGE_W - MARGIN_X, BOT_MARGIN - 22, str(canvas.getPageNumber()))
    canvas.restoreState()

frame_cover = Frame(0, 0, PAGE_W, PAGE_H, id="cover",
                     leftPadding=2.4 * cm, rightPadding=1.9 * cm, topPadding=0, bottomPadding=0)
frame_content = Frame(MARGIN_X, BOT_MARGIN, CONTENT_W, PAGE_H - TOP_MARGIN - BOT_MARGIN, id="content")

class RoadmapDoc(BaseDocTemplate):
    def afterFlowable(self, flowable):
        if isinstance(flowable, Paragraph):
            style_name = flowable.style.name
            text = flowable.getPlainText()
            if style_name == "H1":
                self.notify("TOCEntry", (0, text, self.page))
            elif style_name == "H2":
                self.notify("TOCEntry", (1, text, self.page))

doc = RoadmapDoc(
    "/home/claude/roadmap_build/roadmap.pdf",
    pagesize=A4,
    title="Backend Engineer 4-Week Intensive Roadmap",
    author="Backend Engineering Mentor",
)
doc.addPageTemplates([
    PageTemplate(id="Cover", frames=[frame_cover], onPage=draw_cover),
    PageTemplate(id="Content", frames=[frame_content], onPage=draw_content),
])

# ============================================================================
# STORY BUILD START
# ============================================================================
story = []

# ---- COVER PAGE -------------------------------------------------------------
story.append(sp(120))
story.append(Paragraph("TECHNICAL CAREER PLAYBOOK", ST["Kicker"]))
story.append(sp(14))
story.append(Paragraph("Backend Engineer", ST["CoverTitle"]))
story.append(Paragraph("4-Week Intensive Roadmap", ST["CoverTitle"]))
story.append(Paragraph("From Personal Project to Job-Ready Backend Developer", ST["CoverSub"]))
story.append(sp(26))
line_tbl = Table([[""]], colWidths=[3.2 * cm], rowHeights=[2.6])
line_tbl.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), INDIGO_L)]))
story.append(line_tbl)
story.append(sp(26))
story.append(tag_grid([
    "Python", "Django", "DRF", "PostgreSQL",
    "Docker", "Redis", "Celery", "Nginx",
    "REST APIs", "JWT & OTP Auth", "WebSockets", "CI/CD (GitHub Actions)",
], per_row=4))
story.append(sp(300))
story.append(Paragraph("A 4-week, day-by-day plan covering production readiness, backend &amp; "
                        "system-design interview mastery, data structures &amp; security, and a complete "
                        "job-application system &#8212; built for developers who already ship real projects "
                        "and are ready to convert that experience into a job offer.", ST["CoverFoot"]))
story.append(sp(10))
story.append(Paragraph("2026 Edition", ST["CoverFoot"]))

story.extend(section_break())

# ---- TABLE OF CONTENTS -------------------------------------------------------
story.append(h1("Table of Contents"))
toc = TableOfContents()
toc.levelStyles = [ST["TOC1"], ST["TOC2"]]
story.append(toc)
story.extend(section_break())

# ---- HOW TO USE THIS ROADMAP -------------------------------------------------
story.append(h1("How to Use This Roadmap"))
story.append(p(
    "You already know how to **build** backend systems — Django, DRF, PostgreSQL, Docker, "
    "Redis, Celery, Nginx, JWT/OTP auth, REST APIs and WebSockets are already in your hands. "
    "This roadmap does not teach you a new framework. It converts what you can already build "
    "into what a hiring company can verify, trust, and pay for."
))
story.append(p(
    "Every week has a single job to do. Do not skip ahead — each week is a prerequisite for the next."
))
story.append(simple_table(
    ["Week", "Mission", "Output by Sunday night"],
    [
        ["1", "Make your existing project production-grade", "A deployable, monitored, secure project you can defend line by line"],
        ["2", "Master the backend interview", "Deep, correct answers for the questions that filter 80% of candidates"],
        ["3", "Coding interview + security mindset", "Comfort with DSA patterns and an attacker's view of your own code"],
        ["4", "Become job-ready and start applying", "Polished resume, GitHub, portfolio, and 5+ applications submitted daily"],
    ],
    col_widths=[2.2 * cm, 7.3 * cm, CONTENT_W - 2.2 * cm - 7.3 * cm],
))
story.append(sp(4))
story.append(h3("Daily Rhythm"))
story.append(p("Each day is built to fit around a job or full course load:"))
story.append(bullets([
    "**Core block (2–3h):** the day's main technical task — hands-on, applied to your own project",
    "**Study block (1–1.5h):** interview questions, reading, or deliberate practice",
    "**Review (10–15 min):** tick the daily checklist before you close your laptop",
]))
story.append(callout("tip",
    "If a day takes longer than planned, protect the **Core block** first. Study blocks can spill "
    "into the weekend — a working, production-grade project is worth more in an interview than "
    "one extra afternoon of reading."))
story.append(h3("How Each Week Is Structured"))
story.append(bullets([
    "**Daily tasks** — what to actually do, in order",
    "**Tables & checklists** — the reference material you will reuse in Week 4 and beyond",
    "**Common Mistakes** — the exact mistakes that make candidates look junior",
    "**End-of-week checklist** — the gate you must pass before moving on",
]))
story.append(callout("note",
    "Wherever an example is needed, this roadmap uses Django + DRF, PostgreSQL, Redis, Celery and "
    "Nginx — the exact stack you already work in — instead of generic pseudo-code."))

story.extend(section_break())

# ============================================================================
# WEEK 1 — PRODUCTION READINESS
# ============================================================================
story.append(week_banner(1, "Production Readiness",
    "Turn the project you already built into something you can deploy, monitor, secure, "
    "and defend line-by-line in an interview."))

story.append(p(
    "A working project on your laptop and a **production-ready** project are different things. "
    "The gap between them is exactly what separates a junior candidate from someone a team can "
    "trust with real users. This week closes that gap, one concern at a time."
))
story.append(divider())

# --- DAY 1 -------------------------------------------------------------------
story.append(day_card("DAY 1", "Environment Variables & Secrets Management", "~3 hrs", [
    "List every secret currently hardcoded in `settings.py` (SECRET_KEY, DB password, email password, API keys)",
    "Install `django-environ` (or `python-decouple`) and move every secret into environment variables",
    "Create a `.env.example` with placeholder values only, and commit that file",
    "Confirm `.env` is in `.gitignore`, then scan git history for previously committed secrets",
    "Rotate any secret that was ever committed, even in an old commit",
]))
story.append(h3("Why this matters"))
story.append(p(
    "A hardcoded `SECRET_KEY` is not a style issue — Django uses it to sign sessions, password-reset "
    "tokens, and CSRF tokens. Anyone who reads it from your repository can **forge a valid session "
    "for any user**, including staff accounts. A leaked database password is a full data breach, "
    "not a bug."
))
story.append(callout("mistake",
    "Deleting a `.env` file from the latest commit does **not** remove it from git history. "
    "`git log --all --full-history -- .env` will still show it. Use `git filter-repo` or "
    "`bfg-repo-cleaner` to purge it, then rotate the secret anyway — assume it is already compromised."))
story.append(code_block('''
# settings/base.py
import environ

env = environ.Env()
environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("DJANGO_SECRET_KEY")
DEBUG = env.bool("DEBUG", default=False)

DATABASES = {
    "default": env.db("DATABASE_URL"),
}
'''))
story.append(callout("tip",
    "Use a **different** `SECRET_KEY` per environment (dev / staging / prod). If one environment "
    "is compromised, the others stay safe — this is the same principle as not reusing passwords."))

# --- DAY 2 -------------------------------------------------------------------
story.append(day_card("DAY 2", "Logging & Structured Error Handling", "~3.5 hrs", [
    "Configure Django's `LOGGING` dict with console + rotating file handlers",
    "Write a custom DRF exception handler returning one consistent JSON error shape",
    "Replace bare `except Exception:` blocks with specific exceptions plus `logger.exception(...)`",
    "Add Sentry (or an equivalent error tracker) — production settings only",
    "Verify no logger ever prints a password, token, or OTP in plaintext",
]))
story.append(h3("The internal mechanism: Python's logging hierarchy"))
story.append(p(
    "Every `logging.getLogger(name)` call returns a logger positioned in a **tree** based on dotted "
    "name (`myapp.orders` is a child of `myapp`). A log record walks up that tree through every "
    "ancestor's handlers unless `propagate = False` is set. This is why a misconfigured root logger "
    "silently swallows — or duplicates — logs from every app in the project."
))
story.append(simple_table(
    ["Level", "Use it for", "Example"],
    [
        ["DEBUG", "Local diagnostics only, never enabled in prod", "Raw SQL params, cache hit/miss"],
        ["INFO", "Expected business events", "\"Order #4021 created\", \"OTP sent\""],
        ["WARNING", "Recoverable, needs attention", "Retry succeeded after 1 failure"],
        ["ERROR", "A request failed for the user", "Payment gateway timeout"],
        ["CRITICAL", "The system itself is at risk", "Database connection pool exhausted"],
    ],
    col_widths=[2.6*cm, 6.4*cm, CONTENT_W - 2.6*cm - 6.4*cm],
))
story.append(code_block('''
def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None:
        response.data = {
            "error": {
                "code": response.status_code,
                "message": str(exc),
            }
        }
    return response
'''))
story.append(callout("mistake",
    "Logging the full request body \"for debugging\" in production. If that endpoint ever accepts a "
    "password, OTP, or card number, it is now sitting in plaintext log files — often shipped to a "
    "third-party log aggregator outside your control."))

# --- DAY 3 -------------------------------------------------------------------
story.append(day_card("DAY 3", "Health Checks & Dependency Monitoring", "~2.5 hrs", [
    "Build a `/health/live/` endpoint that only confirms the process is running",
    "Build a `/health/ready/` endpoint that pings PostgreSQL, Redis, and a Celery worker",
    "Wire `docker-compose` healthchecks to the readiness endpoint, not the liveness one",
    "Add an uptime monitor (even a free one) pointed at the readiness endpoint",
]))
story.append(h3("Liveness vs. Readiness — why one endpoint is not enough"))
story.append(p(
    "**Liveness** answers \"is the process alive?\" — used to decide whether to restart a container. "
    "**Readiness** answers \"can this instance actually serve traffic right now?\" — used to decide "
    "whether to route requests to it. Returning `HttpResponse(\"OK\")` for both is a classic mistake: "
    "if the database is down, a liveness-only check keeps restarting a perfectly healthy container "
    "while the real problem — the database — goes unnoticed."
))
story.append(code_block('''
def readiness(request):
    checks = {"database": False, "redis": False}
    try:
        connection.ensure_connection()
        checks["database"] = True
    except OperationalError:
        pass
    try:
        cache.set("healthcheck", "1", timeout=5)
        checks["redis"] = cache.get("healthcheck") == "1"
    except Exception:
        pass
    healthy = all(checks.values())
    return JsonResponse(checks, status=200 if healthy else 503)
'''))
story.append(callout("note",
    "You already fixed `depends_on` race conditions between Nginx and Daphne — this is the same "
    "idea applied one layer deeper: `depends_on: condition: service_healthy` only works if the "
    "healthcheck it points to actually reflects readiness, not just \"the process started\"."))

# --- DAY 4 -------------------------------------------------------------------
story.append(day_card("DAY 4", "Docker & Docker Compose — Production Audit", "~3.5 hrs", [
    "Confirm every container runs as a non-root `USER`, never root",
    "Order Dockerfile layers so `COPY requirements.txt` happens before `COPY . .` (cache efficiency)",
    "Verify `.dockerignore` excludes `.git`, `.env`, `__pycache__`, and test artifacts",
    "Set `mem_limit` / `cpus` per service in `docker-compose.prod.yml`",
    "Confirm Trivy in CI gates the build on HIGH/CRITICAL findings, not just reports them",
    "Use named volumes for PostgreSQL data — never rely on the container's writable layer",
]))
story.append(h3("Auditing what you already built"))
story.append(p(
    "You already solved the hard version of this problem — a multi-stage build with a distroless "
    "runtime image and a portable virtualenv to bridge the glibc/Wolfi gap. Day 4 is not about "
    "rebuilding that; it is the **audit pass** a senior engineer runs before sign-off: non-root user, "
    "minimal attack surface, no secrets baked into any layer, and healthchecks wired to something real."
))
story.append(code_block('''
# docker-compose.prod.yml (excerpt)
services:
  web:
    image: fooddelivery-backend:latest
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health/ready/"]
      interval: 30s
      timeout: 5s
      retries: 3
    mem_limit: 512m
    cpus: "0.75"
'''))
story.append(callout("mistake",
    "Baking a secret into an image with a build-time `ARG` or `ENV`. Even if the final Dockerfile "
    "stage does not reference it, it can remain recoverable in intermediate build cache layers. "
    "Secrets belong in the **runtime environment**, never in the image."))

# --- DAY 5 -------------------------------------------------------------------
story.append(day_card("DAY 5", "Nginx Production Hardening", "~3 hrs", [
    "Add security headers: `X-Frame-Options`, `X-Content-Type-Options`, `Referrer-Policy`, `Strict-Transport-Security`",
    "Enable gzip (or brotli) compression for text-based responses",
    "Add `limit_req_zone` rate limiting on the login and OTP endpoints specifically",
    "Set `Cache-Control` headers on static/media files with versioned filenames",
    "For the WebSocket/Daphne upstream: correct `proxy_read_timeout` and the `Upgrade`/`Connection` headers",
]))
story.append(simple_table(
    ["Header", "Protects against"],
    [
        ["`X-Frame-Options: DENY`", "Clickjacking via `<iframe>` embedding"],
        ["`X-Content-Type-Options: nosniff`", "MIME-sniffing attacks on uploaded files"],
        ["`Strict-Transport-Security`", "Protocol downgrade / SSL-stripping attacks"],
        ["`Content-Security-Policy`", "Reflected & stored XSS payload execution"],
        ["`Referrer-Policy: strict-origin-when-cross-origin`", "Leaking full URLs (with tokens) to third parties"],
    ],
    col_widths=[7.2*cm, CONTENT_W - 7.2*cm],
))
story.append(code_block('''
limit_req_zone $binary_remote_addr zone=login_limit:10m rate=5r/m;

location /api/auth/login/ {
    limit_req zone=login_limit burst=3 nodelay;
    proxy_pass http://django_backend;
}

location /ws/ {
    proxy_pass http://daphne_backend;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_read_timeout 3600s;
}
'''))
story.append(callout("tip",
    "Rate-limit by **endpoint**, not globally. A global limit either blocks legitimate heavy browsing "
    "or is too loose to stop OTP/login brute-forcing — the two have completely different traffic shapes."))

# --- DAY 6 -------------------------------------------------------------------
story.append(day_card("DAY 6", "CI/CD & Code Quality Gates", "~3 hrs", [
    "Tighten Ruff rules (`E`, `F`, `I`, `UP`, `B`, `SIM`) and fail the pipeline on any violation",
    "Add pre-commit hooks so lint failures never reach a pushed commit",
    "Add a coverage gate — fail the build if coverage drops below an agreed threshold (e.g. 80%)",
    "Protect `main`: require passing CI + at least one review before merge",
    "Tag releases with semantic versioning (`v1.4.0`) instead of deploying arbitrary commits",
]))
story.append(code_block('''
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.6.9
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
'''))
story.append(callout("interview",
    "\"Why do you gate on coverage **and** lint, instead of just running tests?\" — a strong answer: "
    "tests catch broken behavior, lint catches drift in style and latent bugs (unused imports, "
    "shadowed variables), and a coverage gate stops the test suite itself from silently rotting "
    "as new code ships without tests."))

# --- DAY 7 -------------------------------------------------------------------
story.append(day_card("DAY 7", "Testing Hardening + Full Week Review", "~4 hrs", [
    "Confirm test settings use in-memory SQLite, `locmem` cache, and eager Celery execution",
    "Fix any shared-state test bleed (e.g. throttle caches persisting between test methods)",
    "Run the full suite twice in a row locally — a flaky test that passes once is not a passing test",
    "Deploy the current build to a staging-like `docker-compose` stack end-to-end",
    "Walk through every Day 1–6 item once more against the running staging stack",
]))
story.append(callout("note",
    "You already found this exact bug: `AnonRateThrottle`'s cache persisting across test methods "
    "and silently failing unrelated tests. The general lesson generalizes far beyond throttling — "
    "**any** shared mutable state (cache, module-level globals, class attributes) is a test-isolation "
    "risk. Default to clearing it in `setUp`/`tearDown` unless you have a specific reason not to."))

story.append(sp(4))
story.append(h2("End-of-Week 1 Checklist"))
story.append(checklist([
    "No secret, key, or password exists anywhere in source code or git history",
    "Structured logging is in place with a consistent DRF error response shape",
    "`/health/ready/` genuinely checks PostgreSQL and Redis, not just process liveness",
    "Docker images run as non-root, pass Trivy scanning, and have resource limits set",
    "Nginx serves security headers, rate-limits sensitive endpoints, and handles WebSocket upgrades",
    "CI blocks merges on lint failures, test failures, and coverage regressions",
    "The full test suite passes twice in a row with zero flaky failures",
    "A staging deployment was run end-to-end using the production Docker Compose stack",
]))

story.append(h2("Common Mistakes This Week"))
story.append(simple_table(
    ["Mistake", "Real-world impact"],
    [
        ["Reusing the dev `SECRET_KEY` in production", "One leaked environment compromises every environment"],
        ["Logging full request/response bodies", "Passwords, OTPs, and tokens end up in plaintext log storage"],
        ["Health check only pings the app process", "Orchestrator keeps a broken instance \"alive\" while users see errors"],
        ["Running containers as root", "A single RCE in the app becomes root-level container compromise"],
        ["No rate limit on login/OTP endpoints", "Trivial credential-stuffing or OTP brute-force at scale"],
    ],
    col_widths=[7.4*cm, CONTENT_W - 7.4*cm],
))

story.append(h2("Expected Outcome"))
story.append(p(
    "By Sunday night, your project should be something you could deploy to a real server today "
    "without embarrassment: no secret exposure, meaningful logs, honest health checks, hardened "
    "containers, a hardened reverse proxy, and a CI pipeline that actually blocks bad code. This is "
    "also, not coincidentally, the exact list a senior engineer mentally checks during your first "
    "code review at a new job."
))
story.append(motivation_note(1,
    "Production readiness is invisible when done right — nobody thanks you for the outage that "
    "never happened. That invisibility is the whole point. You just did a week of work that "
    "most junior developers never learn to do at all."))

story.extend(section_break())

# ============================================================================
# WEEK 2 — BACKEND INTERVIEW MASTERY
# ============================================================================
story.append(week_banner(2, "Backend Interview Mastery",
    "Build deep, correct answers for the questions that filter most candidates before a system-design "
    "round is even reached."))

story.append(p(
    "This week is not memorization. Every answer below explains the **mechanism** first — because "
    "an interviewer who asks one follow-up question can tell instantly whether you memorized an "
    "answer or actually understand it."
))
story.append(divider())

# --- DAY 8: PYTHON DEEP DIVE --------------------------------------------------
story.append(h2("Day 8 — Python Deep Dive"))
story.append(p("Focus: **memory management, decorators, generators, context managers, the GIL.**"))

story.append(h3("Memory Management"))
story.append(p(
    "CPython manages memory with two mechanisms working together. **Reference counting** is the "
    "primary one: every object carries a counter of how many references point to it; when it hits "
    "zero, the object is freed immediately. This is deterministic — no separate GC pause needed for "
    "most objects. The problem is **reference cycles** (`a.ref = b; b.ref = a`), where two objects "
    "reference each other but nothing external references either — the count never reaches zero. "
    "The **cyclic garbage collector** exists specifically to find and break these cycles, running "
    "periodically across three generations (younger objects are checked more often, on the "
    "assumption that most objects die young)."
))
story.append(qa(
    "Why can a Python object be freed the instant you do `del obj`, but sometimes it isn't?",
    "`del` only removes *that* reference and decrements the refcount. If it was the last reference, "
    "the object's `__del__` runs immediately and memory is reclaimed right away — that's reference "
    "counting. If the object participates in a reference cycle, the refcount never reaches zero from "
    "`del` alone, and it survives until the cyclic collector runs."
))
story.append(mini_exercise(
    "Create two objects that reference each other, `del` both external names, then call "
    "`gc.collect()` and print `gc.garbage` before and after to see the cycle actually get collected."))

story.append(h3("Decorators"))
story.append(p(
    "A decorator is just a function that takes a function and returns a (usually wrapped) function. "
    "`@my_decorator` above `def view(...):` is syntactic sugar for `view = my_decorator(view)`. The "
    "wrapper works because of **closures** — the inner function keeps a reference to variables from "
    "the enclosing scope even after that scope has returned. `functools.wraps` matters because "
    "without it, the wrapped function loses its original `__name__` and `__doc__`, which silently "
    "breaks introspection-based tools (admin registration, API schema generation, debuggers)."
))
story.append(code_block('''
def log_calls(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger.info("calling %s", func.__name__)
        return func(*args, **kwargs)
    return wrapper
'''))
story.append(qa(
    "What actually breaks if you forget `@functools.wraps(func)` in a decorator?",
    "`view.__name__` becomes `\"wrapper\"` for every decorated view. DRF's schema generation, "
    "Django's URL debug page, and any tool that inspects `__name__`/`__doc__` for identification "
    "will report the wrong thing — this has caused real, confusing bugs in generated API docs."
))

story.append(h3("Generators"))
story.append(p(
    "A function containing `yield` doesn't run when called — it returns a generator object "
    "immediately. Execution only happens on each `next()` call, pausing exactly at the `yield` and "
    "resuming from there next time. This is **lazy evaluation**: a generator processing a million-row "
    "queryset holds one row in memory at a time instead of materializing a million-item list."
))
story.append(qa(
    "When would a generator be the wrong choice for a Django view?",
    "When you need `len()`, need to iterate the data more than once, or need random access by index "
    "— a generator is exhausted after one pass and doesn't support any of those. It shines for "
    "one-shot streaming (large CSV export, chunked API responses), not for data you'll reuse."
))

story.append(h3("Context Managers"))
story.append(p(
    "`with` relies on the **context manager protocol**: `__enter__` runs at the start, `__exit__` "
    "always runs at the end — even if an exception was raised inside the block. This guarantee is "
    "exactly why `transaction.atomic()` is a context manager: `__exit__` is where Django decides to "
    "commit or roll back, and it needs to run **regardless** of how the block exited."
))
story.append(code_block('''
class atomic:
    def __enter__(self):
        self.sid = transaction.savepoint()
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            transaction.savepoint_commit(self.sid)
        else:
            transaction.savepoint_rollback(self.sid)
'''))

story.append(h3("The GIL (Global Interpreter Lock)"))
story.append(p(
    "The GIL allows only one thread to execute Python bytecode at a time, even on a multi-core "
    "machine. It exists because CPython's memory management (that reference counting from earlier) "
    "is not thread-safe by default — the GIL is the simplest fix. The practical consequence: "
    "**threading helps with I/O-bound work** (the GIL is released during I/O waits) but **does "
    "nothing for CPU-bound work** — for that you need multiprocessing (separate memory, separate "
    "GIL per process) or push the CPU-heavy work to Celery workers."
))
story.append(simple_table(
    ["Workload", "Best tool", "Why"],
    [
        ["I/O-bound (API calls, DB queries)", "`asyncio` or threads", "GIL releases during I/O wait"],
        ["CPU-bound (image processing, ML inference)", "`multiprocessing` / Celery", "Each process has its own GIL"],
        ["Mixed (web request handling)", "Daphne/ASGI + Celery offload", "Keep the request cycle I/O-bound; offload CPU work"],
    ],
    col_widths=[6.4*cm, 4.6*cm, CONTENT_W - 6.4*cm - 4.6*cm],
))
story.append(callout("mistake",
    "\"I'll use threading to speed up this CPU-heavy report generation.\" Threading will not help — "
    "the GIL means only one thread runs Python bytecode at a time. This is one of the most common "
    "wrong answers in Python interviews."))

story.extend(section_break())

# --- DAY 9: DJANGO CORE + ORM -------------------------------------------------
story.append(h2("Day 9 — Django Core &amp; ORM Internals"))
story.append(p("Focus: **request/response cycle, middleware, signals, the ORM's laziness, N+1 queries.**"))

story.append(h3("The Request/Response Cycle"))
story.append(p(
    "A request enters through the WSGI/ASGI server, passes through the middleware stack **top to "
    "bottom** on the way in, hits URL resolution, then the view. The response passes back through "
    "the same middleware stack **bottom to top**. This ordering is exactly why `SecurityMiddleware` "
    "sits near the top (it needs to act before almost anything else) and why authentication "
    "middleware must run before any middleware that assumes `request.user` exists."
))
story.append(qa(
    "You added custom middleware that reads `request.user`, but it crashes with an `AttributeError`. "
    "What's the likely cause?",
    "Your middleware is listed **before** `AuthenticationMiddleware` in `MIDDLEWARE`. Order matters "
    "on the way in — middleware only sees what earlier middleware has already attached to the "
    "request."
))

story.append(h3("Signals — power and cost"))
story.append(p(
    "Signals (`post_save`, `pre_delete`, etc.) decouple side effects from the code that triggers "
    "them. The cost is **traceability**: a `save()` call can trigger logic that lives in a completely "
    "different file, with no import or call visible at the call site. Senior engineers use signals "
    "sparingly — often preferring an explicit service function called directly from the view, "
    "reserving signals for cross-cutting concerns (cache invalidation, audit logging) that genuinely "
    "belong outside the core business logic."
))
story.append(callout("mistake",
    "Putting core business logic inside a `post_save` signal (e.g. sending the order-confirmation "
    "email). It works — until someone bulk-updates orders with `.update()`, which bypasses `save()` "
    "and silently skips the signal entirely."))

story.append(h3("ORM Internals: Laziness and the N+1 Problem"))
story.append(p(
    "A `QuerySet` does not hit the database when created — it builds a query object and only "
    "executes on iteration, slicing with a step, `len()`, `list()`, or `bool()`. This laziness is "
    "what makes the **N+1 problem** so easy to introduce invisibly: looping over a queryset and "
    "accessing a related object inside the loop fires one additional query per iteration, and it "
    "looks completely normal in code review."
))
story.append(code_block('''
# N+1: one query for orders, then one query PER order for .customer
for order in Order.objects.all():
    print(order.customer.name)

# Fixed: one query total, joined
for order in Order.objects.select_related("customer"):
    print(order.customer.name)
'''))
story.append(qa(
    "When do you use `select_related` versus `prefetch_related`?",
    "`select_related` does a SQL `JOIN` and is for **forward** foreign-key/one-to-one relationships "
    "— one query total. `prefetch_related` runs a **second, separate** query and joins the results "
    "in Python — required for **reverse** foreign keys and many-to-many, where a single JOIN would "
    "multiply and duplicate the base rows."
))
story.append(mini_exercise(
    "Enable `django.db.backends` logging in a shell session, loop over a related field without "
    "`select_related`, and count the actual queries fired. Then add `select_related` and compare."))

story.extend(section_break())

# --- DAY 10: DRF + AUTH/PERMISSIONS ------------------------------------------
story.append(h2("Day 10 — DRF, Authentication &amp; Permissions"))
story.append(p("Focus: **serializer internals, ViewSets/routers, permission classes, auth classes, throttling.**"))

story.append(h3("Serializers: validation is a pipeline, not a single step"))
story.append(p(
    "`is_valid()` runs field-level validation first (`validate_<field>`), then object-level "
    "validation (`validate(self, data)`), collecting errors from *all* fields before raising — which "
    "is why a single bad request can return several field errors at once instead of stopping at the "
    "first one. `.save()` only runs after validation passes, calling `create()` or `update()` "
    "depending on whether an instance was passed to the serializer."
))
story.append(qa(
    "Why does `serializer.save()` sometimes silently ignore a field you passed in `validated_data`?",
    "Usually because the field is declared `read_only=True`, or was never declared on the serializer "
    "at all — DRF drops unknown incoming keys during validation rather than raising, unless you "
    "explicitly forbid unknown fields."
))

story.append(h3("Authentication vs. Permissions — a two-step gate"))
story.append(p(
    "These solve two different questions. **Authentication** answers \"who is this?\" (Session, "
    "Token, JWT). **Permissions** answer \"is this identified user allowed to do this?\" "
    "(`IsAuthenticated`, `IsAdminUser`, custom object-level checks). DRF always runs authentication "
    "first for every request; permissions are then checked against whatever authentication produced "
    "— including the deliberate case of an **anonymous** user, which still has to pass through "
    "permission checks."
))
story.append(simple_table(
    ["Auth method", "State", "Typical use"],
    [
        ["Session", "Server-side, cookie-based", "Browser-based apps, same-origin"],
        ["Token (DRF built-in)", "Server-side, header-based", "Simple mobile/API clients"],
        ["JWT", "Stateless, signed, header-based", "Distributed systems, microservices, mobile"],
    ],
    col_widths=[3.6*cm, 5.2*cm, CONTENT_W - 3.6*cm - 5.2*cm],
))
story.append(callout("mistake",
    "Checking `if request.user.is_staff` inside the view body instead of using a permission class. "
    "It works today, but the check silently disappears the moment someone adds a second view or a "
    "viewset action and forgets to copy the same `if`. Permission classes are enforced structurally; "
    "an inline `if` is enforced by memory."))

story.append(h3("Throttling: a different question again"))
story.append(p(
    "Throttling answers neither \"who\" nor \"allowed to do what\" — it answers \"how **often**\". "
    "`AnonRateThrottle` and `UserRateThrottle` key their cache by IP or user ID respectively; the "
    "rate window resets based on cache expiry, which is exactly why a throttle cache that isn't "
    "cleared between test runs produces confusing, order-dependent test failures."
))
story.append(qa(
    "A test passes in isolation but fails when run as part of the full suite. The endpoint under "
    "test uses `AnonRateThrottle`. What's the most likely cause?",
    "Throttle state lives in the cache backend and persists across test methods by default. An "
    "earlier test already \"used up\" the rate limit for that IP, so a later test gets a 429 instead "
    "of the expected 200/201. Fix: clear the cache in `setUp()`/`tearDown()`, or override the "
    "throttle rate in test settings."
))

story.append(sp(4))
story.append(h3("Week 2 So Far — Revision Checklist"))
story.append(checklist([
    "Can explain reference counting vs. the cyclic GC without notes",
    "Can write a decorator using `functools.wraps` from memory",
    "Can explain why threading doesn't speed up CPU-bound Python code",
    "Can name the exact ordering of middleware on request vs. response",
    "Can identify an N+1 query by reading a loop, not just by running a profiler",
    "Can explain the three separate questions: authentication, permission, throttling",
]))

story.extend(section_break())

# --- DAY 11: DATABASE DEEP DIVE ----------------------------------------------
story.append(h2("Day 11 — Database Deep Dive"))
story.append(p("Focus: **indexes, transactions &amp; isolation levels, SQL optimization, EXPLAIN ANALYZE.**"))

story.append(h3("Indexes: the mechanism, not just \"it makes it faster\""))
story.append(p(
    "A B-tree index is a sorted structure that lets PostgreSQL find a row in `O(log n)` instead of "
    "scanning every row (`O(n)`). The cost is not free: every `INSERT`/`UPDATE`/`DELETE` must also "
    "update every index on that table, and each index consumes disk space and cache memory. This is "
    "exactly why indexing every column \"just in case\" is a real anti-pattern, not a safe default — "
    "it slows every write to (maybe) speed up a read that never happens."
))
story.append(qa(
    "You added an index on `status`, but a query filtering on `status='pending'` still does a full "
    "table scan. Why?",
    "If `pending` rows are, say, 90% of the table, the query planner correctly decides a sequential "
    "scan is cheaper than jumping through an index for most of the table anyway. Indexes help most "
    "on **selective** columns — few matching rows relative to the table size."
))
story.append(code_block('''
EXPLAIN ANALYZE
SELECT * FROM orders WHERE customer_id = 42;

-- Look for:
--  Seq Scan  -> likely missing/unused index
--  Index Scan -> index is being used
--  actual time= ...  -> real execution cost, not estimate
'''))

story.append(h3("Transactions &amp; Isolation Levels"))
story.append(p(
    "**ACID** (Atomicity, Consistency, Isolation, Durability) is the contract a transaction makes. "
    "**Isolation level** decides how much one transaction can see of another's uncommitted or "
    "concurrently-committed changes. PostgreSQL defaults to **Read Committed** — each statement sees "
    "only data committed before that statement began, which prevents dirty reads but still allows "
    "**non-repeatable reads** (reading the same row twice in one transaction and getting different "
    "values, because another transaction committed in between)."
))
story.append(simple_table(
    ["Isolation level", "Prevents", "Still allows"],
    [
        ["Read Committed (Postgres default)", "Dirty reads", "Non-repeatable reads, phantom reads"],
        ["Repeatable Read", "Dirty + non-repeatable reads", "Phantom reads (mostly, via MVCC in Postgres)"],
        ["Serializable", "All of the above", "Nothing — enforced as if transactions ran one at a time"],
    ],
    col_widths=[5.6*cm, 4.6*cm, CONTENT_W - 5.6*cm - 4.6*cm],
))
story.append(callout("mistake",
    "Using `Model.objects.get()` then `save()` to decrement stock (\"read, check, write\") under "
    "concurrent requests. Two requests can both read stock=1, both pass the check, and both "
    "decrement — selling the same last item twice. Use `F('stock') - 1` at the database level, or "
    "`select_for_update()` inside `transaction.atomic()`, so the check-and-write is atomic."))

story.extend(section_break())

# --- DAY 12: REST API DESIGN + HTTP -------------------------------------------
story.append(h2("Day 12 — REST API Design &amp; HTTP"))
story.append(p("Focus: **status codes, idempotency, pagination, versioning, HTTP caching.**"))

story.append(h3("Status Codes: precision signals seniority"))
story.append(simple_table(
    ["Code", "Meaning", "Common misuse"],
    [
        ["200", "OK, with a body", "Used for a `DELETE` that returns nothing (`204` is correct)"],
        ["201", "Created, with the new resource", "Returning `200` after `POST` that created something"],
        ["204", "No Content — success, empty body", "Returning `200` with an empty `{}`"],
        ["400", "Client sent invalid data", "Used for \"not found\" or \"not authorized\""],
        ["401", "Not authenticated", "Confused with 403"],
        ["403", "Authenticated but not allowed", "Confused with 401"],
        ["409", "Conflict with current state", "Rarely used, often replaced with a generic 400"],
        ["422", "Semantically invalid (validation)", "Used interchangeably with 400 without a clear rule"],
    ],
    col_widths=[1.6*cm, 5.0*cm, CONTENT_W - 1.6*cm - 5.0*cm],
))
story.append(qa(
    "What is the practical difference between `401` and `403`, and why does mixing them up matter?",
    "`401 Unauthorized` means the server doesn't know who you are (missing/invalid credentials) — "
    "the correct client reaction is \"log in\". `403 Forbidden` means the server knows exactly who "
    "you are and refuses anyway — the correct reaction is \"don't retry with different credentials, "
    "this user can never do this.\" Returning `403` for an expired token sends clients into a "
    "confusing retry loop instead of re-authenticating."
))

story.append(h3("Idempotency"))
story.append(p(
    "An idempotent request produces the same end-state no matter how many times it's repeated. "
    "`GET`, `PUT`, and `DELETE` are supposed to be idempotent by definition — `POST` is not. This "
    "matters directly for retries: a mobile client on a flaky network safely retries a `PUT`, but "
    "blindly retrying a `POST` (e.g. \"create order\") can create duplicate orders unless you add an "
    "explicit idempotency key."
))
story.append(callout("tip",
    "For payment or order-creation endpoints, accept an `Idempotency-Key` header from the client and "
    "store the result keyed by it. A retried request with the same key returns the **original** "
    "result instead of creating a second order."))

story.append(h3("Pagination &amp; Versioning"))
story.append(p(
    "**Offset pagination** (`?page=3`) is simple but degrades on large tables — the database still "
    "has to count/skip the earlier rows. **Cursor pagination** (`?after=<id>`) uses an indexed "
    "column directly and stays fast regardless of how deep you paginate, at the cost of losing "
    "random page access. For **versioning**, URL versioning (`/api/v1/...`) is the most explicit and "
    "cache-friendly; header versioning is more \"RESTfully pure\" but harder to test by just visiting "
    "a URL in a browser."
))

story.extend(section_break())

# --- DAY 13: INFRA DEEP DIVE --------------------------------------------------
story.append(h2("Day 13 — Infrastructure Deep Dive"))
story.append(p("Focus: **Redis, Celery, Nginx, Docker, Linux, Git — the internals behind daily commands.**"))

story.append(h3("Redis: more than a cache"))
story.append(qa(
    "Why does Redis let you set a per-key TTL, and why does that matter for session storage?",
    "Redis is in-memory by design — everything stored costs RAM. A TTL means expired sessions, OTP "
    "codes, and rate-limit counters are reclaimed automatically instead of accumulating forever. "
    "Without it, a cache used for OTPs would need a separate cleanup job just to avoid an "
    "ever-growing memory footprint."
))
story.append(p(
    "Under memory pressure, Redis evicts keys according to the configured **eviction policy** "
    "(`allkeys-lru`, `volatile-lru`, `noeviction`, etc.). Using Redis for both a cache **and** as a "
    "Celery broker on the same instance with `noeviction` risks the broker's queue data being "
    "evicted under memory pressure exactly like it was disposable cache data — usually the wrong "
    "trade-off."
))

story.append(h3("Celery: the task queue's actual moving parts"))
story.append(p(
    "A `.delay()` call serializes the task and its arguments, pushes them onto the broker (Redis), "
    "and returns immediately — the **worker process** is a separate process that polls the broker "
    "and executes tasks. This separation is why a Celery task must be **idempotent-friendly**: the "
    "worker can crash mid-task and, depending on `acks_late` settings, redeliver the same task."
))
story.append(qa(
    "Your Celery task sends an order-confirmation email. Under what circumstance could a customer "
    "receive the email twice?",
    "If `task_acks_late=True` and the worker crashes **after** sending the email but **before** "
    "acknowledging the task, the broker redelivers it to another worker, which sends it again. Fix: "
    "make the task idempotent — e.g. check an `email_sent` flag on the order before sending, not "
    "just \"has this task run before.\""
))

story.append(h3("Nginx: reverse proxy vs. load balancer"))
story.append(p(
    "A **reverse proxy** sits in front of one or more backend servers and forwards client requests to "
    "them, hiding the backend's existence. A **load balancer** is a reverse proxy with an added job: "
    "distributing traffic across *multiple* backend instances using a strategy (round-robin, "
    "least-connections, ip-hash). Nginx's `upstream` block is literally both at once when you list "
    "more than one server."
))

story.append(h3("Docker, Linux, Git — rapid-fire internals"))
story.append(qa(
    "What actually makes a Docker image layer \"cached\"?",
    "Docker hashes each instruction plus its build context. If a `COPY` instruction's source files "
    "are byte-identical to the last build **and** every instruction before it was also a cache hit, "
    "that layer is reused instead of re-executed — which is exactly why `COPY requirements.txt` "
    "before `COPY . .` avoids reinstalling dependencies every time application code changes."
))
story.append(qa(
    "What is the real difference between `git merge` and `git rebase`?",
    "`merge` creates a new commit joining two histories, preserving exactly what happened and when — "
    "safe on shared branches. `rebase` rewrites commits onto a new base, producing a linear history "
    "but changing commit hashes — safe only on branches nobody else has already pulled, since "
    "rewritten history diverges from anyone else's copy."
))
story.append(callout("mistake",
    "Rebasing a branch that a teammate has already pulled and built on top of. Their next `pull` "
    "produces a confusing pile of duplicate commits, because their history and the rewritten history "
    "no longer share the same commit hashes."))

story.extend(section_break())

# --- DAY 14: ARCHITECTURE + BEHAVIORAL ----------------------------------------
story.append(h2("Day 14 — Architecture &amp; Behavioral Questions"))
story.append(p("Focus: **scaling a Django system, the STAR method, a full week revision pass.**"))

story.append(h3("System Design, at Django scale"))
story.append(p(
    "You don't need to design Twitter. You need to credibly answer: \"your Django app is getting "
    "slow under load — walk me through how you'd investigate and fix it.\" A strong answer moves "
    "through layers in order, not randomly:"
))
story.append(numbered([
    "**Measure first** — is it CPU, memory, DB, or network? Guessing before measuring is the #1 red flag",
    "**Database layer** — missing indexes, N+1 queries, connection pool exhaustion",
    "**Caching layer** — cache hot reads in Redis, with a clear invalidation strategy",
    "**Application layer** — move slow synchronous work (emails, PDF generation, notifications) into Celery",
    "**Horizontal scaling** — more Gunicorn/Daphne workers behind Nginx, only once the above is done",
]))
story.append(callout("interview",
    "Jumping straight to \"add more servers\" without mentioning measurement or the database layer "
    "reads as junior. Senior answers are boring and sequential: measure, fix the database, cache, "
    "then scale out."))

story.append(h3("Behavioral Questions — the STAR method"))
story.append(p(
    "**Situation, Task, Action, Result.** The most common failure is spending 80% of the answer on "
    "Situation and rushing Result. Interviewers remember Result and Action — lead with a one-sentence "
    "Situation, then spend most of the time on what **you** specifically did and what changed because "
    "of it."
))
story.append(qa(
    "\"Tell me about a bug that took you a long time to find.\"",
    "Pick something real, structure it in under 90 seconds: what the symptom was, what you tried "
    "that *didn't* work and why that was a reasonable thing to try, what the actual root cause turned "
    "out to be, and what you changed afterward (a test, a monitor, a process) so it can't silently "
    "recur. That last part — prevention, not just the fix — is what separates a senior answer."
))

story.append(sp(4))
story.append(h2("End-of-Week 2 Checklist"))
story.append(checklist([
    "Can answer every Day 8–14 question out loud, without reading the answer first",
    "Can explain N+1 queries, isolation levels, and idempotency to a non-technical friend simply",
    "Can walk through the 5-layer \"app is slow\" investigation without prompting",
    "Have 3 real STAR-formatted stories ready (a bug, a disagreement, a deadline under pressure)",
]))
story.append(h2("Common Mistakes This Week"))
story.append(simple_table(
    ["Mistake", "Why it costs you the interview"],
    [
        ["Memorized one-line answers with no mechanism", "One follow-up question exposes the gap immediately"],
        ["Confusing 401 and 403, or PUT and PATCH", "Signals imprecise REST knowledge, a very visible tell"],
        ["Jumping to \"add more servers\" first", "Skips measurement — reads as guessing, not engineering"],
        ["Rambling Situation, rushed Result in behavioral answers", "The part interviewers remember gets the least airtime"],
    ],
    col_widths=[7.4*cm, CONTENT_W - 7.4*cm],
))
story.append(motivation_note(2,
    "You now understand *why* the tools you already use behave the way they do — not just how to "
    "call them. That difference is exactly what a 45-minute interview is designed to detect."))

story.extend(section_break())

# ============================================================================
# WEEK 3 — DATA STRUCTURES, ALGORITHMS & SECURITY
# ============================================================================
story.append(week_banner(3, "Data Structures, Algorithms &amp; Security",
    "Build real comfort with the coding-interview patterns, and learn to read your own code the way "
    "an attacker would."))

story.append(p(
    "Two very different muscles, trained back to back on purpose: the coding round tests how you "
    "think under a time limit, and the security review tests how carefully you think when nobody is "
    "timing you. Both are judged in real interviews, often in the same interview loop."
))
story.append(divider())

# --- DAY 15: ARRAYS, STRINGS, COMPLEXITY --------------------------------------
story.append(day_card("DAY 15", "Arrays, Strings &amp; Complexity Analysis", "~3 hrs", [
    "Solve 3 array problems using the two-pointer pattern",
    "Solve 2 string problems using the sliding-window pattern",
    "For every solution, state its time and space complexity before checking the answer",
]))
story.append(h3("Time &amp; Space Complexity — reasoning, not memorized labels"))
story.append(p(
    "Big-O describes how work **grows** as input size grows — it is not a stopwatch measurement. A "
    "single nested loop over the same array is `O(n²)` regardless of how fast the inner line of code "
    "runs, because the number of operations scales with the square of `n`. This is exactly what "
    "interviewers probe when they ask you to \"optimize\" a brute-force solution: they want you to "
    "recognize repeated work, not just write faster code."
))
story.append(simple_table(
    ["Pattern", "When it applies", "Typical complexity win"],
    [
        ["Two pointers", "Sorted array, pair/triplet sum, reversing in place", "`O(n²)` &#8594; `O(n)`"],
        ["Sliding window", "Contiguous subarray/substring with a condition", "`O(n²)` &#8594; `O(n)`"],
        ["Hash map lookup", "\"Have I seen this before?\" style problems", "`O(n)` &#8594; `O(1)` per lookup"],
        ["Binary search", "Sorted data, or a monotonic answer space", "`O(n)` &#8594; `O(log n)`"],
    ],
    col_widths=[3.4*cm, 6.6*cm, CONTENT_W - 3.4*cm - 6.6*cm],
))
story.append(code_block('''
def two_sum_sorted(nums, target):
    left, right = 0, len(nums) - 1
    while left < right:
        total = nums[left] + nums[right]
        if total == target:
            return [left, right]
        elif total < target:
            left += 1
        else:
            right -= 1
    return []
'''))
story.append(callout("interview",
    "Say your complexity out loud **before** you're asked. \"This is O(n) time, O(1) space because "
    "I only move two pointers inward\" — volunteering this is one of the simplest ways to sound "
    "senior in a coding round."))

# --- DAY 16: HASH MAPS, STACKS, QUEUES ----------------------------------------
story.append(day_card("DAY 16", "Hash Maps, Stacks &amp; Queues", "~3 hrs", [
    "Solve 2 problems using a hash map for O(1) lookups",
    "Implement a valid-parentheses checker using a stack",
    "Implement a basic queue-based level-order traversal",
]))
story.append(h3("Why these aren't just \"textbook\" structures"))
story.append(p(
    "A **hash map** is the backbone of anything requiring \"have I seen this key before?\" — rate "
    "limiters, deduplication, caching layers all reduce to a hash map at their core. A **stack** "
    "(LIFO) mirrors the call stack itself — which is exactly why recursion and \"undo\" features are "
    "naturally stack-shaped. A **queue** (FIFO) mirrors a task queue like Celery's broker — first "
    "task in, first task out (ignoring priority queues for a moment)."
))
story.append(qa(
    "Why is a stack the right structure for validating balanced brackets, `((a+b)*c)`, instead of a "
    "counter?",
    "A counter can confirm the **count** of `(` matches `)`, but not the **order** — `)(` would "
    "incorrectly pass a counter-only check. A stack enforces order: push on `(`, and on `)` the top "
    "of the stack must be the matching open bracket, or the string is invalid."
))
story.append(code_block('''
def is_valid(s):
    stack = []
    pairs = {")": "(", "]": "[", "}": "{"}
    for ch in s:
        if ch in "([{":
            stack.append(ch)
        elif ch in ")]}":
            if not stack or stack.pop() != pairs[ch]:
                return False
    return not stack
'''))

# --- DAY 17: TREES, BINARY SEARCH, RECURSION ----------------------------------
story.append(day_card("DAY 17", "Trees, Binary Search &amp; Recursion", "~3.5 hrs", [
    "Implement recursive and iterative in-order tree traversal",
    "Solve 2 binary search problems, including one on an \"answer space\" rather than an array",
    "Solve 1 problem using DFS and 1 using BFS on a tree or grid",
]))
story.append(h3("Recursion: the mental model that actually helps"))
story.append(p(
    "A recursive solution needs exactly two things: a **base case** that stops the recursion, and a "
    "step that reduces the problem toward that base case. Trust the recursive call to correctly "
    "solve the smaller sub-problem — trying to mentally trace every level of a deep recursion during "
    "an interview is where people run out of time and confidence."
))
story.append(qa(
    "What's the real difference between DFS and BFS on a tree, in terms of memory used?",
    "DFS's memory cost is bounded by the **height** of the tree (the recursion stack). BFS's memory "
    "cost is bounded by the **width** of the tree (everything in the current level, held in a "
    "queue). On a wide, shallow tree, BFS uses far more memory than DFS at the same node count."
))
story.append(callout("tip",
    "Binary search isn't just \"for sorted arrays.\" It applies to **any monotonic answer space** — "
    "e.g. \"find the minimum capacity that lets all packages ship within D days\" is a classic "
    "binary-search-on-the-answer problem, not an array-search problem."))

# --- DAY 18: SORTING, SEARCHING, LEETCODE ROADMAP -----------------------------
story.append(day_card("DAY 18", "Sorting, Searching &amp; the Practice Roadmap", "~3 hrs", [
    "Be able to explain how merge sort and quick sort each achieve O(n log n)",
    "Know which built-in sort your language uses and its worst-case complexity",
    "Set up a tracked practice list for the remaining 3 weeks",
]))
story.append(simple_table(
    ["Algorithm", "Average", "Worst case", "Stable?"],
    [
        ["Merge sort", "O(n log n)", "O(n log n)", "Yes"],
        ["Quick sort", "O(n log n)", "O(n\u00b2)", "No"],
        ["Timsort (Python's `sorted()`)", "O(n log n)", "O(n log n)", "Yes"],
        ["Binary search", "O(log n)", "O(log n)", "n/a"],
    ],
    col_widths=[6.0*cm, 3.2*cm, 3.2*cm, CONTENT_W - 6.0*cm - 3.2*cm - 3.2*cm],
))
story.append(h3("A realistic practice roadmap, not \"grind 500 problems\""))
story.append(numbered([
    "**Weeks 3–4 (now):** ~40 problems covering arrays, strings, hash maps, stacks/queues, trees — "
    "pattern recognition over volume",
    "**Ongoing after this roadmap:** 3–5 problems a week, revisiting ones you struggled with after "
    "2 weeks — spaced repetition beats one-time grinding",
    "**Before an actual interview loop:** re-solve your \"hard for me\" list from memory, timed",
]))
story.append(callout("mistake",
    "Solving 300 random problems with no pattern tracking. Recognizing \"this is a sliding-window "
    "problem\" in 30 seconds is the actual interview skill — raw volume without pattern review "
    "trains the wrong thing."))

story.append(sp(4))
story.append(h3("DSA Mid-Week Checklist"))
story.append(checklist([
    "Can state a solution's time/space complexity without being asked",
    "Recognize two-pointer, sliding-window, and binary-search-on-answer patterns on sight",
    "Comfortable choosing between DFS and BFS based on the actual question being asked",
    "Have a tracked, revisited practice list — not just a growing \"solved\" count",
]))

story.extend(section_break())