# Trello Integration for Task Management

## Overview

The Memory Bank provides project context and knowledge, while Trello manages actionable tasks, progress tracking, and workflow states. This separation keeps the Memory Bank focused on "what we know" while Trello handles "what we need to do."

## Trello Board Structure

### Standard Lists
1. **Backlog** - Tasks identified but not yet prioritized
2. **Ready** - Tasks ready to be worked on with clear requirements
3. **In Progress** - Tasks currently being worked on
4. **Testing** - Tasks completed but requiring validation
5. **Done** - Completed and validated tasks

### Card Categories (Labels)
- 🔴 **Critical** - Blocking issues or security concerns
- 🟠 **High Priority** - Important features or improvements
- 🟡 **Medium Priority** - Standard development tasks
- 🟢 **Low Priority** - Nice-to-have features or optimizations
- 🔵 **Technical Debt** - Code quality improvements
- 🟣 **Documentation** - Documentation updates or creation
- ⚫ **Infrastructure** - DevOps, deployment, or infrastructure tasks

## Workflow Integration

### Task Discovery Process
1. **Memory Bank Analysis** - Review memory bank for gaps, issues, or opportunities
2. **Trello Query** - Check existing cards to avoid duplication
3. **Card Creation** - Create new cards with proper categorization
4. **Prioritization** - Assign appropriate labels and move to correct list

### Development Workflow
```
Backlog → Ready → In Progress → Testing → Done
```

#### Starting Work
1. Query Trello for "Ready" tasks
2. Move selected card to "In Progress"
3. Update Memory Bank with current focus in `activeContext.md`
4. Begin development work

#### During Development
1. Update card with progress notes and blockers
2. Create sub-tasks or related cards as needed
3. Move cards between states as work progresses

#### Completing Work
1. Move card to "Testing"
2. Validate functionality (manual testing, automated tests, etc.)
3. Update Memory Bank with new patterns, learnings, or context
4. Move card to "Done" after validation
5. Update `progress.md` with completed work

### Trello Operations

#### Querying Tasks
- **Get Ready Tasks**: `get_cards_by_list_id` for Ready list
- **Check In Progress**: `get_cards_by_list_id` for In Progress list
- **Review Backlog**: `get_cards_by_list_id` for Backlog list
- **Get My Tasks**: `get_my_cards` for assigned tasks

#### Managing Cards
- **Create Task**: `add_card_to_list` with proper description and labels
- **Update Progress**: `update_card_details` with status updates
- **Move Cards**: `move_card` between workflow states
- **Archive Completed**: `archive_card` for old completed tasks

#### Board Management
- **Recent Activity**: `get_recent_activity` to understand recent changes
- **List Management**: `get_lists` to understand board structure

## Memory Bank Integration

### Reduced Memory Bank Scope
The Memory Bank should focus on:
- **Project Context** - Why, what, and how the project works
- **Technical Patterns** - Architecture, design decisions, and implementation patterns
- **Current Focus** - What's being worked on right now
- **Key Learnings** - Important insights and decisions made

### Removed from Memory Bank
- **Detailed Task Lists** - Move to Trello cards
- **Progress Tracking** - Use Trello workflow states
- **Future Feature Lists** - Create as Backlog cards
- **Issue Tracking** - Create as prioritized cards

### Updated Memory Bank Files

#### `activeContext.md` Changes
- Focus on current work context, not task lists
- Reference Trello cards by ID for current work
- Document patterns and decisions from current work
- Keep next steps high-level, detailed tasks in Trello

#### `progress.md` Changes
- Document major milestones and releases
- Focus on "what works" rather than "what's left"
- Reference Trello for current status of pending work
- Keep evolution history and architectural decisions

## Automation Rules

### Automatic Card Movement
1. **Starting Work** - Move from Ready → In Progress when work begins
2. **Code Complete** - Move from In Progress → Testing when implementation done
3. **Validation Complete** - Move from Testing → Done when validated
4. **Stale Cards** - Flag cards in In Progress for >1 week without updates

### Card Creation Triggers
1. **Bug Discovery** - Create Critical/High priority cards for bugs found
2. **Technical Debt** - Create Technical Debt cards when code quality issues identified
3. **Feature Requests** - Create appropriately prioritized cards for new features
4. **Documentation Gaps** - Create Documentation cards when gaps identified

### Memory Bank Updates
1. **After Major Features** - Update system patterns and technical context
2. **After Architecture Changes** - Update system patterns and active context
3. **After Releases** - Update progress with new capabilities
4. **Weekly Reviews** - Update active context with current focus and learnings

## Best Practices

### Card Creation
- **Clear Titles** - Descriptive, actionable titles
- **Detailed Descriptions** - Include context, requirements, and acceptance criteria
- **Proper Labels** - Use priority and category labels consistently
- **Due Dates** - Set realistic due dates for time-sensitive tasks
- **Assignments** - Assign cards to specific team members when applicable

### Card Management
- **Regular Updates** - Update cards with progress, blockers, and notes
- **Link Related Work** - Reference related cards, PRs, or documentation
- **Attachment Usage** - Attach relevant files, screenshots, or links
- **Comment History** - Use comments for status updates and decisions

### Board Hygiene
- **Archive Old Cards** - Archive completed cards older than 30 days
- **Review Backlog** - Regularly review and prioritize backlog items
- **Update Descriptions** - Keep card descriptions current with changing requirements
- **Label Consistency** - Maintain consistent labeling across all cards

## Integration Commands

### Query Commands
```
- Check what's ready to work on
- Show my current tasks
- Get recent board activity
- List backlog items by priority
```

### Management Commands
```
- Create task for [description]
- Move [task] to testing
- Update [task] with [progress]
- Archive completed tasks
```

### Workflow Commands
```
- Start work on [task]
- Complete current task
- Review testing queue
- Update memory bank and Trello
```

## Error Handling

### Trello API Issues
- Graceful degradation when Trello unavailable
- Local task tracking fallback in Memory Bank
- Retry logic for transient failures
- Clear error messages for user guidance

### Sync Issues
- Conflict resolution between Memory Bank and Trello
- Duplicate task detection and merging
- Stale data handling and refresh procedures
- Manual override capabilities when needed

## Reporting and Analytics

### Progress Tracking
- Cards completed per time period
- Average time in each workflow state
- Backlog growth and burn-down rates
- Priority distribution analysis

### Quality Metrics
- Bug card creation rates
- Technical debt accumulation
- Documentation coverage gaps
- Testing task completion rates

This integration transforms the development workflow from memory-based task tracking to a dynamic, queryable system that scales with project complexity while maintaining the Memory Bank's focus on project knowledge and context.