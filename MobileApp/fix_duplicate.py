import os

path = "lib/providers/feedback_provider.dart"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Remove the redundant _feedbacks.insert in provider.
old_block = """      if (success) {
        _feedbacks.insert(0, feedback);
        notifyListeners();
      }"""
new_block = """      if (success) {
        // KhĂ´ng cáº§n insert vĂ o _feedbacks vĂ¬ fetchFeedbacks sáº½ lĂ m má»›i list
        // VĂ  Ä‘á»ƒ trĂ¡nh reference gĂ¢y duplicate.
        notifyListeners();
      }"""

# Handle utf-8 writing carefully, just remove the insert line.
content = content.replace("        _feedbacks.insert(0, feedback);", "")

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

# Fix LocalFeedbackDataSource to return a copy just to be safe
ds_path = "lib/datasources/feedback/local_feedback_datasource.dart"
with open(ds_path, "r", encoding="utf-8") as f:
    ds = f.read()

ds = ds.replace("return _inMemoryData!;", "return List.from(_inMemoryData!);")
with open(ds_path, "w", encoding="utf-8") as f:
    f.write(ds)
print("Fixed duplicate feedback issue")