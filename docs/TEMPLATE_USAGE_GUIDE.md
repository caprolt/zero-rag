# Planning Document Template Usage Guide

## 🚀 Quick Start

This template is designed to work seamlessly with RepoTrackr's parsing engine. Follow these steps to get started:

### 1. Copy the Template
```bash
# Copy the template to your project
cp planning/template-planning-document.md docs/plan.md
```

### 2. Customize for Your Project
Replace all `[placeholder]` text with your actual project information:

- **Project Name**: Your actual project name
- **Repository URL**: Your GitHub repository URL
- **Dates**: Actual start and target completion dates
- **Technology choices**: Your specific tech stack decisions

### 3. Update Task Status
Use the checkbox patterns that RepoTrackr recognizes:

```markdown
- [ ] Task not started (todo)
- [x] Task completed (done)
- [~] Task in progress (doing)
- [!] Task blocked (blocked)
```

### 4. Add to Your Repository
Place the document in one of these locations:
- `docs/plan.md` (recommended)
- `plan.md` (alternative)
- `README.md` (with plan section)

## 📋 Template Sections Explained

### Project Overview
- Basic project information
- Timeline and status tracking
- High-level goals and objectives

### Development Phases
- Organized by development phases
- Each phase has clear tasks and deliverables
- Status tracking for each phase

### Technical Implementation
- Technology stack decisions
- API endpoint planning
- Architecture decisions

### Progress Tracking
- Current status summary
- Milestone tracking
- Blockers and issues

## ✅ Best Practices

### Task Formatting
- Use clear, actionable task descriptions
- Keep tasks specific and measurable
- Update status regularly as work progresses

### Status Updates
- Mark tasks as `[x]` when complete
- Use `[~]` for work in progress
- Use `[!]` for blocked items
- Leave `[ ]` for not started

### Organization
- Group related tasks under phases
- Use consistent formatting throughout
- Keep the document updated regularly

## 🔄 Integration with RepoTrackr

### Automatic Parsing
RepoTrackr will automatically:
- Extract all checkbox tasks
- Calculate completion percentages
- Determine project status (green/yellow/red)
- Track progress over time

### Status Calculation
- 🟢 **Green**: ≥70% complete, no blocked items
- 🟡 **Yellow**: 30-69% complete, ≤1 blocked task
- 🔴 **Red**: <30% complete, >1 blocked task, or stale

### Real-time Updates
- Update task status in your markdown file
- Commit and push to GitHub
- RepoTrackr will automatically detect changes
- Dashboard will reflect new progress

## 📊 Example Usage

### Starting a New Project
1. Copy the template to `docs/plan.md`
2. Fill in project details
3. Customize phases for your specific project
4. Add initial tasks to Phase 1
5. Commit and push to GitHub
6. Add the repository to RepoTrackr

### During Development
1. Update task status as you work
2. Add new tasks as they're identified
3. Mark blockers when they occur
4. Update progress regularly
5. Commit changes to keep RepoTrackr current

### Project Completion
1. Mark all tasks as complete
2. Update final status and metrics
3. Document lessons learned
4. Archive the project in RepoTrackr

## 🛠️ Customization Tips

### For Different Project Types
- **Web Applications**: Focus on frontend/backend phases
- **Mobile Apps**: Include platform-specific tasks
- **APIs/Services**: Emphasize backend and integration
- **Libraries/Tools**: Focus on documentation and testing

### For Team Projects
- Add assignee information to tasks
- Include code review requirements
- Add team-specific deliverables
- Include stakeholder approval steps

### For Complex Projects
- Break phases into smaller sub-phases
- Add dependency tracking between tasks
- Include risk mitigation strategies
- Add contingency planning

## 📝 Maintenance

### Regular Updates
- Review and update weekly
- Mark completed tasks promptly
- Add new tasks as they're identified
- Update blockers and issues

### Version Control
- Commit changes regularly
- Use descriptive commit messages
- Tag major milestones
- Keep a changelog of significant updates

### Documentation
- Keep the document current
- Add lessons learned
- Document important decisions
- Update success metrics

## 🆘 Troubleshooting

### RepoTrackr Not Detecting Tasks
- Ensure tasks use correct checkbox format
- Check file location (docs/plan.md, plan.md, or README.md)
- Verify markdown syntax is correct
- Check repository permissions

### Incorrect Progress Calculation
- Verify task status markers are correct
- Check for duplicate task titles
- Ensure all tasks are properly formatted
- Review blocked task counts

### Status Not Updating
- Commit and push changes to GitHub
- Check RepoTrackr processing status
- Verify repository URL is correct
- Check for processing errors

## 📞 Support

For help with the template or RepoTrackr integration:
- Check the RepoTrackr documentation
- Review the example planning documents
- Create an issue in the repository
- Contact the development team

---

**Template Version:** 1.0  
**Last Updated:** December 2024  
**Compatible with:** RepoTrackr v1.0+
