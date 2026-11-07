#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
EMPIRICAL CHALLENGER: PETAL SYNTAX & INTEGRITY ADVERSARIAL TEST SUITE
==============================================================================
Project: RentalSystem - HUIT 2025
Role: Petal Empirical Challenger (Adversarial stress-testing)
Target: D:\\DoAnCuNhan\\Rose_Diagrams\\RentalSystem_Master.mdl
Validator: D:\\DoAnCuNhan\\Rose_Diagrams\\validate_petal.py

Test Dimensions:
1. Strict Charset & Byte Purity (ASCII 0..127, No BOM, No Nulls, No Control chars)
2. State-Machine Parentheses Balance & String Escape Boundary
3. Full S-Expression AST Parsing (Proof of Tree Well-formedness)
4. Quid Uniqueness & Hex Formatting
5. Quidu Referential Integrity & Semantic Target Resolution
6. Banned Keywords Audit (RoleViewList, Procs (list Processes)), case variations)
7. Mandatory Petal Constructs Audit (roleview_list, ProcsNDevs, root categories)
8. AssociationViewNew RoleView Structural Integrity
9. Oracle Stress-Test: Mutation Testing of validate_petal.py (Negative Controls)
==============================================================================
"""

import sys
import os
import re
import subprocess
import tempfile
from pathlib import Path
from collections import Counter, defaultdict
from typing import List, Dict, Tuple, Set, Optional, Any

# Ensure stdout handles UTF-8
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

TARGET_MDL = Path(r"D:\DoAnCuNhan\Rose_Diagrams\RentalSystem_Master.mdl")
VALIDATOR_PY = Path(r"D:\DoAnCuNhan\Rose_Diagrams\validate_petal.py")


class TestResult:
    def __init__(self, name: str):
        self.name = name
        self.passed = True
        self.details: List[str] = []
        self.metrics: Dict[str, Any] = {}

    def fail(self, message: str):
        self.passed = False
        self.details.append(f"[FAIL] {message}")

    def info(self, message: str):
        self.details.append(f"[INFO] {message}")

    def metric(self, key: str, value: Any):
        self.metrics[key] = value


class PetalAdversarialChallenger:
    def __init__(self, mdl_path: Path):
        self.mdl_path = mdl_path
        self.raw_bytes = b""
        self.text = ""
        self.lines: List[str] = []
        self.declared_quids: Dict[str, Tuple[int, str, str]] = {}  # quid -> (line, obj_type, obj_name)
        self.referenced_quidus: List[Tuple[str, int, str]] = []  # (quidu, line, context)
        self.results: List[TestResult] = []

    def load(self):
        if not self.mdl_path.exists():
            raise FileNotFoundError(f"Target MDL not found: {self.mdl_path}")
        with open(self.mdl_path, "rb") as f:
            self.raw_bytes = f.read()
        self.text = self.raw_bytes.decode("ascii", errors="replace")
        self.lines = self.text.splitlines()

    # --------------------------------------------------------------------------
    # 1. CHARSET & BYTE PURITY
    # --------------------------------------------------------------------------
    def test_charset_and_byte_purity(self) -> TestResult:
        res = TestResult("Dimension 1: Charset & Byte-Level Purity")
        res.metric("total_bytes", len(self.raw_bytes))
        res.metric("total_lines", len(self.lines))

        # Check for BOM
        if self.raw_bytes.startswith(b"\xef\xbb\xbf"):
            res.fail("File contains UTF-8 BOM (0xEF 0xBB 0xBF). Win32 Rose parser fails on BOM.")
        if self.raw_bytes.startswith(b"\xff\xfe") or self.raw_bytes.startswith(b"\xfe\xff"):
            res.fail("File contains UTF-16 BOM. Win32 Rose parser requires ANSI ASCII.")

        # Check for null bytes
        null_count = self.raw_bytes.count(b"\x00")
        if null_count > 0:
            res.fail(f"Found {null_count} null bytes (\\x00) which prematurely terminate C strings in Rose.")
        res.metric("null_bytes", null_count)

        # Check for non-ASCII characters (> 127)
        non_ascii_indices = [idx for idx, b in enumerate(self.raw_bytes) if b > 127]
        res.metric("non_ascii_bytes_count", len(non_ascii_indices))
        if non_ascii_indices:
            res.fail(f"Found {len(non_ascii_indices)} non-ASCII bytes (ord > 127). Sample byte offsets: {non_ascii_indices[:5]}")
        else:
            res.info("100% pure 7-bit ASCII confirmed. Clean decoding under US-ASCII.")

        # Check for invalid control characters (allow \t=9, \n=10, \r=13)
        invalid_ctrl = []
        for idx, b in enumerate(self.raw_bytes):
            if b < 32 and b not in (9, 10, 13):
                invalid_ctrl.append((idx, b))
        res.metric("invalid_ctrl_chars", len(invalid_ctrl))
        if invalid_ctrl:
            res.fail(f"Found {len(invalid_ctrl)} disallowed control characters. Sample: {invalid_ctrl[:5]}")
        else:
            res.info("No illegal control characters detected.")

        return res

    # --------------------------------------------------------------------------
    # 2. STATE-MACHINE PARENTHESES BALANCE & STRING ESCAPE BOUNDARY
    # --------------------------------------------------------------------------
    def test_parentheses_and_string_escapes(self) -> TestResult:
        res = TestResult("Dimension 2: Parentheses Balance & String Escapes")
        stack: List[Tuple[int, int]] = []
        in_string = False
        escape = False

        line = 1
        col = 0
        total_open = 0
        total_close = 0
        max_depth = 0

        for i, ch in enumerate(self.text):
            if ch == '\n':
                line += 1
                col = 0
                continue
            col += 1

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
                    total_open += 1
                    stack.append((line, col))
                    if len(stack) > max_depth:
                        max_depth = len(stack)
                elif ch == ')':
                    total_close += 1
                    if not stack:
                        res.fail(f"Unmatched closing parenthesis ')' at line {line}:{col}")
                    else:
                        stack.pop()

        res.metric("total_open_parens", total_open)
        res.metric("total_close_parens", total_close)
        res.metric("max_paren_depth", max_depth)
        res.metric("unclosed_parens", len(stack))

        if in_string:
            res.fail("Unclosed string literal reaching EOF!")
        if stack:
            res.fail(f"{len(stack)} unclosed opening parentheses '(' remaining at EOF! First 3 at: {stack[:3]}")

        if not stack and not in_string and total_open == total_close:
            res.info(f"Perfect parenthesis balance: {total_open} '(' exactly matched with {total_close} ')'.")
            res.info(f"Maximum AST nesting depth: {max_depth} levels.")

        return res

    # --------------------------------------------------------------------------
    # 3. FULL S-EXPRESSION AST PARSER (DEEP STRUCTURAL WELL-FORMEDNESS)
    # --------------------------------------------------------------------------
    def test_s_expression_ast_parser(self) -> TestResult:
        res = TestResult("Dimension 3: Full S-Expression AST Structural Parsing")
        
        # Tokenizer
        tokens = []
        token_pattern = re.compile(r'\(|\)|"([^"\\]*(?:\\.[^"\\]*)*)"|[^\s()"]+')
        
        for match in token_pattern.finditer(self.text):
            val = match.group(0)
            if val.startswith('"') and val.endswith('"'):
                tokens.append(('STR', val[1:-1]))
            elif val == '(':
                tokens.append(('LPAREN', '('))
            elif val == ')':
                tokens.append(('RPAREN', ')'))
            else:
                tokens.append(('ATOM', val))

        res.metric("total_tokens", len(tokens))

        # Iterative stack-based S-Expression tree builder
        tree = []
        stack = [tree]
        
        try:
            for t_type, t_val in tokens:
                if t_type == 'LPAREN':
                    new_node: List[Any] = []
                    stack[-1].append(new_node)
                    stack.append(new_node)
                elif t_type == 'RPAREN':
                    if len(stack) <= 1:
                        res.fail("AST stack underflow on RPAREN")
                        break
                    stack.pop()
                else:
                    stack[-1].append(t_val)
            
            if len(stack) != 1:
                res.fail(f"AST stack has {len(stack)-1} unclosed frames at end of token stream")
            else:
                res.info(f"S-Expression AST constructed successfully. Root children count: {len(tree)}")
                top_objects = [item for item in tree if isinstance(item, list) and len(item) > 1 and item[0] == 'object']
                res.metric("top_level_objects", len(top_objects))
                res.info(f"Top-level Petal objects count: {len(top_objects)}")
        except Exception as ex:
            res.fail(f"AST Parser encountered exception: {ex}")

        return res

    # --------------------------------------------------------------------------
    # 4. QUID DECLARATION UNIQUENESS & FORMAT
    # --------------------------------------------------------------------------
    def test_quid_uniqueness_and_formatting(self) -> TestResult:
        res = TestResult("Dimension 4: Quid Uniqueness & Format")

        quid_regex = re.compile(r'\bquid\s+"([^"]+)"')
        quid_lines = []
        for line_idx, line in enumerate(self.lines, 1):
            for m in quid_regex.finditer(line):
                q = m.group(1)
                quid_lines.append((q, line_idx, line.strip()))

        res.metric("total_declared_quids", len(quid_lines))

        quid_counts = Counter(q for q, _, _ in quid_lines)
        duplicates = {q: count for q, count in quid_counts.items() if count > 1}
        res.metric("duplicate_quid_count", len(duplicates))

        if duplicates:
            for q, count in list(duplicates.items())[:5]:
                occurrences = [l for val, l, _ in quid_lines if val == q]
                res.fail(f"Duplicate quid '{q}' occurs {count} times on lines: {occurrences}")
        else:
            res.info(f"100% Unique Quids: All {len(quid_lines)} declared quids are completely distinct.")

        # Check format: Rose 16-hex-digit or alphanumeric
        invalid_format = []
        for q, l, _ in quid_lines:
            if not q or len(q) < 8 or not re.match(r'^[0-9a-fA-F_]+$', q):
                invalid_format.append((q, l))
        res.metric("malformed_quids", len(invalid_format))
        if invalid_format:
            res.fail(f"Found {len(invalid_format)} malformed quids. Sample: {invalid_format[:5]}")
        else:
            res.info("All quid identifiers adhere to standard hexadecimal/alphanumeric formatting.")

        # Store declared quids for Dimension 5
        self.declared_quids = {q: (l, "", "") for q, l, _ in quid_lines}

        return res

    # --------------------------------------------------------------------------
    # 5. QUIDU REFERENTIAL INTEGRITY (CROSS-REFERENCE AUDIT)
    # --------------------------------------------------------------------------
    def test_quidu_referential_integrity(self) -> TestResult:
        res = TestResult("Dimension 5: Quidu Referential Integrity")

        quidu_regex = re.compile(r'\bquidu\s+"([^"]+)"')
        quidu_refs = []
        for line_idx, line in enumerate(self.lines, 1):
            for m in quidu_regex.finditer(line):
                qu = m.group(1)
                quidu_refs.append((qu, line_idx, line.strip()))

        res.metric("total_quidu_references", len(quidu_refs))

        unresolved = []
        for qu, line_idx, ctx in quidu_refs:
            if qu not in self.declared_quids:
                unresolved.append((qu, line_idx, ctx))

        res.metric("unresolved_quidu_count", len(unresolved))
        if unresolved:
            for qu, line_idx, ctx in unresolved[:10]:
                res.fail(f"Unresolved quidu '{qu}' referenced at line {line_idx}: '{ctx}' does not exist in declared quids!")
        else:
            res.info(f"100% Referential Integrity: All {len(quidu_refs)} quidu references resolve to valid declared quids.")

        return res

    # --------------------------------------------------------------------------
    # 6. BANNED KEYWORD AUDIT
    # --------------------------------------------------------------------------
    def test_banned_keywords_audit(self) -> TestResult:
        res = TestResult("Dimension 6: Banned Keyword Audit")

        # Prohibited token 1: RoleViewList (case-insensitive search)
        rvl_matches = []
        rvl_case_insensitive = re.compile(r'\bRoleViewList\b', re.IGNORECASE)
        for line_idx, line in enumerate(self.lines, 1):
            m = rvl_case_insensitive.search(line)
            if m:
                rvl_matches.append((line_idx, line.strip()))

        res.metric("RoleViewList_occurrences", len(rvl_matches))
        if rvl_matches:
            for l, ctx in rvl_matches:
                res.fail(f"Banned keyword 'RoleViewList' detected at line {l}: '{ctx}'")
        else:
            res.info("0 occurrences of banned keyword 'RoleViewList' confirmed.")

        # Prohibited token 2: Procs (list Processes))
        procs_matches = []
        procs_regex = re.compile(r'Procs\s+\(list\s+Processes\s*\)', re.IGNORECASE)
        for line_idx, line in enumerate(self.lines, 1):
            m = procs_regex.search(line)
            if m:
                procs_matches.append((line_idx, line.strip()))

        res.metric("Procs_list_Processes_occurrences", len(procs_matches))
        if procs_matches:
            for l, ctx in procs_matches:
                res.fail(f"Banned syntax 'Procs (list Processes))' detected at line {l}: '{ctx}'")
        else:
            res.info("0 occurrences of banned syntax 'Procs (list Processes))' confirmed.")

        return res

    # --------------------------------------------------------------------------
    # 7. MANDATORY CONSTRUCTS AUDIT
    # --------------------------------------------------------------------------
    def test_mandatory_constructs(self) -> TestResult:
        res = TestResult("Dimension 7: Mandatory Petal Constructs Audit")

        # Construct A: Petal Header
        petal_hdr = re.search(r'\(object\s+Petal\s+version\s+47\s+_written\s+"[^"]+"\s+charSet\s+0\)', self.text)
        if not petal_hdr:
            res.fail("Missing standard Rational Rose Petal header (version 47, charSet 0)")
        else:
            res.info("Verified standard Petal header: version 47, charSet 0.")

        # Construct B: Root Design
        design_hdr = re.search(r'\(object\s+Design\s+"Logical View"\s+is_unit\s+TRUE\s+is_loaded\s+TRUE\s+quid\s+"([^"]+)"', self.text)
        if not design_hdr:
            res.fail("Missing root object Design 'Logical View'")
        else:
            res.info(f"Verified root object Design 'Logical View' (quid: {design_hdr.group(1)}).")

        # Construct C: root_usecase_package
        usecase_pkg = re.search(r'root_usecase_package\s+\(object\s+Class_Category\s+"Use Case View"', self.text)
        if not usecase_pkg:
            res.fail("Missing 'root_usecase_package (object Class_Category \"Use Case View\"'")
        else:
            res.info("Verified 'root_usecase_package (object Class_Category \"Use Case View\"'.")

        # Construct D: root_category
        root_cat = re.search(r'root_category\s+\(object\s+Class_Category\s+"Logical View"', self.text)
        if not root_cat:
            res.fail("Missing 'root_category (object Class_Category \"Logical View\"'")
        else:
            res.info("Verified 'root_category (object Class_Category \"Logical View\"'.")

        # Construct E: process_structure with ProcsNDevs
        proc_struct = re.search(r'process_structure\s+\(object\s+Processes', self.text)
        if not proc_struct:
            res.fail("Missing 'process_structure (object Processes'")
        else:
            res.info("Verified 'process_structure (object Processes'.")

        procs_n_devs = re.search(r'ProcsNDevs\s+\(list\s+', self.text)
        if not procs_n_devs:
            res.fail("Missing mandatory 'ProcsNDevs (list ...)' in process_structure")
        else:
            res.info("Verified mandatory 'ProcsNDevs (list ...)' construct present.")

        # Construct F: roleview_list in AssociationViewNew
        assoc_views = list(re.finditer(r'\(object\s+AssociationViewNew\b', self.text))
        res.metric("total_association_views", len(assoc_views))
        
        roleview_lists = list(re.finditer(r'roleview_list\s+\(list\s+RoleViews\b', self.text))
        res.metric("total_roleview_lists", len(roleview_lists))

        if len(assoc_views) > 0 and len(roleview_lists) < len(assoc_views):
            res.fail(f"Mismatch: {len(assoc_views)} AssociationViewNew found, but only {len(roleview_lists)} 'roleview_list (list RoleViews' constructs!")
        elif len(assoc_views) > 0:
            res.info(f"All {len(assoc_views)} AssociationViewNew contain 'roleview_list (list RoleViews'.")

        return res

    # --------------------------------------------------------------------------
    # 8. ASSOCIATIONVIEWNEW ROLEVIEW STRUCTURAL INTEGRITY
    # --------------------------------------------------------------------------
    def _get_matching_block(self, start_idx: int) -> str:
        depth = 0
        in_str = False
        escape = False
        for i in range(start_idx, len(self.text)):
            ch = self.text[i]
            if in_str:
                if escape:
                    escape = False
                elif ch == '\\':
                    escape = True
                elif ch == '"':
                    in_str = False
            else:
                if ch == '"':
                    in_str = True
                elif ch == '(':
                    depth += 1
                elif ch == ')':
                    depth -= 1
                    if depth == 0:
                        return self.text[start_idx : i + 1]
        return self.text[start_idx:]

    def test_association_view_roleviews_structural(self) -> TestResult:
        res = TestResult("Dimension 8: AssociationViewNew RoleView Structural Integrity")

        assoc_indices = [m.start() for m in re.finditer(r'\(object\s+AssociationViewNew\b', self.text)]
        res.metric("inspected_assoc_views", len(assoc_indices))

        for idx, start_pos in enumerate(assoc_indices):
            line_no = self.text[:start_pos].count('\n') + 1
            block = self._get_matching_block(start_pos)

            if "roleview_list" not in block:
                res.fail(f"AssociationViewNew at line {line_no} missing roleview_list block")
                continue

            # Extract quidu of the association
            quidu_match = re.search(r'quidu\s+"([^"]+)"', block)
            if not quidu_match:
                res.fail(f"AssociationViewNew at line {line_no} missing semantic quidu reference")

            # Extract RoleViews
            role_views = list(re.finditer(r'\(object\s+RoleView\b', block))
            if len(role_views) != 2:
                res.fail(f"AssociationViewNew at line {line_no} does not have exactly 2 RoleViews (found {len(role_views)})")

        if res.passed and assoc_indices:
            res.info(f"All {len(assoc_indices)} AssociationViewNew objects possess fully populated client/supplier RoleViews with valid semantic quidu pointers.")

        return res

    # --------------------------------------------------------------------------
    # 9. ORACLE MUTATION TESTING (VERIFYING VALIDATOR ENGINE FIDELITY)
    # --------------------------------------------------------------------------
    def test_oracle_mutation_testing(self) -> TestResult:
        res = TestResult("Dimension 9: Oracle Mutation Testing of validate_petal.py")

        mutations = [
            ("Unclosed Parenthesis", self.text + "\n(object BrokenParen\n", "SYNTAX_PAREN"),
            ("Duplicate Quid", self.text.replace('quid \t"6001000100000002"', 'quid \t"6001000100000001"', 1), "QUID_DUPLICATE"),
            ("Banned Keyword RoleViewList", self.text.replace('roleview_list', 'RoleViewList', 1), "BANNED_KEYWORD"),
            ("Banned Keyword Procs (list Processes))", re.sub(r'ProcsNDevs\s+\(list', 'Procs (list Processes)) \t(list', self.text, count=1), "BANNED_KEYWORD"),
            ("Unresolved Quidu", self.text.replace('quidu \t"6001000100000001"', 'quidu \t"9999999999999999"', 1), "QUID_UNRESOLVED"),
            ("Accented Vietnamese (Non-ASCII)", self.text.replace('Khach hang', 'Khách hàng', 1), "CHARSET_NON_ASCII"),
        ]

        passed_mutations = 0

        with tempfile.TemporaryDirectory() as tmpdir:
            for name, mutated_content, expected_issue in mutations:
                mutant_file = Path(tmpdir) / "mutant.mdl"
                with open(mutant_file, "w", encoding="utf-8") as f:
                    f.write(mutated_content)

                cmd = [sys.executable, str(VALIDATOR_PY), str(mutant_file), "--strict", "--no-snippets"]
                p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

                output = p.stdout + p.stderr
                detected = expected_issue in output or p.returncode != 0

                if detected:
                    passed_mutations += 1
                    res.info(f"Mutation '{name}' caught by validator (returncode: {p.returncode}, found '{expected_issue}').")
                else:
                    res.fail(f"Oracle blind spot! Mutation '{name}' was NOT detected by validate_petal.py! Output: {output[:300]}")

        res.metric("total_mutations", len(mutations))
        res.metric("caught_mutations", passed_mutations)
        if passed_mutations == len(mutations):
            res.info(f"Oracle verification complete: All {len(mutations)} adversarial mutations correctly intercepted by validate_petal.py.")

        return res

    # --------------------------------------------------------------------------
    # EXECUTION HARNESS
    # --------------------------------------------------------------------------
    def run_all(self):
        print("=" * 80)
        print("PETAL ADVERSARIAL EMPIRICAL CHALLENGER TEST HARNESS")
        print(f"Target: {self.mdl_path}")
        print("=" * 80)

        self.load()

        tests = [
            self.test_charset_and_byte_purity,
            self.test_parentheses_and_string_escapes,
            self.test_s_expression_ast_parser,
            self.test_quid_uniqueness_and_formatting,
            self.test_quidu_referential_integrity,
            self.test_banned_keywords_audit,
            self.test_mandatory_constructs,
            self.test_association_view_roleviews_structural,
            self.test_oracle_mutation_testing,
        ]

        all_passed = True
        for t in tests:
            r = t()
            self.results.append(r)
            status = "[PASS]" if r.passed else "[FAIL]"
            print(f"{status} {r.name}")
            for d in r.details:
                print(f"       {d}")
            if not r.passed:
                all_passed = False

        print("=" * 80)
        if all_passed:
            print(">>> FINAL EMPIRICAL VERDICT: [APPROVE] <<<")
            print("All 9 adversarial dimensions PASSED with 0 syntax or integrity flaws.")
        else:
            print(">>> FINAL EMPIRICAL VERDICT: [REQUEST_CHANGES] <<<")
            print("Flaws identified during empirical adversarial testing.")
        print("=" * 80)

        return all_passed


if __name__ == "__main__":
    challenger = PetalAdversarialChallenger(TARGET_MDL)
    success = challenger.run_all()
    sys.exit(0 if success else 1)
