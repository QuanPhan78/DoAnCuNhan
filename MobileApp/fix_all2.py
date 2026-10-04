import os

m_path = "lib/models/installation_model.dart"
with open(m_path, "r", encoding="utf-8") as f: c = f.read()
c = c.replace("import 'package:flutter/material.dart';\n", "")
with open(m_path, "w", encoding="utf-8") as f: f.write(c)

lds_path = "lib/datasources/contract/local_contract_datasource.dart"
with open(lds_path, "r", encoding="utf-8") as f: c = f.read()
c = c.replace("Future<bool> updateContractStatus", "@override\n  Future<bool> updateContractStatus")
with open(lds_path, "w", encoding="utf-8") as f: f.write(c)