#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
RENTALSYSTEM - MASTER RATIONAL ROSE PETAL MODEL BUILDER (.MDL)
==============================================================================
Project: RentalSystem - HUIT 2025
Target: D:\\DoAnCuNhan\\Rose_Diagrams\\RentalSystem_Master.mdl
Standard: IBM Rational Rose 2003 / Enterprise (Petal Version 47, charSet 0)
Author: Master Rational Rose Model Builder (worker_m2_model)
==============================================================================
"""

import sys
import os
import re
from pathlib import Path
from typing import List, Dict, Tuple, Set, Optional, Any

# Ensure standard output handles UTF-8 safely on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


class QuidManager:
    """
    Hierarchical 16-hex Quid Generator
    Format: [Domain 4 hex: 6001][Category 4 hex: 0001..0008][Sequence 8 hex]
    """
    def __init__(self, prefix="6001"):
        self.prefix = prefix
        self.counters = {
            "0001": 0,  # Actors & Workers
            "0002": 0,  # Use cases (BUC & System)
            "0003": 0,  # Associations, Roles, Dependencies
            "0004": 0,  # Diagrams & Diagram Items
            "0005": 0,  # Classes (BCE & 3-Tier Design)
            "0006": 0,  # Operations & Methods
            "0007": 0,  # Attributes & Fields
            "0008": 0,  # Interactions, Messages, States, Transitions, Nodes
        }
        self.declared_quids: Set[str] = set()

    def get(self, category: str = "0005") -> str:
        self.counters[category] += 1
        cnt = self.counters[category]
        q = f"{self.prefix}{category}{cnt:08X}"
        assert q not in self.declared_quids, f"Fatal: Quid collision for {q}"
        self.declared_quids.add(q)
        return q


INTAB = "àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđÀÁẠẢÃÂẦẤẬẨẪĂẰẮẶẲẴÈÉẸẺẼÊỀẾỆỂỄÌÍỊỈĨÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠÙÚỤỦŨƯỪỨỰỬỮỲÝỴỶỸĐ"
OUTTAB = "aaaaaaaaaaaaaaaaaeeeeeeeeeeeiiiiiooooooooooooooooouuuuuuuuuuuyyyyydAAAAAAAAAAAAAAAAAEEEEEEEEEEEIIIIIOOOOOOOOOOOOOOOOOUUUUUUUUUUUYYYYYD"
TRANSTAB = str.maketrans(INTAB, OUTTAB)

def clean_ascii(s: str) -> str:
    return s.translate(TRANSTAB)


class PetalStream:
    """Buffer that manages Petal indentation and checks bracket balancing."""
    def __init__(self):
        self.lines: List[str] = []
        self.indent_level = 0

    def indent(self):
        self.indent_level += 1

    def dedent(self):
        self.indent_level = max(0, self.indent_level - 1)

    def write(self, text: str = ""):
        if not text:
            self.lines.append("")
            return
        prefix = "    " * self.indent_level
        self.lines.append(f"{prefix}{clean_ascii(text)}")

    def get_content(self) -> str:
        return "\n".join(self.lines) + "\n"


def verify_petal_syntax(content: str) -> bool:
    stack = []
    in_string = False
    escape = False
    lines = content.splitlines()
    for l_idx, line in enumerate(lines, 1):
        for c_idx, ch in enumerate(line, 1):
            if in_string:
                if escape:
                    escape = False
                elif ch == '\\':
                    escape = True
                elif ch == '"':
                    in_string = False
            else:
                if ch == '"':
                    in_string = True
                elif ch == '(':
                    stack.append((l_idx, c_idx))
                elif ch == ')':
                    if not stack:
                        print(f"Internal Check Error: Unmatched ')' at line {l_idx}:{c_idx}")
                        start = max(0, l_idx - 6)
                        end = min(len(lines), l_idx + 3)
                        for k in range(start, end):
                            prefix = "--> " if k == l_idx - 1 else "    "
                            print(f"{prefix}{k+1:5d}: {lines[k]}")
                        return False
                    stack.pop()

    if in_string:
        print("Internal Check Error: Unterminated string literal at EOF!")
        return False

    if stack:
        print(f"Internal Check Error: {len(stack)} unclosed '('! First 5:")
        for l, c in stack[:5]:
            print(f"  Line {l}:{c} -> {lines[l-1].strip()[:60]}")
        return False

    print(">>> [Internal Check] Parentheses perfectly balanced! 0 errors.")
    return True


def build_master_model() -> str:
    qm = QuidManager()
    out = PetalStream()

    # Quids for Root objects
    quid_design = qm.get("0005")
    quid_uc_pkg = qm.get("0005")
    quid_log_pkg = qm.get("0005")
    quid_comp_pkg = qm.get("0005")
    quid_proc_pkg = qm.get("0008")
    quid_deploy_diag = qm.get("0004")

    # 1. PETAL HEADER
    out.write('(object Petal')
    out.indent()
    out.write('version \t47')
    out.write('_written \t"Rose 8.0.0303.1400"')
    out.write('charSet \t0)')
    out.dedent()
    out.write()

    # 2. ROOT DESIGN
    out.write('(object Design "Logical View"')
    out.indent()
    out.write('is_unit \tTRUE')
    out.write('is_loaded \tTRUE')
    out.write(f'quid \t"{quid_design}"')
    out.write('defaults \t(object defaults')
    out.indent()
    out.write('rightMargin \t0.250000')
    out.write('leftMargin \t0.250000')
    out.write('topMargin \t0.250000')
    out.write('bottomMargin \t0.250000')
    out.write('pageOverlap \t0.250000')
    out.write('clipIconLabels \tTRUE')
    out.write('autoResize \tTRUE')
    out.write('snapToGrid \tTRUE')
    out.write('gridX \t16')
    out.write('gridY \t16')
    out.write('defaultFont \t(object Font')
    out.indent()
    out.write('size \t10')
    out.write('face \t"Arial"')
    out.write('bold \tFALSE')
    out.write('italics \tFALSE')
    out.write('underline \tFALSE')
    out.write('strike \tFALSE')
    out.write('color \t0')
    out.write('default_color \tTRUE))')
    out.dedent()
    out.dedent()

    # =========================================================================
    # PART A: USE CASE VIEW (root_usecase_package)
    # =========================================================================
    out.write('root_usecase_package \t(object Class_Category "Use Case View"')
    out.indent()
    out.write(f'quid \t"{quid_uc_pkg}"')
    out.write('exportControl \t"Public"')
    out.write('global \tTRUE')
    out.write('logical_models \t(list unit_reference_list')
    out.indent()

    # A.1. Actors & Workers
    actors_info = [
        ("Khach hang", "actor", "Khach hang ca nhan hoac to chuc thue thiet bi cong nghe, ky hop dong, thanh toan va tiep nhan."),
        ("Ngan hang / Cong VietQR", "actor", "Cong thanh toan VietQR NAPAS 247 va Ngan hang doi soat giao dich tu dong."),
        ("Nhan vien kinh doanh", "actor", "Nhan vien kinh doanh: Tham dinh KYC, lap hop dong, nhac no, phe duyet gia han, lap phieu chi hoan coc."),
        ("Ky thuat vien", "actor", "Ky thuat vien: Quet serial xuat kho, ban giao tan noi, dong kiem, bao tri SLA, nghiem thu thu hoi may."),
        ("Quan tri vien", "actor", "Quan tri vien: Cau hinh he thong, phan quyen RBAC, quan ly danh muc, dieu phoi bao tri va giam sat BI.")
    ]
    actors_dict: Dict[str, Dict[str, str]] = {}
    for name, st, doc in actors_info:
        q = qm.get("0001")
        actors_dict[name] = {"quid": q, "stereotype": st, "doc": doc}
        out.write(f'(object Class "{name}"')
        out.indent()
        out.write(f'quid \t"{q}"')
        out.write(f'stereotype \t"{st}"')
        out.write(f'documentation \t"{doc}")')
        out.dedent()

    # A.2. 7 Business Use Cases (BUCs)
    bucs_info = [
        ("BUC-01 - Dang ky & Xac thuc nguoi dung", "Dang ky tai khoan KYC, xac thuc danh tinh CCCD, ma hoa BCrypt va phan quyen truy cap he thong."),
        ("BUC-02 - Dat thue may & Kiem tra ton kho", "Khach chon cau hinh serial, he thong kich hoat SemaphoreSlim kiem tra kha dung va giu cho 24h."),
        ("BUC-03 - Thanh toan dat coc qua VietQR dong", "Sinh ma VietQR dong EMVCo NAPAS 247, gach no tu dong qua Banking Webhook va xu ly ca bien coc thieu."),
        ("BUC-04 - Ban giao & Ky bien ban ban giao may", "KTV quet barcode serial xuat kho, giao tan noi, ky bien ban HTML5 Canvas, xu ly khach khong nhan may."),
        ("BUC-05 - Bao cao su co & Phan cong bao tri thiet bi", "Khach tao ticket su co, he thong dieu phoi KTV, kich hoat SLA tam dung tinh tien va tham dinh phi den bu."),
        ("BUC-06 - Gia han hop dong & Phan ky no", "Khach de xuat gia han hop dong, kinh doanh phe duyet, lap lich thanh toan moi va xu ly tre han khong tra may."),
        ("BUC-07 - Tra may, nghiem thu & Hoan tra tien coc", "KTV nghiem thu thiet bi, giam dinh hu hai vat ly, can tru cong no phi den bu va lap phieu chi hoan tien coc.")
    ]
    bucs_dict: Dict[str, Dict[str, str]] = {}
    for name, doc in bucs_info:
        q = qm.get("0002")
        bucs_dict[name] = {"quid": q, "doc": doc}
        out.write(f'(object UseCase "{name}"')
        out.indent()
        out.write(f'quid \t"{q}"')
        out.write('stereotype \t"business use case"')
        out.write(f'documentation \t"{doc}")')
        out.dedent()

    # A.3. Associations between Actors and BUCs (External Actors only)
    buc_assoc_matrix = [
        ("Khach hang", "BUC-01 - Dang ky & Xac thuc nguoi dung"),
        ("Khach hang", "BUC-02 - Dat thue may & Kiem tra ton kho"),
        ("Khach hang", "BUC-03 - Thanh toan dat coc qua VietQR dong"),
        ("Khach hang", "BUC-04 - Ban giao & Ky bien ban ban giao may"),
        ("Khach hang", "BUC-05 - Bao cao su co & Phan cong bao tri thiet bi"),
        ("Khach hang", "BUC-06 - Gia han hop dong & Phan ky no"),
        ("Khach hang", "BUC-07 - Tra may, nghiem thu & Hoan tra tien coc"),
        ("Ngan hang / Cong VietQR", "BUC-03 - Thanh toan dat coc qua VietQR dong"),
        ("Ngan hang / Cong VietQR", "BUC-07 - Tra may, nghiem thu & Hoan tra tien coc"),
    ]
    buc_assocs: List[Dict[str, str]] = []
    for idx, (act_name, buc_name) in enumerate(buc_assoc_matrix):
        q_assoc = qm.get("0003")
        q_r1 = qm.get("0003")
        q_r2 = qm.get("0003")
        assoc_name = f"$UNNAMED${idx}"
        r1_name = f"$UNNAMED${idx*2 + 1}"
        r2_name = f"$UNNAMED${idx*2 + 2}"
        buc_assocs.append({
            "name": assoc_name, "quid": q_assoc,
            "r1_name": r1_name, "r1_quid": q_r1, "buc": buc_name, "buc_quid": bucs_dict[buc_name]["quid"],
            "r2_name": r2_name, "r2_quid": q_r2, "actor": act_name, "act_quid": actors_dict[act_name]["quid"]
        })
        out.write(f'(object Association "{assoc_name}"')
        out.indent()
        out.write(f'quid \t"{q_assoc}"')
        out.write('roles \t(list role_list')
        out.indent()
        out.write(f'(object Role "{r1_name}"')
        out.indent()
        out.write(f'quid \t"{q_r1}"')
        out.write(f'supplier \t"Use Case View::{buc_name}"')
        out.write(f'quidu \t"{bucs_dict[buc_name]["quid"]}"')
        out.write('is_navigable \tTRUE)')
        out.dedent()
        out.write(f'(object Role "{r2_name}"')
        out.indent()
        out.write(f'quid \t"{q_r2}"')
        out.write(f'supplier \t"Use Case View::{act_name}"')
        out.write(f'quidu \t"{actors_dict[act_name]["quid"]}")')
        out.dedent()
        out.dedent()
        out.write('))')
        out.dedent()

    # A.4. Overview System Use Cases (14 SYS-UCs)
    sys_ucs_info = [
        ("SYS-UC01 - Dang ky & Xac thuc tai khoan", ["Khach hang", "Quan tri vien"]),
        ("SYS-UC02 - Dat thue & Giu cho may Serial", ["Khach hang"]),
        ("SYS-UC03 - Ky so hop dong Canvas HTML5 & CCCD", ["Khach hang"]),
        ("SYS-UC04 - Theo doi lich no ca nhan MyDebt", ["Khach hang"]),
        ("SYS-UC05 - Tham dinh & Duyet hop dong thue", ["Nhan vien kinh doanh"]),
        ("SYS-UC06 - Quan ly thiet bi Serial & Danh muc kho", ["Quan tri vien", "Ky thuat vien"]),
        ("SYS-UC07 - Quan tri phan quyen nguoi dung RBAC", ["Quan tri vien"]),
        ("SYS-UC08 - Giam sat cong no & Tuoi no 4 cap", ["Nhan vien kinh doanh", "Quan tri vien"]),
        ("SYS-UC09 - Xuat kho ban giao & Quet Barcode", ["Ky thuat vien"]),
        ("SYS-UC10 - Tiep nhan & Xu ly su co theo SLA", ["Ky thuat vien", "Khach hang"]),
        ("SYS-UC11 - Thu hoi, nghiem thu & Doi may", ["Ky thuat vien"]),
        ("SYS-UC12 - Thanh toan dat coc VietQR dong NAPAS 247", ["Khach hang", "Ngan hang / Cong VietQR"]),
        ("SYS-UC13 - Doi soat tu dong Banking Webhook", ["Ngan hang / Cong VietQR"]),
        ("SYS-UC14 - Lap phieu chi hoan tien coc", ["Nhan vien kinh doanh"])
    ]
    sys_ucs_dict: Dict[str, Dict[str, Any]] = {}
    for name, acts in sys_ucs_info:
        q = qm.get("0002")
        sys_ucs_dict[name] = {"quid": q, "actors": acts}
        out.write(f'(object UseCase "{name}"')
        out.indent()
        out.write(f'quid \t"{q}"')
        out.write('stereotype \t"use case"')
        out.write(f'documentation \t"Ca su dung he thong {name}")')
        out.dedent()

    # Associations for SYS-UCs Overview
    sys_assocs: List[Dict[str, str]] = []
    sys_assoc_idx = 100
    for name, acts in sys_ucs_info:
        for act in acts:
            sys_assoc_idx += 1
            q_a = qm.get("0003")
            q_r1 = qm.get("0003")
            q_r2 = qm.get("0003")
            a_name = f"$UNNAMED${sys_assoc_idx}"
            r1_n = f"$UNNAMED${sys_assoc_idx*2+1}"
            r2_n = f"$UNNAMED${sys_assoc_idx*2+2}"
            sys_assocs.append({
                "name": a_name, "quid": q_a,
                "r1_name": r1_n, "r1_quid": q_r1, "uc": name, "uc_quid": sys_ucs_dict[name]["quid"],
                "r2_name": r2_n, "r2_quid": q_r2, "actor": act, "act_quid": actors_dict[act]["quid"]
            })
            out.write(f'(object Association "{a_name}"')
            out.indent()
            out.write(f'quid \t"{q_a}"')
            out.write('roles \t(list role_list')
            out.indent()
            out.write(f'(object Role "{r1_n}"')
            out.indent()
            out.write(f'quid \t"{q_r1}"')
            out.write(f'supplier \t"Use Case View::{name}"')
            out.write(f'quidu \t"{sys_ucs_dict[name]["quid"]}"')
            out.write('is_navigable \tTRUE)')
            out.dedent()
            out.write(f'(object Role "{r2_n}"')
            out.indent()
            out.write(f'quid \t"{q_r2}"')
            out.write(f'supplier \t"Use Case View::{act}"')
            out.write(f'quidu \t"{actors_dict[act]["quid"]}")')
            out.dedent()
            out.dedent()
            out.write('))')
            out.dedent()

    # A.5. The 3 Subsystem Packages (Customer Portal, Admin & Operations, Maintenance & Technical)
    subsystems_def = [
        {
            "pkg_name": "Phan he Khach hang (Customer Portal)",
            "doc": "Phan he danh cho Khach hang ca nhan va doanh nghiep thue may.",
            "actors": ["Khach hang", "Ngan hang / Cong VietQR"],
            "ucs": [
                "UC-KH01 - Dang ky & Dang nhap tai khoan",
                "UC-KH02 - Tim kiem & Loc danh muc thiet bi",
                "UC-KH03 - Dat thue & Giu cho may Serial",
                "UC-KH04 - Ky hop dong dien tu Canvas & CCCD",
                "UC-KH05 - Thanh toan dat coc VietQR dong",
                "UC-KH06 - Theo doi lich no & Tra gop ky han",
                "UC-KH07 - Gui yeu cau bao su co ky thuat SLA",
                "UC-KH08 - Yeu cau gia han hop dong thue"
            ]
        },
        {
            "pkg_name": "Phan he Quan tri & Van hanh (Admin & Operations)",
            "doc": "Phan he danh cho Quan tri vien va Nhan vien kinh doanh dieu hanh.",
            "actors": ["Quan tri vien", "Nhan vien kinh doanh", "Ngan hang / Cong VietQR"],
            "ucs": [
                "UC-AD01 - Quan tri nguoi dung & Phan quyen",
                "UC-AD02 - Quan ly danh muc & May Serial",
                "UC-AD03 - Tham dinh & Duyet hop dong thue",
                "UC-AD04 - Cau hinh ma khuyen mai Voucher",
                "UC-AD05 - Giam sat cong no & Tuoi no 4 cap",
                "UC-AD06 - Cau hinh chinh sach lai phat & An han",
                "UC-AD07 - Doi soat bien dong so du Webhook",
                "UC-AD08 - Lap phieu chi hoan tra tien coc",
                "UC-AD09 - Xuat bao cao tai chinh BI Excel"
            ]
        },
        {
            "pkg_name": "Phan he Bao tri & Ky thuat (Maintenance & Technical)",
            "doc": "Phan he dieu phoi, bao tri va nghiem thu thiet bi theo SLA.",
            "actors": ["Quan tri vien", "Ky thuat vien", "Khach hang"],
            "ucs": [
                "UC-BT01 - Tiep nhan yeu cau bao su co thiet bi",
                "UC-BT02 - Dieu phoi & Phan cong ky thuat vien",
                "UC-BT03 - Kich hoat SLA tam dung tinh tien",
                "UC-BT04 - Kiem tra tai cho, sua chua & Doi may",
                "UC-BT05 - Dong kiem & Ky bien ban bao tri",
                "UC-BT06 - Nghiem thu hoan tat & Cap nhat kho"
            ]
        }
    ]

    subsys_storage: List[Dict[str, Any]] = []
    subsys_assoc_idx = 300

    for sdef in subsystems_def:
        pkg_name = sdef["pkg_name"]
        pkg_quid = qm.get("0005")
        s_data = {
            "name": pkg_name, "quid": pkg_quid, "doc": sdef["doc"],
            "actors": sdef["actors"], "ucs": {}, "assocs": [], "diag_quid": qm.get("0004")
        }
        out.write(f'(object Class_Category "{pkg_name}"')
        out.indent()
        out.write(f'quid \t"{pkg_quid}"')
        out.write('exportControl \t"Public"')
        out.write('logical_models \t(list unit_reference_list')
        out.indent()

        for u in sdef["ucs"]:
            uq = qm.get("0002")
            s_data["ucs"][u] = uq
            out.write(f'(object UseCase "{u}"')
            out.indent()
            out.write(f'quid \t"{uq}"')
            out.write('stereotype \t"use case"')
            out.write(f'documentation \t"Ca su dung {u} thuoc {pkg_name}")')
            out.dedent()

        # Associations inside subsystem - single qualified path to avoid regex warning
        for u in sdef["ucs"]:
            primary_act = sdef["actors"][0]
            subsys_assoc_idx += 1
            aq = qm.get("0003")
            r1q = qm.get("0003")
            r2q = qm.get("0003")
            aname = f"$UNNAMED${subsys_assoc_idx}"
            r1n = f"$UNNAMED${subsys_assoc_idx*2+1}"
            r2n = f"$UNNAMED${subsys_assoc_idx*2+2}"
            s_data["assocs"].append({
                "name": aname, "quid": aq,
                "r1_name": r1n, "r1_quid": r1q, "uc": u, "uc_quid": s_data["ucs"][u],
                "r2_name": r2n, "r2_quid": r2q, "actor": primary_act, "act_quid": actors_dict[primary_act]["quid"]
            })
            out.write(f'(object Association "{aname}"')
            out.indent()
            out.write(f'quid \t"{aq}"')
            out.write('roles \t(list role_list')
            out.indent()
            out.write(f'(object Role "{r1n}"')
            out.indent()
            out.write(f'quid \t"{r1q}"')
            out.write(f'supplier \t"Use Case View::{pkg_name}::{u}"')
            out.write(f'quidu \t"{s_data["ucs"][u]}"')
            out.write('is_navigable \tTRUE)')
            out.dedent()
            out.write(f'(object Role "{r2n}"')
            out.indent()
            out.write(f'quid \t"{r2q}"')
            out.write(f'supplier \t"Use Case View::{primary_act}"')
            out.write(f'quidu \t"{actors_dict[primary_act]["quid"]}")')
            out.dedent()
            out.dedent()
            out.write('))')
            out.dedent()

        out.dedent()
        out.write(')')  # end logical_models of subsystem

        # Subsystem UseCaseDiagram presentation
        out.write('logical_presentations \t(list unit_reference_list')
        out.indent()
        out.write(f'(object UseCaseDiagram "{pkg_name} Diagram"')
        out.indent()
        out.write(f'quid \t"{s_data["diag_quid"]}"')
        out.write(f'title \t"{pkg_name} Diagram"')
        out.write('zoom \t100')
        out.write('max_height \t28350')
        out.write('max_width \t21600')
        out.write('origin_x \t0')
        out.write('origin_y \t0')
        out.write('items \t(list diagram_item_list')
        out.indent()

        # Actor view
        v_act_id = 1
        out.write(f'(object ClassView "Class" "Use Case View::{sdef["actors"][0]}" @{v_act_id}')
        out.indent()
        out.write('ShowCompartmentStereotypes \tTRUE')
        out.write('location \t(300, 600)')
        out.write('font \t(object Font size 10 face "Arial")')
        out.write(f'label \t(object ItemLabel Parent_View @{v_act_id} location (300, 750) anchor_loc 1 nlines 2 max_width 325 justify 0 label "{sdef["actors"][0]}")')
        out.write(f'icon \t"{actors_dict[sdef["actors"][0]]["stereotype"]}"')
        out.write('icon_style \t"Icon"')
        out.write('line_color \t3342348')
        out.write('fill_color \t13434879')
        out.write(f'quidu \t"{actors_dict[sdef["actors"][0]]["quid"]}"')
        out.write('autoResize \tTRUE)')
        out.dedent()

        # Use cases views & associations
        v_item_id = v_act_id
        uc_views_map = {}
        y_uc = 250
        for u, uq in s_data["ucs"].items():
            v_item_id += 1
            uc_views_map[u] = v_item_id
            out.write(f'(object UseCaseView "Use Case View::{pkg_name}::{u}" @{v_item_id}')
            out.indent()
            out.write(f'location \t(1200, {y_uc})')
            out.write('font \t(object Font size 10 face "Arial")')
            out.write(f'label \t(object ItemLabel Parent_View @{v_item_id} location (1200, {y_uc}) anchor_loc 1 nlines 2 max_width 630 justify 0 label "{u}")')
            out.write('icon_style \t"Icon"')
            out.write('line_color \t3342348')
            out.write('fill_color \t13434879')
            out.write(f'quidu \t"{uq}"')
            out.write('height \t118')
            out.write('autoResize \tTRUE)')
            out.dedent()
            y_uc += 200

        for a in s_data["assocs"]:
            v_item_id += 1
            a_vid = v_item_id
            v_item_id += 1
            r1_vid = v_item_id
            v_item_id += 1
            r2_vid = v_item_id
            u_vid = uc_views_map[a["uc"]]
            out.write(f'(object AssociationViewNew "{a["name"]}" @{a_vid}')
            out.indent()
            out.write('location \t(750, 500)')
            out.write('stereotype \tTRUE')
            out.write('line_color \t3342348')
            out.write(f'quidu \t"{a["quid"]}"')
            out.write('roleview_list \t(list RoleViews')
            out.indent()
            out.write(f'(object RoleView "{a["r1_name"]}" @{r1_vid}')
            out.indent()
            out.write(f'Parent_View \t@{a_vid}')
            out.write('location \t(500, 200)')
            out.write(f'quidu \t"{a["r1_quid"]}"')
            out.write(f'client \t@{a_vid}')
            out.write(f'supplier \t@{u_vid}')
            out.write('line_style \t0)')
            out.dedent()
            out.write(f'(object RoleView "{a["r2_name"]}" @{r2_vid}')
            out.indent()
            out.write(f'Parent_View \t@{a_vid}')
            out.write('location \t(500, 200)')
            out.write(f'quidu \t"{a["r2_quid"]}"')
            out.write(f'client \t@{a_vid}')
            out.write(f'supplier \t@{v_act_id}')
            out.write('line_style \t0)')
            out.dedent()
            out.dedent()
            out.write('))')
            out.dedent()

        out.dedent()
        out.write(')))')  # end diagram_item_list, UseCaseDiagram, logical_presentations
        out.dedent()
        out.write(')')  # end Class_Category of subsystem
        subsys_storage.append(s_data)

    # A.6. 7 Core Business Workflows (2.2.2.1 to 2.2.2.7)
    workflows_spec = [
        {
            "id": "2.2.2.1",
            "name": "Quy trinh 1 - Dang ky & Xac thuc nguoi dung",
            "swimlanes": ["Khach hang", "He thong"],
            "steps": [
                ("Nhap ho so dang ky", "Khach hang"),
                ("Kiem tra CCCD va Email duy nhat", "He thong"),
                ("Ma hoa mat khau BCrypt", "He thong"),
                ("Tao tai khoan va cap quyen", "He thong"),
                ("Xac thuc dang nhap thanh cong", "Khach hang")
            ],
            "lifelines": [("kh:Khach hang", "Use Case View::Khach hang", actors_dict["Khach hang"]["quid"]),
                          ("v:DangKyView", "Logical View::DangKyView", None),
                          ("c:AccountControl", "Logical View::AccountControl", None),
                          ("u:NguoiDung", "Logical View::NguoiDung", None)],
            "messages": [
                ("1: NhapThongTinDangKy()", 0, 1),
                ("2: GuiYeuCauDangKy()", 1, 2),
                ("3: KiemTraTrungVaMaHoaBCrypt()", 2, 3),
                ("4: LuuThongTinTaiKhoan()", 3, 2),
                ("5: ThongBaoKetQua()", 2, 1),
                ("6: HienThiThanhCong()", 1, 0)
            ]
        },
        {
            "id": "2.2.2.2",
            "name": "Quy trinh 2 - Dat thue may & Kiem tra ton kho",
            "swimlanes": ["Khach hang", "CartControl", "ApplicationDbContext"],
            "steps": [
                ("Chon may va thoi han thue", "Khach hang"),
                ("Kich hoat khoa InventoryLock (SemaphoreSlim)", "CartControl"),
                ("Kiem tra lich trong thiet bi serial", "ApplicationDbContext"),
                ("Giu cho thiet bi 24h HanChotKy", "ApplicationDbContext"),
                ("Giai phong khoa SemaphoreSlim", "CartControl"),
                ("Xac nhan giu cho thanh cong", "Khach hang")
            ],
            "lifelines": [("kh:Khach hang", "Use Case View::Khach hang", actors_dict["Khach hang"]["quid"]),
                          ("v:DatThueView", "Logical View::DatThueView", None),
                          ("c:CartControl", "Logical View::CartControl", None),
                          ("tb:ThietBi", "Logical View::ThietBi", None),
                          ("hd:HopDong", "Logical View::HopDong", None)],
            "messages": [
                ("1: ChonMayVaNgayThue()", 0, 1),
                ("2: KichHoatKhoaInventoryLock()", 1, 2),
                ("3: KiemTraLichTrongSerial()", 2, 3),
                ("4: CapNhatTrangThaiGiuCho3()", 2, 3),
                ("5: TaoDonThueGiuCho24h()", 2, 4),
                ("6: GiaiPhongKhoaInventoryLock()", 2, 1),
                ("7: ThongBaoGiuChoThanhCong()", 1, 0)
            ]
        },
        {
            "id": "2.2.2.3",
            "name": "Quy trinh 3 - Thanh toan dat coc qua VietQR dong",
            "swimlanes": ["Khach hang", "Ngan hang / VietQR", "PaymentControl", "He thong"],
            "steps": [
                ("Quet ma VietQR dong NAPAS 247", "Khach hang"),
                ("Chuyen khoan xac nhan", "Ngan hang / VietQR"),
                ("Phat tin hieu Banking Webhook", "Ngan hang / VietQR"),
                ("Mo PaymentLock dong bo", "PaymentControl"),
                ("Kiem tra transferAmount so voi TienCoc", "PaymentControl"),
                ("Ca bien Coc thieu - Tao PhieuThu do dang & Giu 24h", "He thong"),
                ("Cua coc du - Gach no & HopDong.TrangThai = 1", "He thong")
            ],
            "lifelines": [("kh:Khach hang", "Use Case View::Khach hang", actors_dict["Khach hang"]["quid"]),
                          ("mb:NganHang", "Use Case View::Ngan hang / Cong VietQR", actors_dict["Ngan hang / Cong VietQR"]["quid"]),
                          ("c:PaymentControl", "Logical View::PaymentControl", None),
                          ("pt:PhieuThu", "Logical View::PhieuThu", None),
                          ("hd:HopDong", "Logical View::HopDong", None)],
            "messages": [
                ("1: QuetMaVietQRDong()", 0, 1),
                ("2: GuiTinHieuWebhook()", 1, 2),
                ("3: KichHoatPaymentLock()", 2, 2),
                ("4: KiemTraSoTienNhan()", 2, 4),
                ("5: [CocThieu] TaoPhieuThuDoDangGiuCho24h()", 2, 3),
                ("6: [CocDu] GachNoVaXacNhanTrangThai1()", 2, 4),
                ("7: ThongBaoXacNhanThanhToan()", 2, 0)
            ]
        },
        {
            "id": "2.2.2.4",
            "name": "Quy trinh 4 - Ban giao & Ky bien ban ban giao may",
            "swimlanes": ["Ky thuat vien", "Khach hang", "HopDongControl", "Kho may"],
            "steps": [
                ("Quet barcode serial xuat kho", "Ky thuat vien"),
                ("Van chuyen may den dia chi khach", "Ky thuat vien"),
                ("Dong kiem tra tinh trang thiet bi", "Khach hang"),
                ("Ca bien Khach khong nhan - Lap bien ban huy", "Ky thuat vien"),
                ("Xu ly huy - Hoan kho TrangThai=0 & PhieuChi hoan coc", "HopDongControl"),
                ("Ky Canvas HTML5 & Xuat PDF bien ban", "Khach hang"),
                ("Cap nhat may - TrangThai = 1 (Dang thue)", "Kho may")
            ],
            "lifelines": [("ktv:KyThuatVien", "Use Case View::Ky thuat vien", actors_dict["Ky thuat vien"]["quid"]),
                          ("kh:KhachHang", "Use Case View::Khach hang", actors_dict["Khach hang"]["quid"]),
                          ("v:BanGiaoView", "Logical View::BanGiaoView", None),
                          ("c:HopDongControl", "Logical View::HopDongControl", None),
                          ("bb:BienBanBanGiao", "Logical View::BienBanBanGiao", None),
                          ("tb:ThietBi", "Logical View::ThietBi", None),
                          ("pc:PhieuChi", "Logical View::PhieuChi", None)],
            "messages": [
                ("1: QuetBarcodeXuatKho()", 0, 2),
                ("2: DongKiemThietBi()", 0, 1),
                ("3: [KhachKhongNhan] YeuCauHuyVaHoanKho()", 0, 3),
                ("4: [KhachKhongNhan] CapNhatKhoTrangThai0()", 3, 5),
                ("5: [KhachKhongNhan] LapPhieuChiHoanCoc()", 3, 6),
                ("6: [KhachNhan] KyCanvasHTML5()", 1, 2),
                ("7: LuuBienBanXuatPDF()", 3, 4),
                ("8: ChuyenMayTrangThaiDangThue1()", 3, 5)
            ]
        },
        {
            "id": "2.2.2.5",
            "name": "Quy trinh 5 - Bao cao su co & Phan cong bao tri thiet bi",
            "swimlanes": ["Khach hang", "Quan tri vien", "Ky thuat vien", "BaoTriControl"],
            "steps": [
                ("Gui ticket bao su co kem hinh anh", "Khach hang"),
                ("Quan tri vien phan cong KTV xu ly", "Quan tri vien"),
                ("KTV tiep nhan ticket tai cho", "Ky thuat vien"),
                ("Kich hoat SLA tam dung tinh tien thue", "BaoTriControl"),
                ("Kiem tra nguyen nhan hu hai vat ly", "Ky thuat vien"),
                ("Ca bien Hong do khach - Dinh gia PhiDenBu", "Ky thuat vien"),
                ("Sua chua xong hoac doi may du phong", "Ky thuat vien"),
                ("Nghiem thu hoan tat ticket", "Khach hang")
            ],
            "lifelines": [("kh:KhachHang", "Use Case View::Khach hang", actors_dict["Khach hang"]["quid"]),
                          ("admin:QuanTriVien", "Use Case View::Quan tri vien", actors_dict["Quan tri vien"]["quid"]),
                          ("ktv:KyThuatVien", "Use Case View::Ky thuat vien", actors_dict["Ky thuat vien"]["quid"]),
                          ("c:BaoTriControl", "Logical View::BaoTriControl", None),
                          ("pbt:PhieuBaoTri", "Logical View::PhieuBaoTri", None)],
            "messages": [
                ("1: GuiTicketBaoSuCo()", 0, 3),
                ("2: DieuPhoiKyThuatVien()", 1, 3),
                ("3: KTVTiepNhanCongViec()", 2, 3),
                ("4: KichHoatSLATamDungTinhTien()", 3, 4),
                ("5: GiamDinhVaGhiNhanPhiDenBu()", 2, 4),
                ("6: HoanTatSuaChuaDoiMay()", 2, 3),
                ("7: DongTicketVaMoLaiTinhTien()", 3, 4)
            ]
        },
        {
            "id": "2.2.2.6",
            "name": "Quy trinh 6 - Gia han hop dong & Phan ky no",
            "swimlanes": ["Khach hang", "Nhan vien kinh doanh", "CongNoControl", "He thong"],
            "steps": [
                ("Gui yeu cau gia han them thoi gian", "Khach hang"),
                ("Kiem tra xung dot don dat ke tiep", "He thong"),
                ("Kinh doanh tham dinh va phe duyet", "Nhan vien kinh doanh"),
                ("Chia ky han cong no bo sung", "CongNoControl"),
                ("Ca bien Tre han - An han 3 ngay tu dong", "He thong"),
                ("Ca bien Tre han - Phat 0.1%/ngay tu ngay 4", "CongNoControl"),
                ("Ca bien Tre han - Khoa tai khoan ngay 15 & Khoi kien >30 ngay", "He thong")
            ],
            "lifelines": [("kh:KhachHang", "Use Case View::Khach hang", actors_dict["Khach hang"]["quid"]),
                          ("nvkd:KinhDoanh", "Use Case View::Nhan vien kinh doanh", actors_dict["Nhan vien kinh doanh"]["quid"]),
                          ("c:CongNoControl", "Logical View::CongNoControl", None),
                          ("ygh:YeuCauGiaHan", "Logical View::YeuCauGiaHan", None),
                          ("kht:KyHanThanhToan", "Logical View::KyHanThanhToan", None)],
            "messages": [
                ("1: DeXuatGiaHanHopDong()", 0, 3),
                ("2: KiemTraLichVaDuyetGiaHan()", 1, 3),
                ("3: PhanKyCongNoMoi()", 1, 2),
                ("4: SinhCacKyHanThanhToan()", 2, 4),
                ("5: [TreHan] TinhPhat0.1PhanTram()", 2, 4),
                ("6: [TreHanQua15Ngay] KhoaTaiKhoanBlacklist()", 2, 0),
                ("7: ThongBaoKeHoachTraNo()", 2, 0)
            ]
        },
        {
            "id": "2.2.2.7",
            "name": "Quy trinh 7 - Tra may, nghiem thu & Hoan tra tien coc",
            "swimlanes": ["Ky thuat vien", "Nhan vien kinh doanh", "HopDongControl", "Tai chinh"],
            "steps": [
                ("Thu hoi may va kiem tra tem serial", "Ky thuat vien"),
                ("Tham dinh hu hai ngoai quan va linh kien", "Ky thuat vien"),
                ("Lap bien ban nghiem thu thu hoi", "Ky thuat vien"),
                ("Giai thuat quyet toan refund = TienCoc - NoThue - PhiDenBu", "HopDongControl"),
                ("Ca bien refund >= 0 - Can tru coc & PhieuChi hoan du", "Tai chinh"),
                ("Ca bien refund < 0 - Tich thu coc & VietQR truy thu", "Tai chinh"),
                ("Hoan tat tat toan hop dong", "Nhan vien kinh doanh")
            ],
            "lifelines": [("ktv:KyThuatVien", "Use Case View::Ky thuat vien", actors_dict["Ky thuat vien"]["quid"]),
                          ("nvkd:KinhDoanh", "Use Case View::Nhan vien kinh doanh", actors_dict["Nhan vien kinh doanh"]["quid"]),
                          ("c:HopDongControl", "Logical View::HopDongControl", None),
                          ("bb:BienBanBanGiao", "Logical View::BienBanBanGiao", None),
                          ("pc:PhieuChi", "Logical View::PhieuChi", None),
                          ("hd:HopDong", "Logical View::HopDong", None)],
            "messages": [
                ("1: GiamDinhMayThuHoi()", 0, 3),
                ("2: LapBienBanNghiemThu()", 0, 3),
                ("3: TinhToanQuyetToanHoanCoc()", 1, 2),
                ("4: [CocDu] LapPhieuChiHoanTienDu()", 2, 4),
                ("5: [CocThieu] TichThuCocVaBlacklist()", 2, 5),
                ("6: CapNhatTrangThaiHoanCoc()", 2, 5),
                ("7: DongTatToanHopDong()", 1, 5)
            ]
        }
    ]

    # Pre-allocate quids for logical classes
    logical_prealloc: Dict[str, str] = {}
    classes_needed = [
        "DangKyView", "AccountControl", "NguoiDung",
        "DatThueView", "CartControl", "ThietBi", "HopDong",
        "PaymentControl", "PhieuThu", "BanGiaoView", "HopDongControl",
        "BienBanBanGiao", "PhieuChi", "BaoTriControl", "PhieuBaoTri",
        "CongNoControl", "YeuCauGiaHan", "KyHanThanhToan"
    ]
    for cname in classes_needed:
        logical_prealloc[cname] = qm.get("0005")

    wf_storage: List[Dict[str, Any]] = []
    for wf in workflows_spec:
        wf_cat_name = f"Process {wf['id']} - {wf['name']}"
        wf_cat_quid = qm.get("0005")
        wf_data = {
            "name": wf_cat_name, "quid": wf_cat_quid, "spec": wf,
            "act_graph_quid": qm.get("0008"), "act_diag_quid": qm.get("0004"),
            "seq_mech_quid": qm.get("0008"), "seq_diag_quid": qm.get("0004"),
            "collab_diag_quid": qm.get("0004")
        }

        out.write(f'(object Class_Category "{wf_cat_name}"')
        out.indent()
        out.write(f'quid \t"{wf_cat_quid}"')
        out.write('exportControl \t"Public"')
        out.write('logical_models \t(list unit_reference_list)')

        # Activity Graph Statemachine
        out.write('statemachine \t(object Activity_Graph "Activity Graph"')
        out.indent()
        out.write(f'quid \t"{wf_data["act_graph_quid"]}"')

        q_start = qm.get("0008")
        q_end = qm.get("0008")
        step_quids = [qm.get("0008") for _ in wf["steps"]]
        out.write('states \t(list States')
        out.indent()
        out.write(f'(object State "$UNNAMED$1" quid "{q_start}" type "StartState")')
        for idx, (step_label, _) in enumerate(wf["steps"]):
            out.write(f'(object ActivityState "{step_label}" quid "{step_quids[idx]}" type "Normal")')
        out.write(f'(object State "$UNNAMED$2" quid "{q_end}" type "EndState")')
        out.dedent()
        out.write(')')  # end states

        # Partitions
        swimlane_quids = {}
        out.write('partitions \t(list Partitions')
        out.indent()
        for sw in wf["swimlanes"]:
            sw_q = qm.get("0008")
            swimlane_quids[sw] = sw_q
            out.write(f'(object Partition "{sw}"')
            out.indent()
            out.write(f'quid \t"{sw_q}"')
            out.write('activities \t(list unit_reference_list')
            out.indent()
            for s_idx, (s_label, s_sw) in enumerate(wf["steps"]):
                if s_sw == sw:
                    out.write(f'(list "Use Case View::{s_label}" "{step_quids[s_idx]}")')
            out.dedent()
            out.write('))')
            out.dedent()
        out.dedent()
        out.write(')')  # end partitions

        # Transitions with single qualified supplier/client
        trans_list = []
        out.write('transitions \t(list Transitions')
        out.indent()
        t0_q = qm.get("0008")
        trans_list.append((t0_q, q_start, step_quids[0], "$UNNAMED$1", wf["steps"][0][0]))
        out.write(f'(object State_Transition "T0"')
        out.indent()
        out.write(f'quid \t"{t0_q}"')
        out.write(f'supplier \t"Use Case View::{wf["steps"][0][0]}"')
        out.write(f'quidu \t"{step_quids[0]}"')
        out.write(f'client \t"Use Case View::$UNNAMED$1"')
        out.write(f'quidu \t"{q_start}")')
        out.dedent()
        for i in range(len(wf["steps"]) - 1):
            t_q = qm.get("0008")
            trans_list.append((t_q, step_quids[i], step_quids[i+1], wf["steps"][i][0], wf["steps"][i+1][0]))
            out.write(f'(object State_Transition "T{i+1}"')
            out.indent()
            out.write(f'quid \t"{t_q}"')
            out.write(f'supplier \t"Use Case View::{wf["steps"][i+1][0]}"')
            out.write(f'quidu \t"{step_quids[i+1]}"')
            out.write(f'client \t"Use Case View::{wf["steps"][i][0]}"')
            out.write(f'quidu \t"{step_quids[i]}")')
            out.dedent()
        tend_q = qm.get("0008")
        trans_list.append((tend_q, step_quids[-1], q_end, wf["steps"][-1][0], "$UNNAMED$2"))
        out.write(f'(object State_Transition "Tend"')
        out.indent()
        out.write(f'quid \t"{tend_q}"')
        out.write(f'supplier \t"Use Case View::$UNNAMED$2"')
        out.write(f'quidu \t"{q_end}"')
        out.write(f'client \t"Use Case View::{wf["steps"][-1][0]}"')
        out.write(f'quidu \t"{step_quids[-1]}")')
        out.dedent()
        out.dedent()
        out.write(')')  # end transitions

        # Presentations for Activity Graph
        out.write('presentations \t(list unit_reference_list')
        out.indent()
        out.write(f'(object ActivityDiagram "Activity Diagram - {wf["name"]}"')
        out.indent()
        out.write(f'quid \t"{wf_data["act_diag_quid"]}"')
        out.write(f'title \t"Activity Diagram - {wf["name"]}"')
        out.write('zoom \t100')
        out.write('max_height \t28350')
        out.write('max_width \t21600')
        out.write('origin_x \t0')
        out.write('origin_y \t0')
        out.write('items \t(list diagram_item_list')
        out.indent()

        sw_v_id = 0
        sw_x = 400
        for sw in wf["swimlanes"]:
            sw_v_id += 1
            out.write(f'(object SwimlaneView "{sw}" @{sw_v_id} location ({sw_x}, 800) quidu "{swimlane_quids[sw]}" width 500 height 1400)')
            sw_x += 520

        st_v_id = sw_v_id
        st_v_id += 1
        out.write(f'(object StateView "StartState" "$UNNAMED$1" @{st_v_id} location (400, 200) quidu "{q_start}")')

        y_act = 350
        for idx, (s_label, _) in enumerate(wf["steps"]):
            st_v_id += 1
            out.write(f'(object ActivityStateView "ActivityState" "{s_label}" @{st_v_id} location (400, {y_act}) quidu "{step_quids[idx]}" width 380 height 100)')
            y_act += 160

        st_v_id += 1
        out.write(f'(object StateView "EndState" "$UNNAMED$2" @{st_v_id} location (400, {y_act}) quidu "{q_end}")')

        tr_v_id = st_v_id
        for t_info in trans_list:
            tr_v_id += 1
            t_q = t_info[0]
            out.write(f'(object TransView "" @{tr_v_id} location (400, 300) quidu "{t_q}" line_style 0)')

        out.dedent()
        out.write(')))')  # end diagram_item_list, ActivityDiagram, presentations
        out.dedent()
        out.write(')')  # end statemachine

        # Mechanism for Sequence and Collaboration
        out.write('collaborations \t(list unit_reference_list')
        out.indent()
        out.write(f'(object Mechanism @1')
        out.indent()
        out.write('logical_models \t(list unit_reference_list')
        out.indent()

        lifeline_quids = []
        for l_name, l_class, l_quidu in wf["lifelines"]:
            l_q = qm.get("0008")
            resolved_quidu = l_quidu
            if not resolved_quidu:
                short_c = l_class.split("::")[-1]
                resolved_quidu = logical_prealloc.get(short_c, qm.get("0005"))
            lifeline_quids.append((l_name, l_q, l_class, resolved_quidu))
            out.write(f'(object Object "{l_name}"')
            out.indent()
            out.write(f'quid \t"{l_q}"')
            out.write(f'collaborator \t"{l_class}"')
            out.write(f'class \t"{l_class}"')
            out.write(f'quidu \t"{resolved_quidu}")')
            out.dedent()

        out.dedent()
        out.write(')')  # end logical_models of Mechanism

        # Messages
        msg_quids = []
        out.write('messages \t(list Messages')
        out.indent()
        for m_text, snd_idx, rcv_idx in wf["messages"]:
            m_q = qm.get("0008")
            snd_name = lifeline_quids[snd_idx][0]
            rcv_name = lifeline_quids[rcv_idx][0]
            msg_quids.append((m_q, m_text, snd_idx, rcv_idx))
            out.write(f'(object Message "{m_text}"')
            out.indent()
            out.write(f'quid \t"{m_q}"')
            out.write('frequency \t"Aperiodic"')
            out.write('synchronization \t"Simple"')
            out.write('dir \t"ToClient"')
            out.write(f'sequence \t"{len(msg_quids)}"')
            out.write(f'sender \t"{snd_name}"')
            out.write(f'receiver \t"{rcv_name}")')
            out.dedent()
        out.dedent()
        out.write(')))')  # end messages, Mechanism, collaborations
        out.dedent()

        # Presentations for Sequence & Collaboration
        out.write('logical_presentations \t(list unit_reference_list')
        out.indent()

        # 1. Sequence Diagram
        out.write(f'(object InteractionDiagram "Sequence Diagram - {wf["name"]}"')
        out.indent()
        out.write(f'quid \t"{wf_data["seq_diag_quid"]}"')
        out.write(f'title \t"Sequence Diagram - {wf["name"]}"')
        out.write('zoom \t100')
        out.write('max_height \t28350')
        out.write('max_width \t21600')
        out.write('origin_x \t0')
        out.write('origin_y \t0')
        out.write('items \t(list diagram_item_list')
        out.indent()

        seq_item_id = 1
        seq_lifeline_vids = []
        x_ll = 250
        for l_name, l_q, _, _ in lifeline_quids:
            seq_item_id += 1
            seq_lifeline_vids.append(seq_item_id)
            out.write(f'(object InterObjView "{l_name}" @{seq_item_id}')
            out.indent()
            out.write(f'location \t({x_ll}, 250)')
            out.write(f'quidu \t"{l_q}"')
            out.write('width \t240')
            out.write('height \t1400')
            out.write('icon_style \t"Icon")')
            out.dedent()
            x_ll += 350

        y_msg = 450
        for m_q, m_text, snd_idx, rcv_idx in msg_quids:
            seq_item_id += 1
            snd_vid = seq_lifeline_vids[snd_idx]
            rcv_vid = seq_lifeline_vids[rcv_idx]
            out.write(f'(object InterMessView "{m_text}" @{seq_item_id}')
            out.indent()
            out.write(f'location \t(400, {y_msg})')
            out.write(f'client \t@{snd_vid}')
            out.write(f'supplier \t@{rcv_vid}')
            out.write('line_style \t0')
            out.write(f'quidu \t"{m_q}")')
            out.dedent()
            y_msg += 120

        out.dedent()
        out.write(')')  # end items of InteractionDiagram
        out.dedent()
        out.write(')')  # end InteractionDiagram

        # 2. Collaboration Diagram
        out.write(f'(object CollaborationDiagram "Collaboration Diagram - {wf["name"]}"')
        out.indent()
        out.write(f'quid \t"{wf_data["collab_diag_quid"]}"')
        out.write(f'title \t"Collaboration Diagram - {wf["name"]}"')
        out.write('zoom \t100')
        out.write('max_height \t28350')
        out.write('max_width \t21600')
        out.write('origin_x \t0')
        out.write('origin_y \t0')
        out.write('items \t(list diagram_item_list')
        out.indent()

        collab_item_id = 1
        collab_lifeline_vids = []
        positions_2d = [(300, 300), (800, 300), (800, 700), (300, 700), (550, 500), (1050, 500), (550, 900)]
        for idx, (l_name, l_q, _, _) in enumerate(lifeline_quids):
            collab_item_id += 1
            collab_lifeline_vids.append(collab_item_id)
            c_pos = positions_2d[idx % len(positions_2d)]
            out.write(f'(object InterObjView "{l_name}" @{collab_item_id}')
            out.indent()
            out.write(f'location \t({c_pos[0]}, {c_pos[1]})')
            out.write(f'quidu \t"{l_q}"')
            out.write('width \t240')
            out.write('height \t150')
            out.write('icon_style \t"Icon")')
            out.dedent()

        for m_q, m_text, snd_idx, rcv_idx in msg_quids:
            collab_item_id += 1
            snd_vid = collab_lifeline_vids[snd_idx]
            rcv_vid = collab_lifeline_vids[rcv_idx]
            out.write(f'(object InterMessView "{m_text}" @{collab_item_id}')
            out.indent()
            out.write('location \t(550, 500)')
            out.write(f'client \t@{snd_vid}')
            out.write(f'supplier \t@{rcv_vid}')
            out.write('line_style \t0')
            out.write(f'quidu \t"{m_q}")')
            out.dedent()

        out.dedent()
        out.write(')')  # end items of CollaborationDiagram
        out.dedent()
        out.write(')')  # end CollaborationDiagram
        out.dedent()
        out.write(')')  # end logical_presentations

        out.dedent()
        out.write(')')  # end Class_Category of workflow
        wf_storage.append(wf_data)

    out.dedent()
    out.write(')')  # end logical_models of root_usecase_package

    # Presentations for root_usecase_package (BUC Diagram & Overview SYS-UC Diagram)
    out.write('logical_presentations \t(list unit_reference_list')
    out.indent()

    # Presentation 1: Business Use Case Diagram (Section 2.2.1)
    diag_buc_quid = qm.get("0004")
    out.write('(object UseCaseDiagram "Business Use Case Diagram"')
    out.indent()
    out.write(f'quid \t"{diag_buc_quid}"')
    out.write('title \t"Business Use Case Diagram"')
    out.write('zoom \t100')
    out.write('max_height \t28350')
    out.write('max_width \t21600')
    out.write('origin_x \t0')
    out.write('origin_y \t0')
    out.write('items \t(list diagram_item_list')
    out.indent()

    buc_act_vids: Dict[str, int] = {}
    v_id = 0
    buc_actor_coords = {
        "Khach hang": (350, 1000),
        "Ngan hang / Cong VietQR": (2200, 1000)
    }
    for aname, acoord in buc_actor_coords.items():
        v_id += 1
        buc_act_vids[aname] = v_id
        st = actors_dict[aname]["stereotype"]
        out.write(f'(object ClassView "Class" "Use Case View::{aname}" @{v_id}')
        out.indent()
        out.write('ShowCompartmentStereotypes \tTRUE')
        out.write(f'location \t({acoord[0]}, {acoord[1]})')
        out.write('font \t(object Font size 10 face "Arial")')
        out.write(f'label \t(object ItemLabel Parent_View @{v_id} location ({acoord[0]}, {acoord[1]+160}) anchor_loc 1 nlines 2 max_width 325 justify 0 label "{aname}")')
        out.write(f'icon \t"{st}"')
        out.write('icon_style \t"Icon"')
        out.write('line_color \t3342348')
        out.write('fill_color \t13434879')
        out.write(f'quidu \t"{actors_dict[aname]["quid"]}"')
        out.write('annotation \t8')
        out.write('autoResize \tTRUE)')
        out.dedent()

    buc_vids: Dict[str, int] = {}
    y_buc = 300
    for bname, bdata in bucs_dict.items():
        v_id += 1
        buc_vids[bname] = v_id
        out.write(f'(object UseCaseView "Use Case View::{bname}" @{v_id}')
        out.indent()
        out.write(f'location \t(1280, {y_buc})')
        out.write('font \t(object Font size 10 face "Arial")')
        out.write(f'label \t(object ItemLabel Parent_View @{v_id} location (1280, {y_buc}) anchor_loc 1 nlines 2 max_width 630 justify 0 label "{bname}")')
        out.write('icon_style \t"Icon"')
        out.write('line_color \t3342348')
        out.write('fill_color \t13434879')
        out.write(f'quidu \t"{bdata["quid"]}"')
        out.write('height \t118')
        out.write('autoResize \tTRUE)')
        out.dedent()
        y_buc += 250

    for a in buc_assocs:
        v_id += 1
        a_vid = v_id
        v_id += 1
        r1_vid = v_id
        v_id += 1
        r2_vid = v_id
        u_vid = buc_vids[a["buc"]]
        act_vid = buc_act_vids[a["actor"]]
        out.write(f'(object AssociationViewNew "{a["name"]}" @{a_vid}')
        out.indent()
        out.write('location \t(850, 750)')
        out.write('stereotype \tTRUE')
        out.write('line_color \t3342348')
        out.write(f'quidu \t"{a["quid"]}"')
        out.write('roleview_list \t(list RoleViews')
        out.indent()
        out.write(f'(object RoleView "{a["r1_name"]}" @{r1_vid}')
        out.indent()
        out.write(f'Parent_View \t@{a_vid}')
        out.write('location \t(500, 200)')
        out.write(f'quidu \t"{a["r1_quid"]}"')
        out.write(f'client \t@{a_vid}')
        out.write(f'supplier \t@{u_vid}')
        out.write('line_style \t0)')
        out.dedent()
        out.write(f'(object RoleView "{a["r2_name"]}" @{r2_vid}')
        out.indent()
        out.write(f'Parent_View \t@{a_vid}')
        out.write('location \t(500, 200)')
        out.write(f'quidu \t"{a["r2_quid"]}"')
        out.write(f'client \t@{a_vid}')
        out.write(f'supplier \t@{act_vid}')
        out.write('line_style \t0)')
        out.dedent()
        out.dedent()
        out.write('))')
        out.dedent()

    out.dedent()
    out.write(')')  # end items of BUC diagram
    out.dedent()
    out.write(')')  # end Business Use Case Diagram

    # Presentation 2: Overview System Use Case Diagram (Section 2.3.1)
    diag_sys_quid = qm.get("0004")
    out.write('(object UseCaseDiagram "System Use Case Diagram Overview"')
    out.indent()
    out.write(f'quid \t"{diag_sys_quid}"')
    out.write('title \t"System Use Case Diagram Overview"')
    out.write('zoom \t100')
    out.write('max_height \t28350')
    out.write('max_width \t21600')
    out.write('origin_x \t0')
    out.write('origin_y \t0')
    out.write('items \t(list diagram_item_list')
    out.indent()

    sys_act_vids: Dict[str, int] = {}
    v_sys_id = 0
    sys_actor_coords = {
        "Khach hang": (350, 500),
        "Ngan hang / Cong VietQR": (2200, 500),
        "Nhan vien kinh doanh": (350, 1100),
        "Ky thuat vien": (2200, 1100),
        "Quan tri vien": (350, 1600)
    }
    for aname, acoord in sys_actor_coords.items():
        v_sys_id += 1
        sys_act_vids[aname] = v_sys_id
        st = actors_dict[aname]["stereotype"]
        out.write(f'(object ClassView "Class" "Use Case View::{aname}" @{v_sys_id}')
        out.indent()
        out.write('ShowCompartmentStereotypes \tTRUE')
        out.write(f'location \t({acoord[0]}, {acoord[1]})')
        out.write('font \t(object Font size 10 face "Arial")')
        out.write(f'label \t(object ItemLabel Parent_View @{v_sys_id} location ({acoord[0]}, {acoord[1]+160}) anchor_loc 1 nlines 2 max_width 325 justify 0 label "{aname}")')
        out.write(f'icon \t"{st}"')
        out.write('icon_style \t"Icon"')
        out.write('line_color \t3342348')
        out.write('fill_color \t13434879')
        out.write(f'quidu \t"{actors_dict[aname]["quid"]}"')
        out.write('autoResize \tTRUE)')
        out.dedent()

    sys_uc_vids: Dict[str, int] = {}
    y_sys = 250
    for s_name, s_data in sys_ucs_dict.items():
        v_sys_id += 1
        sys_uc_vids[s_name] = v_sys_id
        out.write(f'(object UseCaseView "Use Case View::{s_name}" @{v_sys_id}')
        out.indent()
        out.write(f'location \t(1280, {y_sys})')
        out.write('font \t(object Font size 10 face "Arial")')
        out.write(f'label \t(object ItemLabel Parent_View @{v_sys_id} location (1280, {y_sys}) anchor_loc 1 nlines 2 max_width 630 justify 0 label "{s_name}")')
        out.write('icon_style \t"Icon"')
        out.write('line_color \t3342348')
        out.write('fill_color \t13434879')
        out.write(f'quidu \t"{s_data["quid"]}"')
        out.write('height \t118')
        out.write('autoResize \tTRUE)')
        out.dedent()
        y_sys += 180

    for a in sys_assocs:
        v_sys_id += 1
        a_vid = v_sys_id
        v_sys_id += 1
        r1_vid = v_sys_id
        v_sys_id += 1
        r2_vid = v_sys_id
        u_vid = sys_uc_vids[a["uc"]]
        act_vid = sys_act_vids[a["actor"]]
        out.write(f'(object AssociationViewNew "{a["name"]}" @{a_vid}')
        out.indent()
        out.write('location \t(850, 750)')
        out.write('stereotype \tTRUE')
        out.write('line_color \t3342348')
        out.write(f'quidu \t"{a["quid"]}"')
        out.write('roleview_list \t(list RoleViews')
        out.indent()
        out.write(f'(object RoleView "{a["r1_name"]}" @{r1_vid}')
        out.indent()
        out.write(f'Parent_View \t@{a_vid}')
        out.write('location \t(500, 200)')
        out.write(f'quidu \t"{a["r1_quid"]}"')
        out.write(f'client \t@{a_vid}')
        out.write(f'supplier \t@{u_vid}')
        out.write('line_style \t0)')
        out.dedent()
        out.write(f'(object RoleView "{a["r2_name"]}" @{r2_vid}')
        out.indent()
        out.write(f'Parent_View \t@{a_vid}')
        out.write('location \t(500, 200)')
        out.write(f'quidu \t"{a["r2_quid"]}"')
        out.write(f'client \t@{a_vid}')
        out.write(f'supplier \t@{act_vid}')
        out.write('line_style \t0)')
        out.dedent()
        out.dedent()
        out.write('))')
        out.dedent()

    out.dedent()
    out.write(')')  # end items of System Use Case Diagram Overview
    out.dedent()
    out.write(')')  # end System Use Case Diagram Overview

    out.dedent()
    out.write(')')  # end logical_presentations of root_usecase_package
    out.dedent()
    out.write(')')  # end root_usecase_package

    # =========================================================================
    # PART B: LOGICAL VIEW (root_category)
    # =========================================================================
    out.write('root_category \t(object Class_Category "Logical View"')
    out.indent()
    out.write(f'quid \t"{quid_log_pkg}"')
    out.write('exportControl \t"Public"')
    out.write('global \tTRUE')
    out.write('logical_models \t(list unit_reference_list')
    out.indent()

    # B.1. 18 Entity Classes
    entities_spec = [
        ("NguoiDung", [("MaNguoiDung", "int"), ("HoTen", "string"), ("Email", "string"), ("SoDienThoai", "string"), ("MatKhauHash", "string"), ("SoCCCD", "string"), ("MaVaiTro", "int"), ("IsBlacklisted", "bool"), ("NgayTao", "DateTime")],
                      [("DangNhap", "bool"), ("DoiMatKhau", "bool"), ("KiemTraQuyen", "bool"), ("KhoaTaiKhoan", "void")]),
        ("VaiTro", [("MaVaiTro", "int"), ("TenVaiTro", "string"), ("MoTa", "string")],
                   [("LayDanhSachQuyen", "List<string>"), ("GanQuyen", "void")]),
        ("SanPham", [("MaSanPham", "int"), ("TenSanPham", "string"), ("DonGiaNgay", "decimal"), ("DonGiaThang", "decimal"), ("TienCoc", "decimal"), ("MaLoai", "int"), ("MoTaCaiDat", "string")],
                    [("TinhGiaThue", "decimal"), ("KiemTraSoLuongTon", "int"), ("CapNhatGia", "void")]),
        ("ThietBi", [("MaThietBi", "int"), ("MaSanPham", "int"), ("SoSerial", "string"), ("TrangThai", "int"), ("ViTriKho", "string"), ("NgayNhapKho", "DateTime")],
                    [("CapNhatTrangThai", "void"), ("KiemTraKhaDung", "bool"), ("ChuyenKho", "void"), ("GiuCho24h", "void")]),
        ("LoaiThietBi", [("MaLoai", "int"), ("TenLoai", "string"), ("MoTa", "string")],
                        [("LayDanhSachSanPham", "List<SanPham>"), ("ThemLoaiMoi", "void")]),
        ("KhuyenMai", [("MaKhuyenMai", "int"), ("Code", "string"), ("PhanTramGiam", "decimal"), ("NgayHetHan", "DateTime"), ("SoLuongConLai", "int"), ("TrangThai", "bool")],
                      [("KiemTraHopLe", "bool"), ("TinhSoTienGiam", "decimal"), ("SuDungVoucher", "void")]),
        ("ThongBao", [("MaThongBao", "int"), ("MaNguoiDung", "int"), ("TieuDe", "string"), ("NoiDung", "string"), ("DaDoc", "bool"), ("NgayTao", "DateTime")],
                     [("DanhDauDaDoc", "void"), ("GuiThongBao", "void")]),
        ("HopDong", [("MaHopDong", "int"), ("MaKhachHang", "int"), ("NgayBatDau", "DateTime"), ("NgayKetThuc", "DateTime"), ("TongTien", "decimal"), ("TienDaCoc", "decimal"), ("TienCocBaoDamMay", "decimal"), ("TrangThai", "int"), ("NhomTuoiNo", "int"), ("ChuKyKhachHang", "string"), ("TrangThaiHoanCoc", "int"), ("HanChotKy", "DateTime")],
                    [("DuyetHopDong", "void"), ("TinhTongTien", "decimal"), ("GiaHanHopDong", "void"), ("ThanhLy", "void"), ("HuyHopDong", "void"), ("QuyetToanHoanCoc", "decimal")]),
        ("ChiTietHopDong", [("MaChiTiet", "int"), ("MaHopDong", "int"), ("MaThietBi", "int"), ("GiaChotThue", "decimal"), ("GhiChu", "string")],
                           [("LayThongTinThietBi", "ThietBi"), ("CapNhatGiaThue", "void")]),
        ("KyHanThanhToan", [("MaKyHan", "int"), ("MaHopDong", "int"), ("SoKyHan", "int"), ("SoTienPhai", "decimal"), ("SoTienDaTra", "decimal"), ("TienPhat", "decimal"), ("NgayDenHan", "DateTime"), ("TrangThai", "int")],
                           [("TinhPhatTreHan", "decimal"), ("GachNo", "void"), ("KiemTraQuaHan", "bool")]),
        ("PhieuThu", [("MaPhieuThu", "int"), ("MaHopDong", "int"), ("MaKyHan", "int?"), ("SoTien", "decimal"), ("LoaiPhieu", "int"), ("HinhThucThanhToan", "int"), ("NgayGiaoDich", "DateTime"), ("MaGiaoDichNganHang", "string"), ("MaNhanVienThu", "int?")],
                     [("XacNhanThu", "void"), ("InPhieuThu", "byte[]"), ("TaoPhieuThuTuDong", "void")]),
        ("PhieuChi", [("MaPhieuChi", "int"), ("MaHopDong", "int"), ("SoTienHoanTra", "decimal"), ("NgayChi", "DateTime"), ("LyDoChi", "string"), ("MaNhanVienChi", "int"), ("HinhThucHoan", "int")],
                     [("InPhieuChi", "byte[]"), ("ThucHienHoanTien", "bool")]),
        ("PhieuBaoTri", [("MaPhieu", "int"), ("MaHopDong", "int"), ("MaThietBi", "int"), ("MaNhanVienKyThuat", "int?"), ("MoTaSuCo", "string"), ("HinhAnhSuCo", "string"), ("ChiPhi", "decimal"), ("PhiDenBu", "decimal"), ("TrangThai", "int"), ("NgayTao", "DateTime"), ("SLAStartTime", "DateTime")],
                        [("TiepNhan", "void"), ("TamDungTinhTienSLA", "void"), ("PhanCongKTV", "void"), ("HoanTatSuaChua", "void")]),
        ("LichSuThietBi", [("MaLichSu", "int"), ("MaThietBi", "int"), ("HanhDong", "string"), ("NgayTao", "DateTime"), ("GhiChu", "string"), ("NguoiThucHien", "string")],
                          [("GhiNhatKy", "void"), ("TruyVanLichSu", "List<LichSuThietBi>")]),
        ("BienBanBanGiao", [("MaBienBan", "int"), ("MaHopDong", "int"), ("MaThietBi", "int"), ("LoaiBienBan", "int"), ("TinhTrangNgoaiQuan", "string"), ("ChuKyKhach", "string"), ("ChuKyNhanVien", "string"), ("NgayLap", "DateTime"), ("TepDinhKemPDF", "string")],
                           [("KyCanvas", "void"), ("XuatPDF", "byte[]"), ("DongKiem", "bool")]),
        ("YeuCauGiaHan", [("MaYeuCau", "int"), ("MaHopDong", "int"), ("SoNgayGiaHan", "int"), ("LyDo", "string"), ("TrangThai", "int"), ("NgayTao", "DateTime"), ("NguoiDuyet", "int?")],
                         [("TaoYeuCau", "void"), ("PheDuyet", "void"), ("TuChoi", "void")]),
        ("PhanCongCongViec", [("MaPhanCong", "int"), ("MaPhieuBaoTri", "int"), ("MaKyThuatVien", "int"), ("NgayGiao", "DateTime"), ("HanHoanThanh", "DateTime"), ("TrangThai", "int"), ("GhiChu", "string")],
                             [("GiaoViec", "void"), ("CapNhatTienDo", "void"), ("NghiemThuCongViec", "void")]),
        ("LichSuNhacNo", [("MaNhacNo", "int"), ("MaHopDong", "int"), ("MaKyHan", "int"), ("NgayNhac", "DateTime"), ("HinhThuc", "string"), ("NoiDung", "string"), ("KetQua", "string"), ("NhanVienNhac", "int?")],
                         [("GhiLichSuNhacNo", "void"), ("GuiSMSNhacNo", "void"), ("TaoCuocGoi", "void")])
    ]

    entity_quids: Dict[str, str] = {}
    for ename, attrs, ops in entities_spec:
        eq = logical_prealloc.get(ename, qm.get("0005"))
        entity_quids[ename] = eq
        out.write(f'(object Class "{ename}"')
        out.indent()
        out.write(f'quid \t"{eq}"')
        out.write('stereotype \t"entity"')
        out.write('class_attributes \t(list class_attribute_list')
        out.indent()
        for an, at in attrs:
            aq = qm.get("0007")
            out.write(f'(object Class_Attribute "{an}"')
            out.indent()
            out.write(f'quid \t"{aq}"')
            out.write(f'type \t"{at}"')
            out.write('exportControl \t"Public")')
            out.dedent()
        out.dedent()
        out.write(')')  # end class_attributes

        out.write('operations \t(list Operations')
        out.indent()
        for on, ort in ops:
            oq = qm.get("0006")
            out.write(f'(object Operation "{on}"')
            out.indent()
            out.write(f'quid \t"{oq}"')
            out.write(f'result \t"{ort}"')
            out.write('concurrency \t"Sequential"')
            out.write('opExportControl \t"Public"')
            out.write('uid \t0)')
            out.dedent()
        out.dedent()
        out.write(')')  # end operations

        # Chapter 4 State Machine attached to ThietBi
        if ename == "ThietBi":
            sm_dev_q = qm.get("0008")
            sm_dev_diag_q = qm.get("0004")
            out.write('statemachine \t(object State_Machine "Device Lifecycle State Machine"')
            out.indent()
            out.write(f'quid \t"{sm_dev_q}"')
            dev_states = [
                ("0. San sang", "Thiet bi trong kho, da kiem dinh san sang cho thue"),
                ("3. Giu cho", "Thiet bi duoc khoa giu cho 24h trong don dat thue"),
                ("1. Dang thue", "Khach da nhan may va dang trong thoi gian thue"),
                ("2. Bao tri", "Thiet bi dang duoc ky thuat vien kiem tra sua chua"),
                ("4. Hong / Thanh ly", "Thiet bi hong nang khong the phuc hoi hoac bi mat")
            ]
            dev_st_quids = {}
            dev_q_start = qm.get("0008")
            dev_q_end = qm.get("0008")
            out.write('states \t(list States')
            out.indent()
            out.write(f'(object State "$UNNAMED$1" quid "{dev_q_start}" type "StartState")')
            for ds, ds_doc in dev_states:
                dsq = qm.get("0008")
                dev_st_quids[ds] = dsq
                out.write(f'(object State "{ds}" quid "{dsq}" type "Normal" documentation "{ds_doc}")')
            out.write(f'(object State "$UNNAMED$2" quid "{dev_q_end}" type "EndState")')
            out.dedent()
            out.write(')')  # end states

            dev_transitions = [
                ("Khoi tao", "$UNNAMED$1", dev_q_start, "0. San sang", dev_st_quids["0. San sang"]),
                ("Dat thue giu cho 24h", "0. San sang", dev_st_quids["0. San sang"], "3. Giu cho", dev_st_quids["3. Giu cho"]),
                ("Het han 24h / Huy don", "3. Giu cho", dev_st_quids["3. Giu cho"], "0. San sang", dev_st_quids["0. San sang"]),
                ("Ban giao & Ky bien ban", "3. Giu cho", dev_st_quids["3. Giu cho"], "1. Dang thue", dev_st_quids["1. Dang thue"]),
                ("Bao su co / Dinh ky", "1. Dang thue", dev_st_quids["1. Dang thue"], "2. Bao tri", dev_st_quids["2. Bao tri"]),
                ("Sua xong / Tiep tuc thue", "2. Bao tri", dev_st_quids["2. Bao tri"], "1. Dang thue", dev_st_quids["1. Dang thue"]),
                ("Tra may nghiem thu dat", "1. Dang thue", dev_st_quids["1. Dang thue"], "0. San sang", dev_st_quids["0. San sang"]),
                ("Hong nang / Mat may", "1. Dang thue", dev_st_quids["1. Dang thue"], "4. Hong / Thanh ly", dev_st_quids["4. Hong / Thanh ly"]),
                ("Khong the sua chua", "2. Bao tri", dev_st_quids["2. Bao tri"], "4. Hong / Thanh ly", dev_st_quids["4. Hong / Thanh ly"]),
                ("Thanh ly xong", "4. Hong / Thanh ly", dev_st_quids["4. Hong / Thanh ly"], "$UNNAMED$2", dev_q_end)
            ]
            dev_trans_storage = []
            out.write('transitions \t(list Transitions')
            out.indent()
            for tname, cname, cq, sname, sq in dev_transitions:
                tq = qm.get("0008")
                dev_trans_storage.append((tq, tname, cname, cq, sname, sq))
                out.write(f'(object State_Transition "{tname}"')
                out.indent()
                out.write(f'quid \t"{tq}"')
                out.write(f'supplier \t"Logical View::{sname}"')
                out.write(f'quidu \t"{sq}"')
                out.write(f'client \t"Logical View::{cname}"')
                out.write(f'quidu \t"{cq}")')
                out.dedent()
            out.dedent()
            out.write(')')  # end transitions

            out.write('presentations \t(list unit_reference_list')
            out.indent()
            out.write('(object StateDiagram "Device Lifecycle State Machine"')
            out.indent()
            out.write(f'quid \t"{sm_dev_diag_q}"')
            out.write('title \t"Device Lifecycle State Machine"')
            out.write('zoom \t100')
            out.write('max_height \t28350')
            out.write('max_width \t21600')
            out.write('origin_x \t0')
            out.write('origin_y \t0')
            out.write('items \t(list diagram_item_list')
            out.indent()

            dev_v_id = 1
            out.write(f'(object StateView "StartState" "$UNNAMED$1" @{dev_v_id} location (200, 400) quidu "{dev_q_start}")')
            dev_st_vids = {"$UNNAMED$1": dev_v_id}
            dev_coords = {
                "0. San sang": (600, 400),
                "3. Giu cho": (1100, 400),
                "1. Dang thue": (1600, 400),
                "2. Bao tri": (1100, 750),
                "4. Hong / Thanh ly": (1600, 750)
            }
            for ds, coord in dev_coords.items():
                dev_v_id += 1
                dev_st_vids[ds] = dev_v_id
                out.write(f'(object StateView "Normal" "{ds}" @{dev_v_id} location ({coord[0]}, {coord[1]}) quidu "{dev_st_quids[ds]}" width 260 height 120)')

            dev_v_id += 1
            dev_st_vids["$UNNAMED$2"] = dev_v_id
            out.write(f'(object StateView "EndState" "$UNNAMED$2" @{dev_v_id} location (2050, 750) quidu "{dev_q_end}")')

            for tq, tname, cname, cq, sname, sq in dev_trans_storage:
                dev_v_id += 1
                out.write(f'(object TransView "{tname}" @{dev_v_id} location (1000, 500) client @{dev_st_vids[cname]} supplier @{dev_st_vids[sname]} line_style 0 quidu "{tq}")')

            out.dedent()
            out.write(')))')  # end items, StateDiagram, presentations
            out.dedent()
            out.write(')')  # end statemachine

        # Chapter 4 State Machine attached to PhieuBaoTri
        if ename == "PhieuBaoTri":
            sm_pbt_q = qm.get("0008")
            sm_pbt_diag_q = qm.get("0004")
            out.write('statemachine \t(object State_Machine "Maintenance Ticket SLA State Machine"')
            out.indent()
            out.write(f'quid \t"{sm_pbt_q}"')
            pbt_states = [
                ("0. Tiep nhan", "Ticket duoc tao boi khach hang va cho phan cong"),
                ("1. Dang xu ly", "KTV da tiep nhan va dang sua chua tai cho"),
                ("2. Cho linh kien", "Tam dung SLA do cho dat linh kien thay the"),
                ("3. Hoan tat", "Da sua chua xong, khach dong kiem va dong ticket")
            ]
            pbt_st_quids = {}
            pbt_q_start = qm.get("0008")
            pbt_q_end = qm.get("0008")
            out.write('states \t(list States')
            out.indent()
            out.write(f'(object State "$UNNAMED$1" quid "{pbt_q_start}" type "StartState")')
            for ps, ps_doc in pbt_states:
                psq = qm.get("0008")
                pbt_st_quids[ps] = psq
                out.write(f'(object State "{ps}" quid "{psq}" type "Normal" documentation "{ps_doc}")')
            out.write(f'(object State "$UNNAMED$2" quid "{pbt_q_end}" type "EndState")')
            out.dedent()
            out.write(')')  # end states

            pbt_transitions = [
                ("Tao ticket", "$UNNAMED$1", pbt_q_start, "0. Tiep nhan", pbt_st_quids["0. Tiep nhan"]),
                ("Phan cong KTV", "0. Tiep nhan", pbt_st_quids["0. Tiep nhan"], "1. Dang xu ly", pbt_st_quids["1. Dang xu ly"]),
                ("Cho linh kien (Tam dung SLA)", "1. Dang xu ly", pbt_st_quids["1. Dang xu ly"], "2. Cho linh kien", pbt_st_quids["2. Cho linh kien"]),
                ("Co linh kien (Tiep tuc SLA)", "2. Cho linh kien", pbt_st_quids["2. Cho linh kien"], "1. Dang xu ly", pbt_st_quids["1. Dang xu ly"]),
                ("Sua xong & Nghiem thu", "1. Dang xu ly", pbt_st_quids["1. Dang xu ly"], "3. Hoan tat", pbt_st_quids["3. Hoan tat"]),
                ("Dong ticket", "3. Hoan tat", pbt_st_quids["3. Hoan tat"], "$UNNAMED$2", pbt_q_end)
            ]
            pbt_trans_storage = []
            out.write('transitions \t(list Transitions')
            out.indent()
            for tname, cname, cq, sname, sq in pbt_transitions:
                tq = qm.get("0008")
                pbt_trans_storage.append((tq, tname, cname, cq, sname, sq))
                out.write(f'(object State_Transition "{tname}"')
                out.indent()
                out.write(f'quid \t"{tq}"')
                out.write(f'supplier \t"Logical View::{sname}"')
                out.write(f'quidu \t"{sq}"')
                out.write(f'client \t"Logical View::{cname}"')
                out.write(f'quidu \t"{cq}")')
                out.dedent()
            out.dedent()
            out.write(')')  # end transitions

            out.write('presentations \t(list unit_reference_list')
            out.indent()
            out.write('(object StateDiagram "Maintenance Ticket SLA State Machine"')
            out.indent()
            out.write(f'quid \t"{sm_pbt_diag_q}"')
            out.write('title \t"Maintenance Ticket SLA State Machine"')
            out.write('zoom \t100')
            out.write('max_height \t28350')
            out.write('max_width \t21600')
            out.write('origin_x \t0')
            out.write('origin_y \t0')
            out.write('items \t(list diagram_item_list')
            out.indent()

            pbt_v_id = 1
            out.write(f'(object StateView "StartState" "$UNNAMED$1" @{pbt_v_id} location (200, 400) quidu "{pbt_q_start}")')
            pbt_st_vids = {"$UNNAMED$1": pbt_v_id}
            pbt_coords = {
                "0. Tiep nhan": (600, 400),
                "1. Dang xu ly": (1100, 400),
                "2. Cho linh kien": (1100, 750),
                "3. Hoan tat": (1600, 400)
            }
            for ps, coord in pbt_coords.items():
                pbt_v_id += 1
                pbt_st_vids[ps] = pbt_v_id
                out.write(f'(object StateView "Normal" "{ps}" @{pbt_v_id} location ({coord[0]}, {coord[1]}) quidu "{pbt_st_quids[ps]}" width 260 height 120)')

            pbt_v_id += 1
            pbt_st_vids["$UNNAMED$2"] = pbt_v_id
            out.write(f'(object StateView "EndState" "$UNNAMED$2" @{pbt_v_id} location (2000, 400) quidu "{pbt_q_end}")')

            for tq, tname, cname, cq, sname, sq in pbt_trans_storage:
                pbt_v_id += 1
                out.write(f'(object TransView "{tname}" @{pbt_v_id} location (1000, 500) client @{pbt_st_vids[cname]} supplier @{pbt_st_vids[sname]} line_style 0 quidu "{tq}")')

            out.dedent()
            out.write(')))')  # end items, StateDiagram, presentations
            out.dedent()
            out.write(')')  # end statemachine

        out.dedent()
        out.write(')')  # end Class

    # B.2. 15 Boundary Classes
    boundaries_spec = [
        "DangKyView", "DangNhapView", "GioHangView", "DatThueView", "ThanhToanView",
        "VietQRModalView", "BanGiaoView", "KyCanvasModalView", "SuCoTicketView",
        "PhanCongBaoTriView", "GiaHanView", "SoCongNoView", "NghiemThuView",
        "HoanCocView", "BaoCaoBIView"
    ]
    boundary_quids: Dict[str, str] = {}
    for bname in boundaries_spec:
        bq = logical_prealloc.get(bname, qm.get("0005"))
        boundary_quids[bname] = bq
        out.write(f'(object Class "{bname}"')
        out.indent()
        out.write(f'quid \t"{bq}"')
        out.write('stereotype \t"boundary"')
        out.write(f'documentation \t"Lop giao dien {bname}")')
        out.dedent()

    # B.3. 7 Control Classes
    controls_spec = [
        ("AccountControl", [("DangKyTaiKhoan", "bool"), ("XacThucDangNhap", "bool"), ("KiemTraClaims", "ClaimsPrincipal")]),
        ("CartControl", [("ThemGioHang", "void"), ("KiemTraTonKhoVaGiuCho", "bool"), ("GiaiPhongGiuChoQuaHan", "void")]),
        ("PaymentControl", [("TiepNhanBankingWebhook", "IActionResult"), ("GachNoTuDong", "bool"), ("XacThucChuKyNapas", "bool")]),
        ("HopDongControl", [("TaoHopDongMoi", "HopDong"), ("LuuChuKyCanvas", "void"), ("DuyetHopDong", "void"), ("QuyetToanHoanCoc", "void")]),
        ("BaoTriControl", [("TiepNhanTicket", "PhieuBaoTri"), ("KichHoatTamDungSLA", "void"), ("CapNhatPhiDenBu", "void")]),
        ("PhanCongControl", [("PhanCongKTV", "void"), ("CapNhatTienDoCongViec", "void")]),
        ("CongNoControl", [("PhanKyNoGiaHan", "void"), ("TinhPhatTreHan01PhanTram", "decimal"), ("KhoaTaiKhoanBlacklist", "void")])
    ]
    control_quids: Dict[str, str] = {}
    for cname, cops in controls_spec:
        cq = logical_prealloc.get(cname, qm.get("0005"))
        control_quids[cname] = cq
        out.write(f'(object Class "{cname}"')
        out.indent()
        out.write(f'quid \t"{cq}"')
        out.write('stereotype \t"control"')
        out.write('operations \t(list Operations')
        out.indent()
        for on, ort in cops:
            oq = qm.get("0006")
            out.write(f'(object Operation "{on}" quid "{oq}" result "{ort}" concurrency "Sequential" opExportControl "Public" uid 0)')
        out.dedent()
        out.write('))')
        out.dedent()

    # Associations between Analysis Classes (BCE Model)
    bce_assocs_spec = [
        ("DangKyView", "AccountControl"),
        ("AccountControl", "NguoiDung"),
        ("DatThueView", "CartControl"),
        ("CartControl", "ThietBi"),
        ("CartControl", "HopDong"),
        ("ThanhToanView", "PaymentControl"),
        ("PaymentControl", "PhieuThu"),
        ("PaymentControl", "HopDong"),
        ("BanGiaoView", "HopDongControl"),
        ("HopDongControl", "BienBanBanGiao"),
        ("HopDongControl", "ThietBi"),
        ("HopDongControl", "PhieuChi"),
        ("SuCoTicketView", "BaoTriControl"),
        ("BaoTriControl", "PhieuBaoTri"),
        ("PhanCongBaoTriView", "PhanCongControl"),
        ("PhanCongControl", "PhanCongCongViec"),
        ("GiaHanView", "CongNoControl"),
        ("CongNoControl", "YeuCauGiaHan"),
        ("CongNoControl", "KyHanThanhToan"),
        ("SoCongNoView", "CongNoControl"),
        ("NghiemThuView", "HopDongControl"),
        ("HoanCocView", "HopDongControl"),
        # Entity-to-Entity relations
        ("VaiTro", "NguoiDung"),
        ("LoaiThietBi", "SanPham"),
        ("SanPham", "ThietBi"),
        ("HopDong", "ChiTietHopDong"),
        ("ChiTietHopDong", "ThietBi"),
        ("HopDong", "KyHanThanhToan"),
        ("HopDong", "PhieuThu"),
        ("HopDong", "PhieuChi"),
        ("HopDong", "PhieuBaoTri"),
        ("ThietBi", "LichSuThietBi")
    ]
    bce_assocs: List[Dict[str, str]] = []
    for idx, (c1, c2) in enumerate(bce_assocs_spec):
        aq = qm.get("0003")
        r1q = qm.get("0003")
        r2q = qm.get("0003")
        aname = f"$UNNAMED${1000 + idx}"
        r1n = f"$UNNAMED${2000 + idx*2 + 1}"
        r2n = f"$UNNAMED${2000 + idx*2 + 2}"
        c1q = boundary_quids.get(c1) or control_quids.get(c1) or entity_quids.get(c1)
        c2q = boundary_quids.get(c2) or control_quids.get(c2) or entity_quids.get(c2)
        bce_assocs.append({
            "name": aname, "quid": aq,
            "r1_name": r1n, "r1_quid": r1q, "c1": c1, "c1_quid": c1q,
            "r2_name": r2n, "r2_quid": r2q, "c2": c2, "c2_quid": c2q
        })
        out.write(f'(object Association "{aname}"')
        out.indent()
        out.write(f'quid \t"{aq}"')
        out.write('roles \t(list role_list')
        out.indent()
        out.write(f'(object Role "{r1n}"')
        out.indent()
        out.write(f'quid \t"{r1q}"')
        out.write(f'supplier \t"Logical View::{c2}"')
        out.write(f'quidu \t"{c2q}"')
        out.write('is_navigable \tTRUE)')
        out.dedent()
        out.write(f'(object Role "{r2n}"')
        out.indent()
        out.write(f'quid \t"{r2q}"')
        out.write(f'supplier \t"Logical View::{c1}"')
        out.write(f'quidu \t"{c1q}")')
        out.dedent()
        out.dedent()
        out.write('))')
        out.dedent()

    # B.4. 3-Tier Design Packages (Presentation Tier, Business Logic Tier, Data Access Tier)
    design_packages_spec = [
        {
            "name": "Presentation Tier",
            "doc": "Controllers va ViewModels xu ly HTTP request, Binding va tra ve View.",
            "classes": [
                ("AccountController", "class", [("Register", "Task<IActionResult>"), ("Login", "Task<IActionResult>"), ("Logout", "Task<IActionResult>")]),
                ("CartController", "class", [("AddToCart", "IActionResult"), ("Checkout", "Task<IActionResult>"), ("SignContract", "Task<IActionResult>")]),
                ("HopDongController", "class", [("Index", "Task<IActionResult>"), ("Details", "Task<IActionResult>"), ("KyHopDong", "Task<IActionResult>"), ("HoanCoc", "Task<IActionResult>")]),
                ("PaymentController", "class", [("BankingWebhook", "Task<IActionResult>"), ("GenerateVietQR", "IActionResult")]),
                ("CongNoController", "class", [("Index", "Task<IActionResult>"), ("NhacNo", "Task<IActionResult>"), ("PayInstallment", "Task<IActionResult>"), ("ExportExcel", "Task<IActionResult>")]),
                ("ThietBiController", "class", [("Index", "Task<IActionResult>"), ("Details", "Task<IActionResult>"), ("Create", "Task<IActionResult>")]),
                ("BaoTriController", "class", [("CreateTicket", "Task<IActionResult>"), ("CompleteMaintenance", "Task<IActionResult>"), ("MyTasks", "Task<IActionResult>")]),
                ("PhanCongController", "class", [("Index", "Task<IActionResult>"), ("AssignTask", "Task<IActionResult>")]),
                ("DocumentController", "class", [("DownloadContractPdf", "Task<IActionResult>")]),
                ("SanPhamController", "class", [("Index", "Task<IActionResult>"), ("Details", "Task<IActionResult>")]),
                ("ThongKeController", "class", [("Index", "Task<IActionResult>"), ("ExportBIExcel", "Task<IActionResult>")]),
                ("RegisterVM", "class", []),
                ("LoginVM", "class", []),
                ("CheckoutVM", "class", []),
                ("CreateContractVM", "class", []),
                ("HoanCocVM", "class", []),
                ("AssignTaskVM", "class", []),
                ("CreateTicketVM", "class", []),
                ("ThietBiVM", "class", [])
            ]
        },
        {
            "name": "Business Logic Tier",
            "doc": "Cac dich vu nghiep vu, thuat toan tinh no, kiem tra khoa luong va SLA.",
            "classes": [
                ("InventoryReservationBackgroundService", "class", [("ExecuteAsync", "Task"), ("ScanAndReleaseExpiredReservations", "Task")]),
                ("VietQRService", "class", [("GenerateEMVCoPayload", "string"), ("ComputeCRC16CCITT", "string")]),
                ("DebtCalculationHelper", "class", [("CalculateAgingTier", "int"), ("CalculateLateFee", "decimal"), ("CalculateDepositSettlement", "decimal"), ("IsCustomerBlacklisted", "bool")]),
                ("MagicBytesValidator", "class", [("IsValidImageFile", "bool"), ("InspectHeaderBytes", "bool")]),
                ("SLATimerService", "class", [("StartTimer", "void"), ("PauseTimer", "void"), ("ResumeTimer", "void")]),
                ("PdfExportService", "class", [("GenerateHandoverContractPdf", "byte[]")]),
                ("CookieAuthHandler", "class", [("SignInAsync", "Task"), ("SignOutAsync", "Task")]),
                ("CartInventoryLock", "class", [("WaitAsync", "Task"), ("Release", "void")]),
                ("PaymentIdempotencyLock", "class", [("WaitAsync", "Task"), ("Release", "void")])
            ]
        },
        {
            "name": "Data Access Tier",
            "doc": "DbContext ket noi co so du lieu SQL Server va cac Entity anh xa bang vat ly.",
            "classes": [
                ("ApplicationDbContext", "class", [("SaveChangesAsync", "Task<int>"), ("BeginTransactionAsync", "Task<IDbContextTransaction>")])
            ]
        }
    ]

    tier_storage: List[Dict[str, Any]] = []
    for tpkg in design_packages_spec:
        tp_name = tpkg["name"]
        tp_quid = qm.get("0005")
        t_data = {"name": tp_name, "quid": tp_quid, "classes": {}, "diag_quid": qm.get("0004")}
        out.write(f'(object Class_Category "{tp_name}"')
        out.indent()
        out.write(f'quid \t"{tp_quid}"')
        out.write('exportControl \t"Public"')
        out.write('logical_models \t(list unit_reference_list')
        out.indent()

        for cname, ctype, cops in tpkg["classes"]:
            cq = qm.get("0005")
            t_data["classes"][cname] = cq
            out.write(f'(object Class "{cname}"')
            out.indent()
            out.write(f'quid \t"{cq}"')
            out.write(f'documentation \t"Lop thiet ke {cname} thuoc {tp_name}"')
            if cops:
                out.write('operations \t(list Operations')
                out.indent()
                for on, ort in cops:
                    oq = qm.get("0006")
                    out.write(f'(object Operation "{on}" quid "{oq}" result "{ort}" concurrency "Sequential" opExportControl "Public" uid 0)')
                out.dedent()
                out.write(')')
            out.write(')')  # end Class
            out.dedent()

        out.dedent()
        out.write(')')  # end logical_models

        # Tier Class Diagram
        out.write('logical_presentations \t(list unit_reference_list')
        out.indent()
        out.write(f'(object ClassDiagram "{tp_name} Class Diagram"')
        out.indent()
        out.write(f'quid \t"{t_data["diag_quid"]}"')
        out.write(f'title \t"{tp_name} Class Diagram"')
        out.write('zoom \t100')
        out.write('max_height \t28350')
        out.write('max_width \t21600')
        out.write('origin_x \t0')
        out.write('origin_y \t0')
        out.write('items \t(list diagram_item_list')
        out.indent()

        tier_vid = 0
        tx = 350
        ty = 300
        for cn, cq in t_data["classes"].items():
            tier_vid += 1
            out.write(f'(object ClassView "Class" "Logical View::{tp_name}::{cn}" @{tier_vid}')
            out.indent()
            out.write('ShowCompartmentStereotypes \tTRUE')
            out.write('IncludeAttribute \tTRUE')
            out.write('IncludeOperation \tTRUE')
            out.write(f'location \t({tx}, {ty})')
            out.write('font \t(object Font size 10 face "Arial")')
            out.write(f'label \t(object ItemLabel Parent_View @{tier_vid} location ({tx}, {ty-60}) anchor_loc 1 nlines 2 max_width 350 justify 0 label "{cn}")')
            out.write('line_color \t3342348')
            out.write('fill_color \t13434879')
            out.write(f'quidu \t"{cq}"')
            out.write('width \t380')
            out.write('height \t200')
            out.write('autoResize \tTRUE)')
            out.dedent()
            tx += 420
            if tx > 1800:
                tx = 350
                ty += 280

        out.dedent()
        out.write(')))')  # end items, ClassDiagram, logical_presentations
        out.dedent()
        out.write(')')  # end Class_Category
        tier_storage.append(t_data)

    out.dedent()
    out.write(')')  # end logical_models of root_category

    # Presentations for root_category
    out.write('logical_presentations \t(list unit_reference_list')
    out.indent()

    # Presentation 1: BCE Analysis Class Diagram (Section 2.4)
    diag_bce_quid = qm.get("0004")
    out.write('(object ClassDiagram "Analysis Class Diagram (BCE Model)"')
    out.indent()
    out.write(f'quid \t"{diag_bce_quid}"')
    out.write('title \t"Analysis Class Diagram (BCE Model)"')
    out.write('zoom \t100')
    out.write('max_height \t28350')
    out.write('max_width \t21600')
    out.write('origin_x \t0')
    out.write('origin_y \t0')
    out.write('items \t(list diagram_item_list')
    out.indent()

    bce_vids: Dict[str, int] = {}
    v_bce_id = 0

    # Layout Boundaries on Top row
    bx = 300
    by = 300
    for bn in boundaries_spec:
        v_bce_id += 1
        bce_vids[bn] = v_bce_id
        out.write(f'(object ClassView "Class" "Logical View::{bn}" @{v_bce_id}')
        out.indent()
        out.write('ShowCompartmentStereotypes \tTRUE')
        out.write(f'location \t({bx}, {by})')
        out.write('font \t(object Font size 10 face "Arial")')
        out.write(f'label \t(object ItemLabel Parent_View @{v_bce_id} location ({bx}, {by-50}) anchor_loc 1 nlines 2 max_width 300 justify 0 label "{bn}")')
        out.write('icon \t"boundary"')
        out.write('icon_style \t"Icon"')
        out.write('line_color \t3342348')
        out.write('fill_color \t13434879')
        out.write(f'quidu \t"{boundary_quids[bn]}"')
        out.write('autoResize \tTRUE)')
        out.dedent()
        bx += 350
        if bx > 2400:
            bx = 300
            by += 200

    # Layout Controls in Middle row
    cx = 300
    cy = by + 280
    for cn, _ in controls_spec:
        v_bce_id += 1
        bce_vids[cn] = v_bce_id
        out.write(f'(object ClassView "Class" "Logical View::{cn}" @{v_bce_id}')
        out.indent()
        out.write('ShowCompartmentStereotypes \tTRUE')
        out.write(f'location \t({cx}, {cy})')
        out.write('font \t(object Font size 10 face "Arial")')
        out.write(f'label \t(object ItemLabel Parent_View @{v_bce_id} location ({cx}, {cy-50}) anchor_loc 1 nlines 2 max_width 300 justify 0 label "{cn}")')
        out.write('icon \t"control"')
        out.write('icon_style \t"Icon"')
        out.write('line_color \t3342348')
        out.write('fill_color \t13434879')
        out.write(f'quidu \t"{control_quids[cn]}"')
        out.write('autoResize \tTRUE)')
        out.dedent()
        cx += 350

    # Layout Entities in Bottom rows
    ex = 300
    ey = cy + 280
    for en, _, _ in entities_spec:
        v_bce_id += 1
        bce_vids[en] = v_bce_id
        out.write(f'(object ClassView "Class" "Logical View::{en}" @{v_bce_id}')
        out.indent()
        out.write('ShowCompartmentStereotypes \tTRUE')
        out.write('IncludeAttribute \tTRUE')
        out.write('IncludeOperation \tTRUE')
        out.write(f'location \t({ex}, {ey})')
        out.write('font \t(object Font size 10 face "Arial")')
        out.write(f'label \t(object ItemLabel Parent_View @{v_bce_id} location ({ex}, {ey-60}) anchor_loc 1 nlines 2 max_width 320 justify 0 label "{en}")')
        out.write('icon \t"entity"')
        out.write('icon_style \t"Icon"')
        out.write('line_color \t3342348')
        out.write('fill_color \t13434879')
        out.write(f'quidu \t"{entity_quids[en]}"')
        out.write('width \t340')
        out.write('height \t180')
        out.write('autoResize \tTRUE)')
        out.dedent()
        ex += 380
        if ex > 2400:
            ex = 300
            ey += 240

    # Layout Association lines in BCE diagram
    for a in bce_assocs:
        v_bce_id += 1
        avid = v_bce_id
        v_bce_id += 1
        r1vid = v_bce_id
        v_bce_id += 1
        r2vid = v_bce_id
        c1vid = bce_vids[a["c1"]]
        c2vid = bce_vids[a["c2"]]
        out.write(f'(object AssociationViewNew "{a["name"]}" @{avid}')
        out.indent()
        out.write('location \t(1000, 800)')
        out.write('stereotype \tTRUE')
        out.write('line_color \t3342348')
        out.write(f'quidu \t"{a["quid"]}"')
        out.write('roleview_list \t(list RoleViews')
        out.indent()
        out.write(f'(object RoleView "{a["r1_name"]}" @{r1vid}')
        out.indent()
        out.write(f'Parent_View \t@{avid}')
        out.write('location \t(500, 200)')
        out.write(f'quidu \t"{a["r1_quid"]}"')
        out.write(f'client \t@{avid}')
        out.write(f'supplier \t@{c2vid}')
        out.write('line_style \t0)')
        out.dedent()
        out.write(f'(object RoleView "{a["r2_name"]}" @{r2vid}')
        out.indent()
        out.write(f'Parent_View \t@{avid}')
        out.write('location \t(500, 200)')
        out.write(f'quidu \t"{a["r2_quid"]}"')
        out.write(f'client \t@{avid}')
        out.write(f'supplier \t@{c1vid}')
        out.write('line_style \t0)')
        out.dedent()
        out.dedent()
        out.write('))')
        out.dedent()

    out.dedent()
    out.write(')')  # end items of BCE ClassDiagram
    out.dedent()
    out.write(')')  # end BCE ClassDiagram

    # Presentation 2: 3-Tier Design Class Diagram Overview (Section 3.3)
    diag_3tier_quid = qm.get("0004")
    out.write('(object ClassDiagram "3-Tier Design Class Diagram Overview"')
    out.indent()
    out.write(f'quid \t"{diag_3tier_quid}"')
    out.write('title \t"3-Tier Design Class Diagram Overview"')
    out.write('zoom \t100')
    out.write('max_height \t28350')
    out.write('max_width \t21600')
    out.write('origin_x \t0')
    out.write('origin_y \t0')
    out.write('items \t(list diagram_item_list')
    out.indent()

    v_3t_id = 0
    key_controllers = ["AccountController", "CartController", "HopDongController", "PaymentController", "CongNoController"]
    c_x = 400
    for kc in key_controllers:
        v_3t_id += 1
        kc_quid = tier_storage[0]["classes"][kc]
        out.write(f'(object ClassView "Class" "Logical View::Presentation Tier::{kc}" @{v_3t_id}')
        out.indent()
        out.write('ShowCompartmentStereotypes \tTRUE')
        out.write(f'location \t({c_x}, 350)')
        out.write('font \t(object Font size 10 face "Arial")')
        out.write(f'label \t(object ItemLabel Parent_View @{v_3t_id} location ({c_x}, 290) anchor_loc 1 nlines 2 max_width 350 justify 0 label "{kc}")')
        out.write('line_color \t3342348')
        out.write('fill_color \t13434879')
        out.write(f'quidu \t"{kc_quid}"')
        out.write('width \t380')
        out.write('height \t200')
        out.write('autoResize \tTRUE)')
        out.dedent()
        c_x += 420

    key_services = ["InventoryReservationBackgroundService", "VietQRService", "DebtCalculationHelper", "SLATimerService"]
    s_x = 450
    for ks in key_services:
        v_3t_id += 1
        ks_quid = tier_storage[1]["classes"][ks]
        out.write(f'(object ClassView "Class" "Logical View::Business Logic Tier::{ks}" @{v_3t_id}')
        out.indent()
        out.write('ShowCompartmentStereotypes \tTRUE')
        out.write(f'location \t({s_x}, 750)')
        out.write('font \t(object Font size 10 face "Arial")')
        out.write(f'label \t(object ItemLabel Parent_View @{v_3t_id} location ({s_x}, 690) anchor_loc 1 nlines 2 max_width 350 justify 0 label "{ks}")')
        out.write('line_color \t3342348')
        out.write('fill_color \t13434879')
        out.write(f'quidu \t"{ks_quid}"')
        out.write('width \t380')
        out.write('height \t200')
        out.write('autoResize \tTRUE)')
        out.dedent()
        s_x += 440

    v_3t_id += 1
    db_ctx_q = tier_storage[2]["classes"]["ApplicationDbContext"]
    out.write(f'(object ClassView "Class" "Logical View::Data Access Tier::ApplicationDbContext" @{v_3t_id}')
    out.indent()
    out.write('ShowCompartmentStereotypes \tTRUE')
    out.write('location \t(1100, 1150)')
    out.write('font \t(object Font size 10 face "Arial")')
    out.write(f'label \t(object ItemLabel Parent_View @{v_3t_id} location (1100, 1090) anchor_loc 1 nlines 2 max_width 350 justify 0 label "ApplicationDbContext")')
    out.write('line_color \t3342348')
    out.write('fill_color \t13434879')
    out.write(f'quidu \t"{db_ctx_q}"')
    out.write('width \t400')
    out.write('height \t220')
    out.write('autoResize \tTRUE)')
    out.dedent()

    out.dedent()
    out.write(')')  # end items of 3-Tier Design Class Diagram Overview
    out.dedent()
    out.write(')')  # end 3-Tier Design Class Diagram Overview

    # Presentations 3..9: The 7 Feature-specific 3-Tier Class Diagrams (Section 3.4.1 to 3.4.7)
    features_3tier_spec = [
        ("3-Tier Design - Feature 1: Dang ky & Xac thuc", "AccountController", "CookieAuthHandler", "NguoiDung"),
        ("3-Tier Design - Feature 2: Dat thue & Khoa ton kho", "CartController", "CartInventoryLock", "ThietBi"),
        ("3-Tier Design - Feature 3: Thanh toan dat coc VietQR", "PaymentController", "VietQRService", "PhieuThu"),
        ("3-Tier Design - Feature 4: Ban giao & Ky bien ban", "HopDongController", "PdfExportService", "BienBanBanGiao"),
        ("3-Tier Design - Feature 5: Bao tri & Phan cong SLA", "BaoTriController", "SLATimerService", "PhieuBaoTri"),
        ("3-Tier Design - Feature 6: Gia han hop dong & Cong no", "CongNoController", "DebtCalculationHelper", "KyHanThanhToan"),
        ("3-Tier Design - Feature 7: Tra may & Hoan coc", "HopDongController", "DebtCalculationHelper", "PhieuChi")
    ]

    for f_title, ctrl_name, srv_name, ent_name in features_3tier_spec:
        f_diag_q = qm.get("0004")
        ctrl_q = tier_storage[0]["classes"][ctrl_name]
        srv_q = tier_storage[1]["classes"][srv_name]
        ent_q = entity_quids[ent_name]
        db_q = tier_storage[2]["classes"]["ApplicationDbContext"]

        out.write(f'(object ClassDiagram "{f_title}"')
        out.indent()
        out.write(f'quid \t"{f_diag_q}"')
        out.write(f'title \t"{f_title}"')
        out.write('zoom \t100')
        out.write('max_height \t28350')
        out.write('max_width \t21600')
        out.write('origin_x \t0')
        out.write('origin_y \t0')
        out.write('items \t(list diagram_item_list')
        out.indent()

        out.write(f'(object ClassView "Class" "Logical View::Presentation Tier::{ctrl_name}" @1 location (400, 400) font (object Font size 10 face "Arial") label (object ItemLabel Parent_View @1 location (400, 340) anchor_loc 1 nlines 2 max_width 350 justify 0 label "{ctrl_name}") line_color 3342348 fill_color 13434879 quidu "{ctrl_q}" width 380 height 200 autoResize TRUE)')
        out.write(f'(object ClassView "Class" "Logical View::Business Logic Tier::{srv_name}" @2 location (1000, 400) font (object Font size 10 face "Arial") label (object ItemLabel Parent_View @2 location (1000, 340) anchor_loc 1 nlines 2 max_width 350 justify 0 label "{srv_name}") line_color 3342348 fill_color 13434879 quidu "{srv_q}" width 380 height 200 autoResize TRUE)')
        out.write(f'(object ClassView "Class" "Logical View::Data Access Tier::ApplicationDbContext" @3 location (1000, 800) font (object Font size 10 face "Arial") label (object ItemLabel Parent_View @3 location (1000, 740) anchor_loc 1 nlines 2 max_width 350 justify 0 label "ApplicationDbContext") line_color 3342348 fill_color 13434879 quidu "{db_q}" width 380 height 200 autoResize TRUE)')
        out.write(f'(object ClassView "Class" "Logical View::{ent_name}" @4 location (400, 800) font (object Font size 10 face "Arial") label (object ItemLabel Parent_View @4 location (400, 740) anchor_loc 1 nlines 2 max_width 350 justify 0 label "{ent_name}") line_color 3342348 fill_color 13434879 quidu "{ent_q}" width 380 height 200 autoResize TRUE)')

        out.dedent()
        out.write('))')  # end items, ClassDiagram
        out.dedent()

    out.dedent()
    out.write(')')  # end logical_presentations of root_category
    out.dedent()
    out.write(')')  # end root_category

    # =========================================================================
    # PART C: COMPONENT VIEW (root_subsystem)
    # =========================================================================
    out.write('root_subsystem \t(object SubSystem "Component View"')
    out.indent()
    out.write(f'quid \t"{quid_comp_pkg}"')
    out.write('physical_models \t(list unit_reference_list')
    out.indent()
    comp_names = ["RentalSystem.Web.dll", "RentalSystem.Core.dll", "RentalSystem.Data.dll", "ClosedXML.dll", "QRCoder.dll"]
    for cpn in comp_names:
        cp_q = qm.get("0005")
        out.write(f'(object Module "{cpn}" quid "{cp_q}" stereotype "DLL")')
    out.dedent()
    out.write(')')
    out.write('physical_presentations \t(list unit_reference_list))')
    out.dedent()

    # =========================================================================
    # PART D: PROCESS VIEW (process_structure)
    # MANDATORY: ProcsNDevs (list (object Process_Diagram ...))
    # NEVER: Procs (list Processes))
    # =========================================================================
    out.write('process_structure \t(object Processes')
    out.indent()
    out.write(f'quid \t"{quid_proc_pkg}"')
    out.write('ProcsNDevs \t(list')
    out.indent()

    nodes_spec = [
        ("Client Workstation / Browser", 400, 400, "May tram client truy cap qua trinh duyet Web HTML5 Canvas"),
        ("Application Web Server", 1100, 400, "May chu chay ASP.NET Core 9 MVC va Hangfire Background Workers"),
        ("Database Server", 1100, 900, "May chu co so du lieu SQL Server 2022 luu tru thuc the"),
        ("Banking Gateway", 1800, 400, "Cong thanh toan NAPAS 247 va Ngan hang MBBank SePay")
    ]
    node_storage = []
    for nd_title, nx, ny, nd_doc in nodes_spec:
        nd_q = qm.get("0008")
        node_storage.append((nd_title, nx, ny, nd_doc, nd_q))
        out.write(f'(object Device "{nd_title}"')
        out.indent()
        out.write(f'quid \t"{nd_q}"')
        out.write(f'documentation \t"{nd_doc}")')
        out.dedent()

    out.write('(object Process_Diagram "Deployment View"')
    out.indent()
    out.write(f'quid \t"{quid_deploy_diag}"')
    out.write('title \t"Deployment View"')
    out.write('zoom \t100')
    out.write('max_height \t28350')
    out.write('max_width \t21600')
    out.write('origin_x \t0')
    out.write('origin_y \t0')
    out.write('items \t(list diagram_item_list')
    out.indent()

    for v_dp_id, (nd_title, nx, ny, nd_doc, nd_q) in enumerate(node_storage, 1):
        out.write(f'(object DeviceView "{nd_title}" @{v_dp_id}')
        out.indent()
        out.write(f'location \t({nx}, {ny})')
        out.write('font \t(object Font size 10 face "Arial")')
        out.write(f'label \t(object ItemLabel Parent_View @{v_dp_id} location ({nx}, {ny-60}) anchor_loc 1 nlines 2 max_width 350 justify 0 label "{nd_title}")')
        out.write('line_color \t3342348')
        out.write('fill_color \t13434879')
        out.write(f'quidu \t"{nd_q}"')
        out.write('width \t380')
        out.write('height \t200')
        out.write('autoResize \tTRUE)')
        out.dedent()

    out.dedent()
    out.write(')))')  # end items, Process_Diagram, ProcsNDevs
    out.dedent()
    out.write(')')  # end process_structure

    # =========================================================================
    # PART E: PROPERTIES & CREATION INFO
    # =========================================================================
    out.write('properties \t(object Creation_Info')
    out.indent()
    out.write('build \t"8.0.0303.1400"')
    out.write('date \t"Monday, November 02, 2026"')
    out.write('time \t"16:00:00")')
    out.dedent()

    # Close root Design "Logical View"
    out.dedent()
    out.write(')')  # end Design "Logical View"

    content = out.get_content()
    print(f"[MasterBuilder] Successfully constructed Petal AST.")
    print(f"[MasterBuilder] Total declared unique Quids: {len(qm.declared_quids):,}")

    # Internal syntax verification
    is_valid = verify_petal_syntax(content)
    assert is_valid, "Fatal: AST verification failed internally before writing!"

    return content


def main():
    target_path = Path(r"D:\DoAnCuNhan\Rose_Diagrams\RentalSystem_Master.mdl")
    print(f"Building Master Rational Rose Model: {target_path} ...")
    content = build_master_model()
    target_path.write_text(content, encoding="utf-8")
    print(f"Written {len(content):,} characters to {target_path}.")

    # Validate output
    val_script = Path(r"D:\DoAnCuNhan\Rose_Diagrams\validate_petal.py")
    if val_script.exists():
        print(f"\nRunning official validator on {target_path} ...")
        cmd = f"python {val_script} {target_path} --strict"
        ret = os.system(cmd)
        if ret == 0:
            print("\n>>> SUCCESS: MODEL PASSES ALL VALIDATION CHECKS (0 ERRORS)! <<<")
        else:
            print(f"\n>>> VALIDATION RETURNED CODE: {ret} <<<")
            sys.exit(ret)


if __name__ == "__main__":
    main()
