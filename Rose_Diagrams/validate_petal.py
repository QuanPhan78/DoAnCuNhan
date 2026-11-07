#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
IBM RATIONAL ROSE PETAL (.MDL) AUTOMATED SYNTAX & INTEGRITY VALIDATOR
==============================================================================
Project: RentalSystem - HUIT 2025
Target Environment: IBM Rational Rose 2003 / 98 Enterprise Edition (Win32)
Role: Milestone 1 - Production Petal Syntax & Model Validator
Author: Setup, Validator & Traceability Worker
==============================================================================
"""

import sys
import os
import re
import argparse
from pathlib import Path
from typing import List, Dict, Tuple, Set, Optional

# Ensure standard output handles UTF-8 safely on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


class ValidationIssue:
    def __init__(self, level: str, category: str, line: int, col: int, message: str, snippet: Optional[str] = None):
        self.level = level.upper()  # ERROR, WARNING, INFO
        self.category = category
        self.line = line
        self.col = col
        self.message = message
        self.snippet = snippet

    def format(self, show_snippet: bool = True) -> str:
        pos = f"Line {self.line}:{self.col}" if self.col > 0 else f"Line {self.line}"
        out = f"  [{self.level}] [{self.category}] {pos} -> {self.message}"
        if show_snippet and self.snippet:
            snippet_lines = self.snippet.splitlines()
            formatted_snippet = "\n".join(f"        | {s}" for s in snippet_lines)
            out += f"\n{formatted_snippet}"
        return out

    def __str__(self):
        return self.format(show_snippet=False)


class PetalValidator:
    def __init__(self, filepath: Path, strict: bool = False, show_snippets: bool = True):
        self.filepath = filepath
        self.strict = strict
        self.show_snippets = show_snippets
        self.issues: List[ValidationIssue] = []
        self.declared_quids: Dict[str, int] = {}
        self.referenced_quidus: List[Tuple[str, int]] = []
        self.lines: List[str] = []
        self.total_lines = 0
        self.version = None
        self.written = None
        self.charset = None

    def _get_snippet(self, line_num: int, context: int = 1) -> str:
        if not self.lines or line_num <= 0:
            return ""
        idx = line_num - 1
        start = max(0, idx - context)
        end = min(len(self.lines), idx + context + 1)
        result = []
        for i in range(start, end):
            prefix = "--> " if i == idx else "    "
            line_content = self.lines[i].rstrip("\r\n")
            result.append(f"{prefix}{i+1:5d}: {line_content}")
        return "\n".join(result)

    def add_issue(self, level: str, category: str, line: int, col: int, message: str, snippet: Optional[str] = None):
        if snippet is None and line > 0 and self.lines:
            snippet = self._get_snippet(line)
        self.issues.append(ValidationIssue(level, category, line, col, message, snippet))

    def validate(self) -> bool:
        if not self.filepath.exists():
            self.add_issue("ERROR", "IO", 0, 0, f"Target file does not exist: {self.filepath}")
            return False

        try:
            content = self.filepath.read_text(encoding="utf-8", errors="replace")
        except Exception as ex:
            self.add_issue("ERROR", "IO", 0, 0, f"Failed to read file: {ex}")
            return False

        self.lines = content.splitlines(keepends=True)
        self.total_lines = len(self.lines)

        # Pipeline of Petal AST & Syntax Verifications
        self._check_header(content)
        self._check_parentheses_and_strings(content)
        self._check_prohibited_keywords()
        self._check_mandatory_constructs(content)
        self._check_quid_uniqueness(content)
        self._check_quidu_integrity()
        self._check_charset_and_vietnamese()
        self._check_colon_escapes(content)

        error_count = sum(1 for iss in self.issues if iss.level == "ERROR")
        return error_count == 0

    def _check_header(self, content: str):
        """Validates Petal header (version 42/47/50, charSet 0)."""
        hdr_regex_a = re.compile(
            r'\(object\s+Petal\s+version\s+(\d+)\s+_written\s+"([^"]+)"\s+charSet\s+(\d+)\)',
            re.DOTALL
        )
        hdr_regex_b = re.compile(
            r'\(object\s+Petal\s+\(version\s+(\d+)\)\s+\(format\s+([^\)]+)\)',
            re.DOTALL
        )

        match_a = hdr_regex_a.search(content[:800])
        match_b = hdr_regex_b.search(content[:800])

        if match_a:
            self.version = int(match_a.group(1))
            self.written = match_a.group(2)
            self.charset = int(match_a.group(3))
            if self.version != 47:
                self.add_issue("WARNING", "HEADER", 1, 1,
                               f"Petal version is {self.version}. Rational Rose 2003 official standard is version 47.")
            if self.charset != 0:
                self.add_issue("ERROR", "HEADER", 1, 1,
                               f"charSet is {self.charset}. Must be 0 (ANSI/DEFAULT_CHARSET) for Win32 Rational Rose.")
        elif match_b:
            self.version = int(match_b.group(1))
            self.written = match_b.group(2)
        else:
            self.add_issue("ERROR", "HEADER", 1, 1,
                           "Invalid or missing Petal file header '(object Petal (version ...) ...)'")

    def _check_parentheses_and_strings(self, content: str):
        """Stack-based verification of balanced parentheses and closed string literals."""
        stack: List[Tuple[int, int]] = []
        in_string = False
        escape = False

        line_num = 1
        col_num = 0

        for idx, ch in enumerate(content):
            if ch == '\n':
                line_num += 1
                col_num = 0
                continue
            col_num += 1

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
                    stack.append((line_num, col_num))
                elif ch == ')':
                    if not stack:
                        snippet = self._get_snippet(line_num)
                        self.add_issue("ERROR", "SYNTAX_PAREN", line_num, col_num,
                                       "Unmatched closing parenthesis ')' without corresponding '('", snippet)
                    else:
                        stack.pop()

        if in_string:
            snippet = self._get_snippet(line_num)
            self.add_issue("ERROR", "SYNTAX_STRING", line_num, col_num,
                           "Unterminated string literal at EOF (missing closing quote '\"')", snippet)

        if stack:
            # Report first 5 unclosed opening parentheses with exact context
            for op_l, op_c in stack[:5]:
                snippet = self._get_snippet(op_l)
                self.add_issue("ERROR", "SYNTAX_PAREN", op_l, op_c,
                               "Unclosed opening parenthesis '('", snippet)
            if len(stack) > 5:
                last_l, last_c = stack[-1]
                snippet = self._get_snippet(last_l)
                self.add_issue("ERROR", "SYNTAX_PAREN", last_l, last_c,
                               f"... and {len(stack) - 5} more unclosed parentheses throughout file.", snippet)

    def _check_prohibited_keywords(self):
        """Detects strictly prohibited tokens: RoleViewList, Procs (list Processes))."""
        rvl_regex = re.compile(r'\bRoleViewList\b')
        procs_regex = re.compile(r'Procs\s+\(list\s+Processes\s*\)')

        for idx, line in enumerate(self.lines, 1):
            if rvl_regex.search(line):
                snippet = self._get_snippet(idx)
                self.add_issue("ERROR", "BANNED_KEYWORD", idx, 1,
                               "Prohibited keyword 'RoleViewList' detected! BẮT BUỘC sử dụng 'roleview_list (list RoleViews'.", snippet)
            if procs_regex.search(line):
                snippet = self._get_snippet(idx)
                self.add_issue("ERROR", "BANNED_KEYWORD", idx, 1,
                               "Prohibited syntax 'Procs (list Processes))' detected! BẮT BUỘC sử dụng 'ProcsNDevs (list (object Process_Diagram ...))'.", snippet)

    def _check_mandatory_constructs(self, content: str):
        """Verifies mandatory constructs for AssociationViewNew and process_structure."""
        # 1. In AssociationViewNew, roleview_list (list RoleViews must be used
        if re.search(r'\(object\s+AssociationViewNew\b', content):
            if not re.search(r'roleview_list\s+\(list\s+RoleViews\b', content):
                self.add_issue("ERROR", "MANDATORY_SYNTAX", 1, 1,
                               "File contains AssociationViewNew but lacks mandatory 'roleview_list (list RoleViews' construct!")

        # 2. In process_structure, ProcsNDevs must be used
        if re.search(r'process_structure\s+\(object\s+Processes\b', content):
            if not re.search(r'ProcsNDevs\s+\(list\b', content):
                self.add_issue("ERROR", "MANDATORY_SYNTAX", 1, 1,
                               "File contains process_structure but lacks mandatory 'ProcsNDevs (list ...)' construct!")

        # 3. Design root object check
        if not re.search(r'\(object\s+Design\s+"Logical View"', content):
            self.add_issue("ERROR", "ROOT_STRUCTURE", 1, 1,
                           "Missing root object '(object Design \"Logical View\" ...)'")

    def _check_quid_uniqueness(self, content: str):
        """Extracts all quids and ensures 100% global uniqueness."""
        quid_regex = re.compile(r'\bquid\s+"([^"]+)"')
        quidu_regex = re.compile(r'\bquidu\s+"([^"]+)"')

        for m in quid_regex.finditer(content):
            q_val = m.group(1)
            line = content[:m.start()].count('\n') + 1
            if q_val in self.declared_quids:
                prev_line = self.declared_quids[q_val]
                snippet = f"Previous at Line {prev_line}:\n" + self._get_snippet(prev_line) + "\nDuplicate at Line " + str(line) + ":\n" + self._get_snippet(line)
                self.add_issue("ERROR", "QUID_DUPLICATE", line, 1,
                               f"Duplicate quid '{q_val}' detected! (First declared at Line {prev_line})", snippet)
            else:
                self.declared_quids[q_val] = line

        for m in quidu_regex.finditer(content):
            qu_val = m.group(1)
            line = content[:m.start()].count('\n') + 1
            self.referenced_quidus.append((qu_val, line))

    def _check_quidu_integrity(self):
        """Verifies all quidu references point to declared quids."""
        unresolved = []
        for qu_val, line in self.referenced_quidus:
            if qu_val not in self.declared_quids:
                unresolved.append((qu_val, line))

        if unresolved:
            for qu_val, line in unresolved[:10]:
                lvl = "ERROR" if self.strict else "WARNING"
                snippet = self._get_snippet(line)
                self.add_issue(lvl, "QUID_UNRESOLVED", line, 1,
                               f"quidu reference '{qu_val}' does not match any declared quid in the file.", snippet)
            if len(unresolved) > 10:
                self.add_issue("WARNING", "QUID_UNRESOLVED", unresolved[-1][1], 1,
                               f"... and {len(unresolved) - 10} more unresolved quidu references.")

    def _check_charset_and_vietnamese(self):
        """Detects accented Vietnamese characters that break Win32 ANSI Rational Rose."""
        accented_lines = []
        for idx, line in enumerate(self.lines, 1):
            non_ascii = [ch for ch in line if ord(ch) > 127]
            if non_ascii:
                accented_lines.append((idx, "".join(set(non_ascii))))

        if accented_lines:
            for idx, chars in accented_lines[:10]:
                snippet = self._get_snippet(idx)
                self.add_issue("WARNING", "CHARSET_NON_ASCII", idx, 1,
                               f"Non-ASCII characters detected ({chars}). Win32 Rose requires pure unaccented Vietnamese!", snippet)
            if len(accented_lines) > 10:
                self.add_issue("WARNING", "CHARSET_NON_ASCII", accented_lines[-1][0], 1,
                               f"... total {len(accented_lines)} lines containing non-ASCII characters.")

    def _check_colon_escapes(self, content: str):
        """Verifies that single colons in qualified supplier/client paths are escaped as \\:."""
        unescaped_colon_regex = re.compile(r'(?:supplier|client)\s+"([^"]*(?<!\\)(?<!:):(?!:)[^"]*)"')
        for m in unescaped_colon_regex.finditer(content):
            path_val = m.group(1)
            line = content[:m.start()].count('\n') + 1
            snippet = self._get_snippet(line)
            self.add_issue("WARNING", "PATH_ESCAPE", line, 1,
                           f"Possible unescaped single colon in path '{path_val}'. In Petal, use '\\\\:' for single colons in element names.", snippet)

    def print_report(self):
        print("=" * 80)
        print("IBM RATIONAL ROSE PETAL SYNTAX VALIDATION REPORT")
        print(f"File: {self.filepath}")
        print(f"Lines: {self.total_lines:,} | Declared Quids: {len(self.declared_quids):,} | Quidu References: {len(self.referenced_quidus):,}")
        print("=" * 80)

        errors = [iss for iss in self.issues if iss.level == "ERROR"]
        warnings = [iss for iss in self.issues if iss.level == "WARNING"]

        if not self.issues:
            print(">>> STATUS: [PASS] 100% SYNTACTICALLY VALID & ERROR-FREE MODEL! <<<")
            return

        print(f"Summary: {len(errors)} ERROR(S), {len(warnings)} WARNING(S)\n")

        if errors:
            print("--- CRITICAL ERRORS (MUST FIX) ---")
            for err in errors:
                print(err.format(show_snippet=self.show_snippets))
                print()

        if warnings:
            print("--- WARNINGS (RECOMMENDED FIXES) ---")
            for w in warnings:
                print(w.format(show_snippet=self.show_snippets))
                print()

        print("=" * 80)
        if errors:
            print(f">>> STATUS: [FAIL] MODEL REJECTED BY VALIDATION RULES ({len(errors)} errors). <<<")
        else:
            print(">>> STATUS: [PASS WITH WARNINGS] NO SYNTAX BLOCKERS. MODEL READY FOR IBM ROSE. <<<")
        print("=" * 80)


def main():
    parser = argparse.ArgumentParser(description="Rational Rose Petal (.mdl) Automated Syntax & Integrity Validator")
    parser.add_argument("target", nargs="?", default=".", help="Path to .mdl file or directory containing .mdl files")
    parser.add_argument("--strict", action="store_true", help="Treat unresolved quidu references as critical errors")
    parser.add_argument("--no-snippets", action="store_true", help="Do not print code snippets for reported issues")
    args = parser.parse_args()

    target_path = Path(args.target)
    if target_path.is_file():
        files = [target_path]
    elif target_path.is_dir():
        files = sorted(list(target_path.glob("*.mdl")))
        if not files:
            print(f"No .mdl files found in directory: {target_path}")
            sys.exit(0)
    else:
        print(f"Error: Target path does not exist: {target_path}")
        sys.exit(1)

    overall_pass = True
    for f in files:
        validator = PetalValidator(f, strict=args.strict, show_snippets=not args.no_snippets)
        is_valid = validator.validate()
        validator.print_report()
        print("\n")
        if not is_valid:
            overall_pass = False

    sys.exit(0 if overall_pass else 1)


if __name__ == "__main__":
    main()
