import os

path = "lib/datasources/search/local_search_datasource.dart"
with open(path, "r", encoding="utf-8") as f:
    c = f.read()

# Fix d.code
c = c.replace("d.code.toLowerCase().contains(lowerQuery) ||", "(d.code?.toLowerCase().contains(lowerQuery) ?? false) ||")

# Fix d.type
c = c.replace("(d.type?.toLowerCase().contains(lowerQuery) ?? false) ||", "d.type.toLowerCase().contains(lowerQuery) ||")

with open(path, "w", encoding="utf-8") as f:
    f.write(c)
