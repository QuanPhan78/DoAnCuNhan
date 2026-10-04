import os

main_path = "lib/main.dart"
with open(main_path, "r", encoding="utf-8") as f:
    c = f.read()

# Fix the broken MaterialApp syntax
broken = """      theme: AppTheme.lightTheme,

        useMaterial3: true,

      ),

      initialRoute: '/',

      onGenerateRoute: AppRouter.generateRoute,

      debugShowCheckedModeBanner: false,

    );"""

fixed = """      theme: AppTheme.lightTheme,
      initialRoute: '/',
      onGenerateRoute: AppRouter.generateRoute,
      debugShowCheckedModeBanner: false,
    );"""

c = c.replace(broken, fixed)
with open(main_path, "w", encoding="utf-8") as f:
    f.write(c)

theme_path = "lib/theme/app_theme.dart"
with open(theme_path, "r", encoding="utf-8") as f:
    tc = f.read()

# Remove the cardTheme entirely to avoid CardThemeData vs CardTheme mismatch in this flutter version
import re
tc = re.sub(r"cardTheme:\s*CardTheme\([^)]*\),", "", tc)
tc = tc.replace("cardTheme: CardThemeData", "//")
# Remove dividerTheme to be safe too
tc = re.sub(r"dividerTheme:\s*const DividerThemeData\([^)]*\),", "", tc)

# Also fix the CardTheme string block just in case it had multiple lines:
tc = re.sub(r"cardTheme: CardTheme\([\s\S]*?\),", "", tc)
tc = re.sub(r"dividerTheme: const DividerThemeData\([\s\S]*?\),", "", tc)

with open(theme_path, "w", encoding="utf-8") as f:
    f.write(tc)
