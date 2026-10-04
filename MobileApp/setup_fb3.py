import os

path = "lib/screens/home/home_screen.dart"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Let's add a "Phản hồi" quick action for Customer.
# The customer quick actions block might look like:
# _buildActionItem(context, Icons.build, 'Bảo trì', '/requests'),
# Let's see if we can find it and replace it.

new_action = "_buildActionItem(context, Icons.feedback, 'Phản hồi', '/feedbacks'),"
if "Phản hồi" not in content and "'Báo sự cố'" in content:
    # Just append it to the Customer Quick Actions
    content = content.replace(
        "_buildActionItem(context, Icons.build, 'Bảo trì', '/incidents'),", 
        "_buildActionItem(context, Icons.build, 'Bảo trì', '/incidents'),\n                " + new_action
    )
    # If the route was still '/requests' (from before my changes)
    content = content.replace(
        "_buildActionItem(context, Icons.build, 'Bảo trì', '/requests'),", 
        "_buildActionItem(context, Icons.build, 'Bảo trì', '/requests'),\n                " + new_action
    )
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
        print("Added Feedback quick action")
else:
    print("Could not find exact spot, or already added.")
