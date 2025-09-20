# Test Coverage Template

## Change Log
|Date|Change description|
|----|------------------|
<!-- INSTRUCTIONS: Succinct but refer to specific test updates or coverage changes -->

<!-- INSTRUCTIONS FOR AGENT: This template follows the test coverage documentation format established in the event-bus module. 
Delete all markdown comments (lines starting with <!--) before finalizing the document. 
Fill in all placeholder content within [brackets]. Follow the structure exactly as provided.

This template is designed for use during TDD cycles to document test coverage progress and provide interactive test execution capabilities.

Always prioritize readability and meaningfulness over following the template exactly. 
E.g. If there are no integration tests, remove that section entirely.
-->

## Module Overview
- **Module**: `[module_path]`
- **Total Tests**: [X] ([Y] unit + [Z] integration)
- **Coverage**: [X]% of acceptance criteria
- **Status**: [✅ Production Ready | 🔄 In Progress | ⚠️ Needs Attention]

<!-- INSTRUCTIONS: Update these metrics as tests are implemented during TDD cycles. 
Status should reflect current implementation state, not just test count. -->

## 🚀 Quick Test Execution
All test names below are **clickable links** that will run the specific test in your terminal:

### Run All Tests
```bash
# All [module_name] tests
uv run pytest tests/[module_path]/

# Unit tests only
uv run pytest tests/[module_path]/unit/

# Integration tests only  
uv run pytest tests/[module_path]/integration/
```

### Run from Test Directory
```bash
# Navigate to test directory first
cd tests/[module_path]/unit/
uv run pytest [test_file].py::[TestClass]::[test_function]

# Or from integration directory
cd tests/[module_path]/integration/
uv run pytest [test_file].py::[test_function]
```

### Run Specific Test
Click any test name below to run that specific test, or copy the command from the link.

<!-- INSTRUCTIONS: Update the directory paths to match the actual module structure. 
The clickable links should use shorter paths (just filename::class::function) for readability. -->

## Test Structure
```
tests/[module_path]/
├── unit/
│   └── [test_file].py          # [X] unit tests
├── integration/
│   └── [test_file].py          # [Y] integration tests
└── test-coverage.md            # This document
```

<!-- INSTRUCTIONS: Update the file structure to match the actual test organization. 
Follow the python/5. python_testing.mdc structure convention. -->

## Unit Test Coverage

### `tests/[module_path]/unit/[test_file].py`

#### Classes Coverage
| Class | Methods | Tests | Coverage |
|-------|---------|-------|----------|
| `[ClassName]` | [X] methods | [Y] tests | [Z]% |
| `[AnotherClass]` | [X] methods | [Y] tests | [Z]% |

<!-- INSTRUCTIONS: List all classes being tested with their method and test counts. 
Update coverage percentages as tests are implemented during TDD cycles. -->

#### Method Coverage Detail

**[ClassName.method_name()]**
**Priority**: [🔴 Critical | 🟡 High | 🟢 Normal]
- ✅ **[Test description]** - [`test_function_name`](command:uv run pytest [test_file].py::[TestClass]::[test_function_name])
- ✅ **[Test description]** - [`test_function_name`](command:uv run pytest [test_file].py::[TestClass]::[test_function_name])
- ❌ **[Test description]** - [`test_function_name`](command:uv run pytest [test_file].py::[TestClass]::[test_function_name])
- ⏳ **[Test description]** - [`test_function_name`](command:uv run pytest [test_file].py::[TestClass]::[test_function_name])

<!-- INSTRUCTIONS: 
- Use RGB priority system: 🔴 Critical (must work), 🟡 High (should work), 🟢 Normal (nice to have)
- Use status indicators: ✅ Passing, ❌ Failing, ⚠️ Warning, 🚫 Broken, ⏳ Pending, 🔄 In Progress
- Include clickable links for each test using shorter paths
- Group tests by the method/functionality they test
- Update status as tests are implemented during TDD cycles
-->

### Unit Test Priority Distribution
| Priority | Count | Status | Coverage |
|----------|-------|--------|----------|
| 🔴 Critical | [X] tests | [Status] | [Y]% |
| 🟡 High | [X] tests | [Status] | [Y]% |
| 🟢 Normal | [X] tests | [Status] | [Y]% |

<!-- INSTRUCTIONS: Update counts and status as tests are implemented. 
Status should reflect overall health of tests in that priority level. -->

## Integration Test Coverage

### `tests/[module_path]/integration/[test_file].py`

#### End-to-End Scenarios
| Test Name | Priority | Status | Coverage |
|-----------|----------|--------|----------|
| [`test_function_name`](command:uv run pytest [test_file].py::[test_function_name]) | 🔴 Critical | ✅ | [Description of what this tests] |
| [`test_function_name`](command:uv run pytest [test_file].py::[test_function_name]) | 🟡 High | ✅ | [Description of what this tests] |

<!-- INSTRUCTIONS: 
- Only include integration tests if they exist
- Use same priority and status system as unit tests
- Include clickable links with shorter paths
- Describe what each integration test covers
-->

