# Cursor Chat Management Guide - ADCC Analysis Engine v0.6

## 🎯 **When to Start a New Chat**

### ✅ **Start New Chat When:**

#### **Performance Issues:**
- **Slow responses** (taking >30 seconds to respond)
- **Timeouts** or connection errors
- **Context truncation warnings** appear
- **Memory issues** or lag in the interface

#### **Phase Transitions:**
- **Planning → Implementation** (current transition)
- **Foundation → Data Acquisition**
- **Data Processing → Analytics**
- **Analytics → Web UI**
- **Development → Testing/Integration**

#### **Session Management:**
- **After 50-100 messages** in a single conversation
- **Every 2-3 hours** of active development
- **Different focus areas** (e.g., switching from coding to debugging)
- **Major feature completion** (ready for next component)

#### **Context Overload:**
- **Too many open files** referenced
- **Complex multi-step operations** completed
- **Large code changes** implemented
- **Extensive documentation** reviewed

### ❌ **Don't Start New Chat When:**
- **In the middle** of a complex implementation
- **During active debugging** sessions
- **In the middle** of a multi-step operation
- **When you need continuity** for a specific task
- **During critical file operations** (creating dictionaries, Glicko calculations)

## 🔄 **Chat Lifecycle Management**

### **Phase-Based Chat Strategy:**

#### **1. Planning Chat** ✅ **COMPLETED**
- **Purpose:** Architecture, roadmap, project organization
- **Duration:** Until planning phase complete
- **Transition:** When ready to begin implementation

#### **2. Foundation Chat** 🔄 **CURRENT**
- **Purpose:** Configuration, logging, utilities
- **Duration:** Week 1 of implementation
- **Transition:** When Phase 1 complete

#### **3. Data Acquisition Chat**
- **Purpose:** File downloads, validation, error handling
- **Duration:** Week 2 of implementation
- **Transition:** When data acquisition working

#### **4. Data Processing Chat**
- **Purpose:** CSV/Excel processing, data cleaning
- **Duration:** Week 3 of implementation
- **Transition:** When data processing complete

#### **5. Analytics Chat**
- **Purpose:** Glicko implementation, rating calculations
- **Duration:** Week 4 of implementation
- **Transition:** When analytics engine working

#### **6. Web UI Chat**
- **Purpose:** FastAPI, authentication, frontend
- **Duration:** Week 5 of implementation
- **Transition:** When web interface complete

#### **7. Integration Chat**
- **Purpose:** End-to-end testing, deployment
- **Duration:** Final week
- **Transition:** When system complete

## 📋 **Pre-Chat Transition Checklist**

### **Before Starting New Chat:**

#### **1. Save Current Work:**
```bash
# Commit all changes
git add .
git commit -m "Checkpoint: [Phase Name] - [Brief Description]"

# Push to remote (if using)
git push origin main
```

#### **2. Verify Critical Files:**
```bash
# Check key files are saved
ls -la context/
ls -la src/
ls -la tests/

# Verify no unsaved work
git status
```

#### **3. Update Documentation:**
```bash
# Update checklist if needed
# Update roadmap progress
# Update any relevant documentation
```

#### **4. Export Context:**
```bash
# Copy context summary
cp context/New_Chat_Context_Summary_End_Planning.md context/New_Chat_Context_Summary_[Phase].md

# Update context summary with current phase
# Add any new important information
```

## 🚀 **New Chat Setup Protocol**

### **1. Initial Context Setup:**

#### **Reference the Context Summary:**
```markdown
# In new chat, start with:
"Please review context/New_Chat_Context_Summary_[Phase].md for complete project context"

# Then reference specific files:
"See context/Architecture_v0.6.md for system design"
"Check context/Development_Roadmap_v0.6.md for current phase tasks"
"Review context/Development_CHECKLIST.md for progress tracking"
```

#### **Quick Status Check:**
```bash
# Verify project state
git log --oneline -5
ls -la
pytest --collect-only
```

### **2. Context Verification:**

#### **Essential Files to Check:**
```bash
# Project structure
tree src/ -L 2
tree tests/ -L 2

# Documentation
ls -la context/
cat context/Development_CHECKLIST.md | head -20

# Current implementation status
ls -la src/config/ 2>/dev/null || echo "Config not yet implemented"
ls -la src/utils/ 2>/dev/null || echo "Utils not yet implemented"
```

