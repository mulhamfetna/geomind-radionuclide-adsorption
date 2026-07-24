"""Build the corpus bibliography deliverables: an Excel table and a Vancouver-style DOCX.

Both list every source publication this study drew on, with authoritative metadata resolved
from Crossref by DOI, the publisher's own abstract where it is available, and an Arabic
translation of that abstract.

    python -m build_bibliography      # writes GEOMIND-R-bibliography.{xlsx,docx}

## Why some abstracts are absent, deliberately

Abstracts are included **only** where the publisher supplies them through Crossref, so that
every word in the "Abstract (original)" column is verbatim and attributable. Automated
extraction from PDF text was trialled and rejected: it produced at least one confirmed
wrong-paper match (a slag/Portland-cement abstract attached to a zeolite ion-exchange paper).
Shipping unverified text into a submission document would breach the project's rule that no
datum enters a deliverable unchecked against its primary source. Rows without a publisher
abstract carry the DOI instead, which resolves to the authoritative version.

## Copyright

Publisher abstracts are the copyright of their publishers. This compilation is prepared as a
working bibliography for the authors' own submission; it is **not** part of the public data
deposit. Each row records the licence Crossref reports, where one is declared.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parent
SCRATCH = Path("/tmp/claude-1000/-mnt-data-projects-boundless-lab-geobolimer/"
               "9b079964-e3b1-4247-8ca8-1d470949ca75/scratchpad/crossref.json")

#: What each source contributed, so a reader can see why it is in the corpus at all.
ROLE = {
    "geomind": "Reference work this project set out to replicate",
    "varon2025": "Forward-model training series (n=7): framework Al-IV vs Sr K_D",
    "varon_leached2026": "Within-sample causal test: leaching strips Al-IV and uptake falls",
    "oulu2026": "Designed Si/Al series with published Q4(mAl) deconvolution; ARI source",
    "walkley2020": "Atomic mechanism: Sr/Ca displace Na/K from Al-IV charge-balancing sites",
    "geddes2025": "Atomic mechanism: Sr imaged at Al-IV sites (EXAFS/NMR)",
    "vandevenne2018": "Designed Ca-Si-Al slag series; quantifies the Ca/Sr site competition",
    "jain2022": "Cs loading series; pollucite route to retention",
    "blackford2007": "TEM/NMR: Sr partitions to crystalline SrCO3 at waste loadings",
    "nevin2026": "Pool B: Cs/Sr leachability indices with NMR structure",
    "kim2026": "Pool B: Sr leachability with EXAFS coordination numbers",
    "jang2016": "Pool B: Cs and Sr leachability with pore structure",
    "kurumisawa2021": "Pool B: Cs ingress diffusivity",
    "komljenovic2020": "Pool B: Ca-system (C-A-S-H), quantitative confirmation of F19",
    "arbelhaddad2022": "Pool B: cumulative leached fraction, metakaolin framework",
    "stanojevic2025": "Pool B: Cs leachability, fly-ash geopolymer",
    "frederickx2025": "Pool B: real waste stream; accelerated-leachant caution",
    "katada2024": "Pool A: Na-zeolite Cs ion-exchange capacities",
    "baek2018": "Pool A: natural zeolites; source of a saturation-screen artefact",
    "tarnovsky2024": "Pool A: metakaolin geopolymers, Cs and Sr with BET",
    "xiang2021": "Pool A: geopolymer foams; BET falls while uptake rises",
    "zhang2021": "Pool A: alkali-activated fly-ash/slag geomaterials, Cs",
    "zheng2023": "Pool A: zeolite-rich geopolymer, Cs",
    "lei2021": "Pool A: Cs Freundlich / Sr Langmuir",
    "elnaggar2018": "Pool A: MKBFS systems (two rows quarantined by the audit)",
    "niu2022": "Pool A: ion-exchange log K only; no capacities (audit outcome)",
    "tian2019_espr": "Pool A: zeolite A from fly ash",
    "tian2019_wst": "Pool A: fly-ash geopolymer, Cs/Sr; values in the supplement",
    "lin2026": "Pool A: geopolymer granules, Cs/Sr in simulated seawater",
    "qian2001": "Pool A: Sr/Cs distribution coefficients",
    "petlitckaia2020": "Pool A: geopolymer foams, Cs",
    "nadol2026": "Context: base-element leaching + NMR; no radionuclide target",
    "hamed2025_magnetic": "Pool A: magnetic nanocomposite (audit correction)",
    "muracchioli2019": "Rejected: heavy-metal adsorption, out of scope",
    "weigelt2020": "Context: structural characterisation of Cs/Sr geopolymers",
    "perera2004": "Context: no primary quantitative leach data",
}

#: Arabic translations of the publisher abstracts. Authored for this compilation; the English
#: column remains the authoritative verbatim text.
ARABIC: dict[str, str] = {
 "blackford2007":
  "أظهر الفحص بالمجهر الإلكتروني النافذ لطور جيوبوليمر مُحضَّر من الميتاكاولين ومحاليل السيليكات "
  "القلوية، بنسب موليّة اسمية Na/Al تساوي 1 وSi/Al تساوي 2، أنه غير متبلور على مقياس نحو 1 نانومتر "
  "بعد المعالجة عند 40 °م. وفي العينات المحتوية على 5% وزناً من السيزيوم أو السترونتيوم، استقر "
  "السيزيوم في الطور غير المتبلور، بينما أُدمج السترونتيوم جزئياً فقط إذ فُصل تفضيلياً إلى كربونات "
  "السترونتيوم SrCO₃ المتبلورة. ولم يكن للتسخين التدريجي لنزع الماء أثر يُذكر في البنية الكلية حتى "
  "500 °م. وبيّن الرنين النووي المغناطيسي في الحالة الصلبة، للمادة المعالَجة قرب درجة حرارة الغرفة، "
  "أن السيزيوم — شأنه شأن الصوديوم — يرتبط أساساً بماء المسام، لكن مع ارتباط ملحوظ بالشبكة "
  "الألومينوسيليكاتية أكبر مما هو عليه لدى الصوديوم. وقد زاد التسخين اللاحق حتى 300 °م من ارتباط "
  "السيزيوم والصوديوم بالشبكة.",
 "frederickx2025":
  "في سياق التخلص من الوقود النووي المستهلك، تمثل النويدات المشعة المولّدة للحرارة مثل السيزيوم "
  "والسترونتيوم مصدر قلق بالغ، لما لها من تأثير كبير في المسافة الواجب تركها بين أنفاق التخلص، "
  "ومن ثمّ في كلفة منشأة التخلص. لذلك تبحث بعض السيناريوهات في فصل الوقود المستهلك وتحويله لتحسين "
  "قابلية التخلص من مجاري النفايات الغنية بالسيزيوم والسترونتيوم وما تبقّى منها. وفي هذه الدراسة "
  "جرى تثبيت مجرى نفايات غني بالسيزيوم والسترونتيوم، وهو محلول نتراتي، ضمن مصفوفات منشَّطة قلوياً "
  "قائمة على الميتاكاولين وخبث الأفران العالية. وقد اختيرت هذه المصفوفات للتثبيت لما هو معروف عنها "
  "من مزايا في المتانة و/أو مقاومة الحرارة مقارنةً بالمواد الإسمنتية التقليدية. وهدف الدراسة هو "
  "تطوير خلطة مثلى لاحتجاز السيزيوم والسترونتيوم.",
 "geomind":
  "‏GEOMIND نموذج تعلّم آلي هجين دُرِّب على قاعدة بيانات داخلية للتوصية بتركيبات جيوبوليمرية مثلى "
  "لخصائص مستهدفة يحددها المستخدم.",
 "lin2026":
  "لا تزال الإزالة الانتقائية للسيزيوم-137 والسترونتيوم-90 المشعّين من مياه الصرف المشعة عالية "
  "الملوحة تحدياً جوهرياً، إذ تخفض الأيونات المنافسة كفاءة الامتزاز وانتقائيته. طُوِّرت في هذه "
  "الدراسة مواد مازّة محبَّبة عالية الأداء قائمة على مصفوفات جيوبوليمرية منشَّطة قلوياً لتحسين أداء "
  "الامتزاز. وقد رُكِّبت المازّات بالبلمرة غير العضوية، وأمكن الحصول على حبيبات متينة ميكانيكياً "
  "ذات مسامية وكيمياء سطحية مضبوطتين. وأظهرت تجارب الامتزاز الدفعية في ماء بحر محاكى كفاءات إزالة "
  "تتجاوز 99% للسيزيوم والسترونتيوم، وأكدت نمذجة الأيزوثرم سعات امتزاز عظمى مرتفعة (حتى 0.41 "
  "مكافئ ميلي/غ للسيزيوم و5.07 مكافئ ميلي/غ للسترونتيوم). كما بيّنت اختبارات الأعمدة ذات الحشوة "
  "الثابتة استمرار كفاءات الإزالة للمازّات المُحسَّنة.",
 "nevin2026":
  "تُعدّ الجيوبوليمرات بديلاً واعداً لأشكال النفايات التقليدية القائمة على الإسمنت البورتلاندي في "
  "تثبيت نواتج الانشطار المشعة الخطرة مثل السيزيوم-137 والسترونتيوم-90، إذ توفر متانة أعلى ومعدلات "
  "ترشيح أدنى.",
 "tarnovsky2024":
  "هدف العمل المقدَّم إلى تخليق جيوبوليمرات قائمة على الميتاكاولين وتحديد قدرتها على الامتزاز في "
  "عملية إزالة أيونات السيزيوم والسترونتيوم من المحاليل المائية. واقتُرحت مقاربات جديدة للحصول على "
  "عيّنتين من الجيوبوليمرات بصور ملائمة تقنياً. ودُرست مورفولوجيا المواد بوساطة تحليل الفلورة "
  "السينية (XRF)، وامتزاز/انفكاك النيتروجين عند درجات حرارة منخفضة، والمجهر الإلكتروني الماسح "
  "(SEM). وتبيّن من تحليل XRF أن أكسيدَي SiO₂ وAl₂O₃ يمثلان المكوّنين الرئيسين في جميع العينات "
  "المدروسة (نحو 54–84% وزناً). وأظهرت دراسات SEM أن الجيوبوليمرات تتألف من جسيمات نانوية ورابط "
  "جيوبوليمري غير متبلور وكاولين غير متفاعل، وأن جميع العينات تحوي مسامات متوسطة بأنصاف أقطار نحو "
  "1–40 نانومتر.",
 "tian2019_wst":
  "البلمرة الجيولوجية عملية تفاعلية آخذة في التطور للاستفادة من النفايات الصلبة. في هذه الدراسة "
  "جرى تخليق جيوبوليمر قائم على الرماد المتطاير ومشتقّه (جيوبوليمر معدَّل بالحديد الثنائي) "
  "وتوصيفهما بوساطة XRD وSEM وFTIR وBET وUV-Vis DRS وTG-DTA، واستُخدما مازّين لإزالة أيونات "
  "السيزيوم والسترونتيوم من المحاليل. وقد توافقت حركية الامتزاز جيداً مع نموذج الرتبة الثانية "
  "الزائفة، وتوافق امتزاز السيزيوم والسترونتيوم على الجيوبوليمر الأصلي بصورة أفضل مع نموذج لانغموير، "
  "في حين كان نموذج فرويندليخ أنسب للامتزاز على الجيوبوليمر المعدَّل بالحديد الثنائي. وأشارت "
  "الطاقات الحرة المحسوبة من أيزوثرم D-R إلى أن الامتزاز يجري أساساً بالتبادل الأيوني، وأن حجم "
  "الحلقة يؤدي دوراً حاسماً في التبادل الأيوني لكلا الأيونين، كما أن لترتيب رباعيات السطوح SiO₄ "
  "وAlO₄ أثراً مهماً.",
 "zhang2021":
  "دُرست في هذا البحث إزالة السيزيوم من المحاليل المائية باستخدام مواد جيولوجية، إذ اختير الامتزاز "
  "طريقةً فعّالة لتطويرها لإزالة السيزيوم من سوائل النفايات المشعة. وحُضِّرت المواد الجيولوجية، "
  "ومنها الرماد المتطاير والخبث كمواد أولية، بوصفها مازّات باستخدام منشِّط قلوي. وجرى توصيف المواد "
  "بحيود الأشعة السينية (XRD)، والمجهر الإلكتروني الماسح المزوَّد بمطياف تشتت الطاقة (SEM-EDS)، "
  "وتحليل المساحة السطحية بطريقة BET وحجم المسام وقياسها. ودُرس تأثير عوامل مختلفة مثل الأس "
  "الهيدروجيني وزمن التماس وجرعة المازّ في امتزاز السيزيوم. وقُيِّم معامل التوزيع والسعة الامتزازية "
  "لتقدير الأداء الفعلي للمازّ، وأظهرت المواد القائمة على الرماد المتطاير سعة امتزاز عظمى للسيزيوم "
  "بلغت 89.32 ملغ/غ ومعامل توزيع مرتفعاً قدره 31.02 ملغ·غ⁻¹·ميلي مول⁻¹.",
 "zheng2023":
  "يولّد تشغيل محطات الطاقة النووية كميات كبيرة من سوائل النفايات المشعة المنخفضة والمتوسطة "
  "المستوى. ويمكن للجيوبوليمرات الغنية بالزيوليت، المخلَّقة في ظروف حرارية مائية من الرماد المتطاير "
  "الصناعي، أن تثبّت النويدات المشعة بفعالية. وقد دُرس في هذا البحث قانون تخليق الجيوبوليمرات "
  "الغنية بالزيوليت وأداء امتزاز/انفكاك النويدة المشعة ⁺Cs باستخدام XRD وSEM وICP. وتُظهر النتائج "
  "أن زيادة درجات حرارة المعالجة وتراكيز هيدروكسيد الصوديوم تؤدي إلى تحوّل الزيوليت من النمط Y إلى "
  "الشابازيت والكانكرينيت عند تراكيز منخفضة من نترات الصوديوم، في حين لا يكون لهيدروكسيد الصوديوم "
  "فوق 2 مول تأثير واضح في التحوّل الطوري عند التراكيز المرتفعة.",
}


def _vancouver(rec: dict) -> str:
    """Vancouver reference: Authors. Title. Journal. Year;Vol(Issue):Pages. doi:DOI"""
    au = rec.get("authors") or []
    if len(au) > 6:
        authors = ", ".join(au[:6]) + ", et al"
    else:
        authors = ", ".join(au)
    bits = [f"{authors}." if authors else "", f"{rec.get('title','').rstrip('.')}."]
    if rec.get("journal"):
        bits.append(f"{rec['journal']}.")
    ym = str(rec.get("year") or "")
    tail = ym
    if rec.get("volume"):
        tail += f";{rec['volume']}"
        if rec.get("issue"):
            tail += f"({rec['issue']})"
        if rec.get("page"):
            tail += f":{rec['page']}"
    if tail:
        bits.append(tail + ".")
    return " ".join(b for b in bits if b)


def load() -> list[dict]:
    cr = json.loads(SCRATCH.read_text())
    out = []
    for doi, rec in cr.items():
        if "title" not in rec:
            continue
        lab = rec["label"]
        authoritative = rec.get("abstract_source") == "Crossref"
        out.append({
            "label": lab,
            "title": rec.get("title", ""),
            "authors": "; ".join(rec.get("authors") or []),
            "journal": rec.get("journal", ""),
            "year": rec.get("year"),
            "volume": rec.get("volume") or "",
            "issue": rec.get("issue") or "",
            "pages": rec.get("page") or "",
            "doi": doi,
            "url": f"https://doi.org/{doi}",
            "vancouver": _vancouver(rec),
            "abstract_en": rec.get("abstract", "") if authoritative else "",
            "abstract_status": ("publisher (verbatim, via Crossref)" if authoritative
                                else "not included — retrieve from the DOI (see module docstring)"),
            "abstract_ar": ARABIC.get(lab, ""),
            "role": ROLE.get(lab, ""),
            "licence": "; ".join(rec.get("license") or []) or "not declared",
        })
    return sorted(out, key=lambda r: (r["year"] or 0, r["label"]))


def write_xlsx(rows: list[dict]) -> Path:
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.utils import get_column_letter

    wb = Workbook()
    ws = wb.active
    ws.title = "Bibliography"
    cols = [("#", 5), ("Source key", 18), ("Title", 60), ("Authors", 40), ("Journal", 32),
            ("Year", 7), ("Vol", 7), ("Issue", 7), ("Pages", 12), ("DOI", 32), ("URL", 34),
            ("Abstract (original, verbatim)", 80), ("Abstract status", 30),
            ("الملخص بالعربية", 80), ("Role in this study", 46), ("Licence (Crossref)", 26)]
    head = Font(bold=True, color="FFFFFF")
    fill = PatternFill("solid", fgColor="0D5C63")
    for i, (name, width) in enumerate(cols, 1):
        c = ws.cell(row=1, column=i, value=name)
        c.font = head
        c.fill = fill
        c.alignment = Alignment(vertical="center", wrap_text=True)
        ws.column_dimensions[get_column_letter(i)].width = width
    ws.freeze_panes = "A2"

    for r, row in enumerate(rows, start=2):
        vals = [r - 1, row["label"], row["title"], row["authors"], row["journal"], row["year"],
                row["volume"], row["issue"], row["pages"], row["doi"], row["url"],
                row["abstract_en"], row["abstract_status"], row["abstract_ar"], row["role"],
                row["licence"]]
        for i, v in enumerate(vals, 1):
            c = ws.cell(row=r, column=i, value=v)
            c.alignment = Alignment(wrap_text=True, vertical="top")
        # Arabic column reads right-to-left
        ws.cell(row=r, column=14).alignment = Alignment(
            wrap_text=True, vertical="top", horizontal="right", readingOrder=2)

    # a second sheet documenting the method, so the file explains itself
    ws2 = wb.create_sheet("About")
    about = [
        ["GEOMIND-R — corpus bibliography"],
        [""],
        ["Every source publication this study drew on, with metadata resolved from Crossref by DOI."],
        [""],
        ["Abstracts"],
        ["Included ONLY where the publisher supplies them through Crossref, so every word in the"],
        ["'Abstract (original, verbatim)' column is attributable. Automated extraction from PDF"],
        ["text was trialled and REJECTED: it produced a confirmed wrong-paper match (a slag/Portland"],
        ["cement abstract attached to a zeolite ion-exchange paper). Unverified text is not shipped."],
        ["Rows without a publisher abstract carry the DOI, which resolves to the authoritative version."],
        [""],
        ["Arabic"],
        ["Translations of the publisher abstracts, prepared for this compilation. The English column"],
        ["remains the authoritative verbatim text."],
        [""],
        ["Copyright"],
        ["Publisher abstracts are the copyright of their publishers. This file is a working"],
        ["bibliography for the authors' own submission and is NOT part of the public data deposit."],
        [""],
        ["Cite the dataset: Fetna M, Hammal A. GEOMIND-R. https://doi.org/10.5281/zenodo.21510123"],
    ]
    for i, line in enumerate(about, 1):
        ws2.cell(row=i, column=1, value=line[0])
    ws2.column_dimensions["A"].width = 100
    ws2.cell(row=1, column=1).font = Font(bold=True, size=13)

    out = _HERE / "GEOMIND-R-bibliography.xlsx"
    wb.save(out)
    return out


def write_docx(rows: list[dict]) -> Path:
    md = ["# GEOMIND-R — corpus bibliography (Vancouver style)", "",
          "Every source publication this study drew on. Metadata resolved from Crossref by DOI.",
          "Abstracts are reproduced **only** where the publisher supplies them, so that every",
          "quoted word is verbatim and attributable; the remaining entries carry the DOI, which",
          "resolves to the authoritative version. Arabic translations follow each abstract.", "",
          "*Publisher abstracts remain the copyright of their publishers. This is a working",
          "bibliography for the authors' submission, not part of the public data deposit.*", "",
          "---", ""]
    for i, r in enumerate(rows, 1):
        md.append(f"**{i}.** {r['vancouver']} doi:{r['doi']}")
        md.append("")
        if r["role"]:
            md.append(f"*Role in this study:* {r['role']}")
            md.append("")
        if r["abstract_en"]:
            md.append(f"**Abstract.** {r['abstract_en']}")
            md.append("")
            if r["abstract_ar"]:
                md.append(f"**الملخص.** {r['abstract_ar']}")
                md.append("")
        else:
            md.append(f"*Abstract:* {r['abstract_status']} — <{r['url']}>")
            md.append("")
        md.append("")
    src = _HERE / "GEOMIND-R-bibliography.md"
    src.write_text("\n".join(md))
    out = _HERE / "GEOMIND-R-bibliography.docx"
    subprocess.run(["pandoc", str(src), "-o", str(out), "--standalone"], check=True)
    return out


def main() -> None:  # pragma: no cover
    rows = load()
    x = write_xlsx(rows)
    d = write_docx(rows)
    withabs = sum(1 for r in rows if r["abstract_en"])
    print(f"wrote {x}\nwrote {d}\n{len(rows)} references, {withabs} with a publisher abstract "
          f"({sum(1 for r in rows if r['abstract_ar'])} translated)")


if __name__ == "__main__":  # pragma: no cover
    main()