### Integration Test Priority Distribution
| Priority | Count | Status | Coverage |
|----------|-------|--------|----------|
| 🔴 Critical | [X] tests | [Status] | [Y]% |
| 🟡 High | [X] tests | [Status] | [Y]% |
| 🟢 Normal | [X] tests | [Status] | [Y]% |

<!-- INSTRUCTIONS: Update counts and status as integration tests are implemented. -->

## Priority-Based Coverage Matrix

### 🔴 Critical Priority (Must Work)
| Feature | Unit Tests | Integration Tests | Status | Risk Level |
|---------|------------|------------------|--------|------------|
| [Feature name] | [X] tests | [Y] tests | [Status] | [Low/Medium/High] |
| [Feature name] | [X] tests | [Y] tests | [Status] | [Low/Medium/High] |

### 🟡 High Priority (Should Work)
| Feature | Unit Tests | Integration Tests | Status | Risk Level |
|---------|------------|------------------|--------|------------|
| [Feature name] | [X] tests | [Y] tests | [Status] | [Low/Medium/High] |
| [Feature name] | [X] tests | [Y] tests | [Status] | [Low/Medium/High] |

### 🟢 Normal Priority (Nice to Have)
| Feature | Unit Tests | Integration Tests | Status | Risk Level |
|---------|------------|------------------|--------|------------|
| [Feature name] | [X] tests | [Y] tests | [Status] | [Low/Medium/High] |
| [Feature name] | [X] tests | [Y] tests | [Status] | [Low/Medium/High] |

<!-- INSTRUCTIONS: 
- Map features to their test coverage across unit and integration tests
- Use risk levels: Low (well tested), Medium (some gaps), High (needs attention)
- Update as features are implemented during TDD cycles
- Remove priority levels that don't apply to the module
-->

## Test Status Legend
- ✅ **Passing** - Test is implemented and passing
- ❌ **Failing** - Test is implemented but failing
- ⚠️ **Warning** - Test has issues or needs attention
- 🚫 **Broken** - Test is broken and needs fixing
- ⏳ **Pending** - Test is planned but not implemented
- 🔄 **In Progress** - Test is currently being worked on

<!-- INSTRUCTIONS: Keep this legend consistent across all test coverage documents. -->

## Coverage Summary

### Overall Health
- **Total Tests**: [X]
- **Unit Tests**: [Y] ([Z]%)
- **Integration Tests**: [W] ([V]%)
- **Passing**: [X] ([Y]%)
- **Failing**: [X] ([Y]%)
- **Warning**: [X] ([Y]%)
- **Broken**: [X] ([Y]%)
- **Pending**: [X] ([Y]%)

### Priority Distribution
- **🔴 Critical**: [X] tests ([Y]%) - [Status]
- **🟡 High**: [X] tests ([Y]%) - [Status]
- **🟢 Normal**: [X] tests ([Y]%) - [Status]

<!-- INSTRUCTIONS: Update these metrics as tests are implemented during TDD cycles. 
Use percentages to show distribution across test types and priorities. -->

## Test File Responsibilities

### Unit Tests (`[test_file].py`)
- **Purpose**: Test individual components in isolation
- **Scope**: Single class/method behavior
- **Dependencies**: Mocked or stubbed
- **Speed**: Fast execution
- **Coverage**: [X] tests covering [description]

### Integration Tests (`[test_file].py`)
- **Purpose**: Test component interactions and real-world scenarios
- **Scope**: Multi-component workflows
- **Dependencies**: Real implementations with minimal I/O
- **Speed**: Moderate execution
- **Coverage**: [X] tests covering [description]

<!-- INSTRUCTIONS: 
- Update file names to match actual test files
- Describe what each test type covers in this specific module
- Adjust descriptions based on the module's complexity and requirements
-->

## Recommendations

### ✅ Strengths
- [List current strengths of the test coverage]
- [Highlight well-tested areas]
- [Note good test organization]

### 🔄 Future Considerations
- [Areas that need more testing]
- [Performance considerations]
- [Monitoring or observability needs]
- [Edge cases to consider]

<!-- INSTRUCTIONS: 
- Update based on current test coverage state
- Focus on actionable recommendations
- Consider both immediate needs and long-term maintainability
-->

## Last Updated
- **Date**: [YYYY-MM-DD]
- **Version**: [X.Y.Z]
- **Status**: [Current implementation status]

<!-- INSTRUCTIONS: Always update the timestamp and version when making changes to maintain version history. 
Status should reflect the current state of the module implementation and testing. -->

<!-- INSTRUCTIONS FOR AGENT: 
When using this template during TDD cycles:

1. **RED Phase**: Mark tests as ⏳ Pending, create failing tests, mark as ❌ Failing
2. **GREEN Phase**: Update status to ✅ Passing as tests are implemented
3. **REFACTOR Phase**: Update coverage metrics and recommendations

Always update the coverage summary and priority distribution as tests are implemented.
Use the clickable links to quickly run specific tests during development.
Keep the document current with the actual test implementation state.
-->