#### **Test Setup Verification:**
```bash
# Check test configuration
pytest --collect-only
python -c "import pytest; print('Pytest version:', pytest.__version__)"

# Verify test structure
ls -la tests/unit/
ls -la tests/integration/
ls -la tests/e2e/
```

## 📊 **Performance Monitoring**

### **Signs of Performance Degradation:**

#### **Response Time:**
- **Good:** <10 seconds
- **Warning:** 10-30 seconds
- **Critical:** >30 seconds

#### **Context Quality:**
- **Good:** AI remembers recent context well
- **Warning:** AI asks for clarification on recent topics
- **Critical:** AI forgets important context

#### **Memory Usage:**
- **Good:** Smooth operation
- **Warning:** Occasional lag
- **Critical:** Frequent freezes or crashes

### **When to Force New Chat:**
```bash
# If experiencing any of these:
# - Multiple timeouts in a row
# - AI forgetting recent context
# - Interface becoming unresponsive
# - Context truncation warnings
```

## 🔧 **Context Preservation Strategies**

### **1. File-Based Context:**
- **Keep all documentation** in `context/` folder
- **Use descriptive commit messages**
- **Reference specific file paths** instead of descriptions
- **Maintain up-to-date context summaries**

### **2. Code-Based Context:**
- **Use clear variable names** and comments
- **Follow consistent naming conventions**
- **Include docstrings** in all functions
- **Use type hints** for clarity

### **3. Documentation-Based Context:**
- **Update README.md** with current status
- **Maintain development checklist**
- **Document key decisions** and rationale
- **Keep architecture documentation** current

## 📝 **Chat Transition Templates**

### **Template 1: Phase Transition**
```markdown
# Phase Transition: [Old Phase] → [New Phase]

## Completed:
- [List of completed tasks]
- [Key achievements]
- [Files created/modified]

## Next Phase Focus:
- [Specific tasks for new phase]
- [Key files to work on]
- [Testing requirements]

## Context Files:
- context/New_Chat_Context_Summary_[NewPhase].md
- context/Architecture_v0.6.md
- context/Development_Roadmap_v0.6.md
```

### **Template 2: Performance Issue**
```markdown
# Performance-Based Transition

## Reason:
- [Specific performance issues]
- [Context overload indicators]
- [Response time degradation]

## Current Status:
- [What was being worked on]
- [Last successful operation]
- [Pending tasks]

## Next Steps:
- [Continue from where left off]
- [Reference specific files]
- [Focus on specific tasks]
```

### **Template 3: Session Management**
```markdown
# Session-Based Transition

## Session Duration:
- [Hours of active development]
- [Number of messages]
- [Major accomplishments]

## Current Focus:
- [What was being implemented]
- [Next immediate tasks]
- [Testing status]

## Context Preservation:
- [Key decisions made]
- [Important files created]
- [Critical configurations]
```

## 🎯 **Best Practices Summary**

### **Do:**
- ✅ **Commit frequently** before transitions
- ✅ **Use descriptive commit messages**
- ✅ **Reference specific file paths**
- ✅ **Maintain up-to-date context summaries**
- ✅ **Monitor performance indicators**
- ✅ **Plan transitions at natural break points**

### **Don't:**
- ❌ **Transition mid-implementation** without saving
- ❌ **Forget to commit** before new chat
- ❌ **Rely on memory** instead of documentation
- ❌ **Ignore performance warnings**
- ❌ **Start new chat** without context preparation

## 🔗 **Quick Reference Commands**

### **Pre-Transition:**
```bash
# Save work
git add .
git commit -m "Checkpoint: [Phase] - [Description]"

# Verify status
git status
git log --oneline -3

# Check key files
ls -la context/
ls -la src/
```

### **Post-Transition:**
```bash
# Verify context
cat context/New_Chat_Context_Summary_[Phase].md | head -20

# Check project state
git log --oneline -5
pytest --collect-only

# Verify structure
tree src/ -L 2
```

---

**Last Updated:** $(date)
**Version:** 1.0
**Ready for Implementation Phase Transitions** 