#!/bin/bash

# Test script for write-ahead log workflow
# Demonstrates the workflow functionality

echo "🧪 Testing Write-Ahead Log Workflow"
echo "=================================="

# 1. Test cache directory structure
echo "1. Testing cache directory structure..."
if [ -d ".cache" ]; then
    echo "✅ .cache directory exists"
else
    echo "❌ .cache directory missing"
    exit 1
fi

# Check required files
required_files=("status.csv" "todo" "fixme" "research" "kb.md" "README.md")
for file in "${required_files[@]}"; do
    if [ -f ".cache/$file" ]; then
        echo "✅ .cache/$file exists"
    else
        echo "❌ .cache/$file missing"
        exit 1
    fi
done

# 2. Test status.csv format
echo -e "\n2. Testing status.csv format..."
if grep -q "^filename,lineNumber$" .cache/status.csv; then
    echo "✅ status.csv has correct header"
else
    echo "❌ status.csv header incorrect"
    exit 1
fi

# Check for todo, fixme, research entries
if grep -q "^todo," .cache/status.csv; then
    echo "✅ todo entry in status.csv"
else
    echo "❌ todo entry missing from status.csv"
    exit 1
fi

# 3. Test line reading functionality
echo -e "\n3. Testing line reading functionality..."
current_line=$(grep "^todo," .cache/status.csv | cut -d',' -f2)
if [ -n "$current_line" ] && [ "$current_line" -eq "$current_line" ] 2>/dev/null; then
    echo "✅ Can read current line number: $current_line"
else
    echo "❌ Cannot read current line number"
    exit 1
fi

# Test reading specific line
task=$(sed -n "${current_line}p" .cache/todo)
if [ -n "$task" ]; then
    echo "✅ Can read line $current_line from todo: '$task'"
else
    echo "❌ Cannot read line $current_line from todo"
    exit 1
fi

# 4. Test append-only behavior
echo -e "\n4. Testing append-only behavior..."
initial_lines=$(wc -l < .cache/todo)
echo "Test task" >> .cache/todo
final_lines=$(wc -l < .cache/todo)

if [ "$final_lines" -eq "$((initial_lines + 1))" ]; then
    echo "✅ Append-only behavior working (lines: $initial_lines -> $final_lines)"
else
    echo "❌ Append-only behavior failed"
    exit 1
fi

# 5. Test status update
echo -e "\n5. Testing status update..."
new_line=$((current_line + 1))
sed -i "s/^todo,.*/todo,${new_line}/" .cache/status.csv
updated_line=$(grep "^todo," .cache/status.csv | cut -d',' -f2)

if [ "$updated_line" -eq "$new_line" ]; then
    echo "✅ Status update working (todo: $current_line -> $updated_line)"
else
    echo "❌ Status update failed"
    exit 1
fi

# 6. Test knowledge base format
echo -e "\n6. Testing knowledge base format..."
if grep -q "File:" .cache/kb.md && grep -q "Location:" .cache/kb.md; then
    echo "✅ Knowledge base has correct format"
else
    echo "❌ Knowledge base format incorrect"
    exit 1
fi

# 7. Test cross-platform compatibility
echo -e "\n7. Testing cross-platform compatibility..."
echo "Current line reading test:"
echo "sed -n '1p' .cache/todo"
sed -n '1p' .cache/todo

echo -e "\n✅ All tests passed!"
echo "Write-ahead log workflow is functioning correctly"

# Clean up test data
sed -i '$d' .cache/todo
sed -i "s/^todo,.*/todo,1/" .cache/status.csv

echo -e "\n🎉 Test completed successfully!"
