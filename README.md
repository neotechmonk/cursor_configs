# Cursor Rules Repository

A comprehensive collection of Cursor rules for Python development, Git workflows, memory management, and more. This repository provides standardized development practices that can be easily integrated into any project.

## Project Organization

This repository is organized as a standard Cursor rules structure that can be integrated into any project:

```
.cursor/
└── rules/
    ├── python/           # Python development rules (numbered by priority)
    ├── git.mdc          # Git workflow standards
    ├── memory-management.mdc  # Documentation and task tracking
    ├── plan-updates.mdc # Surgical update guidelines
    └── rule-creation.mdc # Standards for creating new rules
```

**Key Principles:**
- **Hierarchical organization**: Rules are grouped by domain (python/, git/, etc.)
- **Numbered priorities**: Python rules use numbered prefixes for importance order
- **Single responsibility**: Each rule file focuses on one specific domain
- **Consistent naming**: `.mdc` extension for all rule files
- **Template-based**: Rules can be copied and customized per project

## Quick Start

### Option 1: Git Subtree (Recommended for Teams)

**Initial Setup:**
```bash
# Add this repository as a subtree in your project
git subtree add --prefix=.cursor https://github.com/neotechmonk/cursor_configs.git main --squash
```

**Daily Usage:**
```bash
# Edit project-specific rules in .cursor/rules/
git add .cursor/
git commit -m "Update cursor rules"
git push origin your-branch

# Push team rule updates (requires PR approval)
git subtree push --prefix=.cursor https://github.com/neotechmonk/cursor_configs.git main

# Get latest team updates
git subtree pull --prefix=.cursor https://github.com/neotechmonk/cursor_configs.git main --squash
```

### Option 2: Manual Copy (Simple Projects)

**Copy Rules to Your Project:**
```bash
# Clone this repository
git clone https://github.com/neotechmonk/cursor_configs.git

# Copy the .cursor directory to your project
cp -r cursor_configs/.cursor /path/to/your/project/

# Or copy specific rule categories
cp -r cursor_configs/.cursor/rules/python /path/to/your/project/.cursor/rules/
cp -r cursor_configs/.cursor/rules/git /path/to/your/project/.cursor/rules/
```

### Option 3: Symlink (Development)

**Create Symlink for Development:**
```bash
# Create symlink to this repository
ln -s /path/to/cursor_configs/.cursor /path/to/your/project/.cursor

# Note: This approach is good for development but not for production
```

## Available Rules

### Python Development
- **Python Structure** (`python/1. python_structure.mdc`): Secure coding practices
- **Python Coding** (`python/2. python_coding.mdc`): Design patterns and best practices
- **Python Performance** (`python/3. python_performance.mdc`): Optimization strategies
- **Python Testing** (`python/5. python_testing.mdc`): Testing guidelines
- **Python Tooling** (`python/6. python_tooling.mdc`): Packaging and deployment
- **Python Debugging** (`python/7. python_debugging.mdc`): Debugging strategies
- **Python Linting** (`python/8. python-linting.mdc`): Code quality with Ruff
- **Python Deployment** (`python/9. python-deployment.mdc`): Deployment best practices

### Git & Workflow
- **Git Standards** (`git.mdc`): Commit message standards and guidelines
- **Memory Management** (`memory-management.mdc`): Documentation and task tracking
- **Plan Updates** (`plan-updates.mdc`): Surgical, focused updates

### General
- **Rule Creation** (`rule-creation.mdc`): Standards for creating new Cursor rules

## Rule Categories

### Core Rules (Always Include)
- `rule-creation.mdc` - Essential for maintaining rule standards
- `git.mdc` - Git workflow standards

### Python Projects
Include all Python rules for comprehensive coverage:
```bash
cp -r .cursor/rules/python /path/to/your/project/.cursor/rules/
```

### Documentation-Heavy Projects
Include memory management rules:
```bash
cp -r .cursor/rules/memory-management.mdc /path/to/your/project/.cursor/rules/
```

## Customization

### Project-Specific Rules
Create your own rules in `.cursor/rules/` alongside the shared ones:

```bash
# Your project structure
.cursor/rules/
├── python/                    # Shared Python rules
├── git.mdc                    # Shared Git rules
├── my-project-rules.mdc      # Your custom rules
└── team-standards.mdc        # Team-specific standards
```

### Rule Override
Rules are processed in order, so you can override shared rules by placing your custom rules after them in the directory listing.

## Maintenance

### Updating Rules
- **Git Subtree**: Use `git subtree pull` to get latest updates
- **Manual Copy**: Re-copy rules when you need updates
- **Symlink**: Updates are automatic but affect all linked projects

### Contributing Back
1. Fork this repository
2. Make your improvements
3. Submit a pull request
4. Once approved, your rules become available to the team

## Best Practices

### For Teams
- Use Git subtree for consistent rule sharing
- Establish PR review process for rule changes
- Regular sync meetings to discuss rule improvements
- Document any project-specific customizations

### For Individual Projects
- Start with core rules (git, rule-creation)
- Add Python rules if developing Python code
- Copy memory management rules for documentation projects
- Customize rules to fit your workflow

### For Open Source
- Fork and customize rules for your project
- Consider contributing improvements back
- Maintain compatibility with upstream changes

## Troubleshooting

### Common Issues

**Rules Not Working:**
- Ensure `.cursor/rules/` directory exists
- Check file extensions are `.mdc`
- Verify rule syntax in Cursor

**Git Subtree Conflicts:**
```bash
# Resolve conflicts manually
git status
# Edit conflicted files
git add .
git commit -m "Resolve subtree conflicts"
```

**Performance Issues:**
- Large rule sets may slow down Cursor
- Consider using only essential rules
- Use symlinks for development, copies for production

## Support

- **Issues**: Report problems on GitHub
- **Discussions**: Use GitHub Discussions for questions
- **Contributions**: Submit PRs for improvements
- **Documentation**: Check this README and individual rule files

## License

This project is licensed under the MIT License - see the LICENSE file for details.
