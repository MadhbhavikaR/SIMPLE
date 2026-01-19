# Write-Ahead Log Cache System

This `.cache/` directory contains intermediate analysis and execution state to enable efficient work resumption without re-analyzing the entire repository.

## Purpose

The write-ahead log system persists:
- Planned tasks and their order
- Discovered issues and bugs
- Research notes and open questions
- Knowledge base of resolved issues
- Execution state for resumption

## Structure

```
.cache/
├── README.md              # This file
├── status.csv             # Current execution pointers
├── todo                   # Planned tasks (ordered)
├── fixme                  # Discovered issues (ordered)
├── research               # Open questions (ordered)
├── kb.md                  # Knowledge base (resolved issues)
└── [optional files]       # Additional context files
```

## Key Principles

1. **Write-Ahead**: All actions are planned and written before execution
2. **Append-Only**: Files are never deleted or reordered
3. **Line-Based**: Each file contains atomic steps on separate lines
4. **Resume Points**: `status.csv` tracks where to continue
5. **Cross-Platform**: Uses native OS commands for line reading

## Usage

1. **Before starting work**: Check `status.csv` for resume points
2. **During work**: Append to `todo`, `fixme`, `research` as needed
3. **After completing a step**: Update the line number in `status.csv`
4. **When discovering issues**: Append to `fixme` with details
5. **When resolving issues**: Add to `kb.md` knowledge base

## Benefits

- **Token Efficiency**: Avoids re-analyzing entire repository
- **Resume Capability**: Can continue from exact point of interruption
- **Audit Trail**: Complete history of all steps and decisions
- **Knowledge Retention**: Prevents rediscovering same solutions
