# 🔧 Troubleshooting Guide: Behave Test Failures

## ⚡ TL;DR (3-Line Summary)

1. **Problem**: `environment.py` was in `steps/` directory instead of `features/` directory
2. **Impact**: Behave couldn't find it, so hooks never ran and `context.page` was never created
3. **Fix**: Move `environment.py` to `features/` and copy step files to `features/steps/`

---

## 📋 Problem Description

When running Behave tests, you encounter the following error:

```
Given I am on the internet homepage
  Traceback (most recent call last):
    File "steps\herokuapp_test_steps.py", line 10, in step_navigate_to_homepage
      context.home_page = HomePage(context.page)
                                   ^^^^^^^^^^^^
  AttributeError: 'Context' object has no attribute 'page'
```

## 🔍 Root Cause Analysis (Chain of Thought Reasoning)

### Step 1: Understanding the Error
- **Error Message**: `'Context' object has no attribute 'page'`
- **Meaning**: The `context.page` variable doesn't exist when the test step tries to use it
- **Question**: Where should `context.page` be created?

### Step 2: Tracing the Context Object
- `context.page` is created in the `before_scenario()` hook
- This hook is defined in `environment.py`
- The hook should run automatically before each scenario
- **Question**: Why isn't the hook running?

### Step 3: Understanding Behave's File Discovery
Behave has specific requirements for where files must be located:

```
Behave looks for environment.py in: features/environment.py
Behave looks for step definitions in: features/steps/*.py
```

### Step 4: Identifying the Problem
- **Expected Location**: `features/environment.py` ✅
- **Actual Location**: `steps/environment.py` ❌
- **Result**: Behave can't find `environment.py`, so hooks never run
- **Consequence**: `context.page` is never created → AttributeError

## ✅ Solution

The fix requires reorganizing the project to match Behave's expected structure.

### Step 1: Move `environment.py` to Correct Location

**From**: `steps/environment.py`
**To**: `features/environment.py`

```powershell
# PowerShell command
Move-Item "steps\environment.py" "features\environment.py" -Force
```

### Step 2: Create `features/steps/` Directory

```powershell
New-Item -ItemType Directory -Force -Path "features\steps"
```

### Step 3: Copy Step Definitions

```powershell
Copy-Item "steps\*.py" -Destination "features\steps\" -Force
```

## 📁 Correct Directory Structure

After the fix, your project should look like this:

```
demo/
├── features/                              ← Features directory
│   ├── environment.py                    ✅ MUST be here!
│   ├── steps/                            ← Steps subdirectory
│   │   ├── __init__.py
│   │   ├── common_steps.py
│   │   ├── herokuapp_test_steps.py
│   │   └── login_steps.py
│   ├── example.feature
│   ├── herokuapp_test.feature
│   └── login_console.feature
├── pages/                                 ← Page Object Models
│   ├── __init__.py
│   ├── base_page.py
│   ├── home_page.py
│   └── login_page.py
├── helpers/                               ← Helper utilities
│   ├── auth_helper.py
│   ├── healing_locator.py
│   ├── screenshot_manager.py
│   ├── wait_manager.py
│   └── data_generator.py
├── fixtures/                              ← Test data
│   └── test_data.json
├── reports/                               ← Test reports
│   └── screenshots/
├── behave.ini                             ← Behave configuration
├── requirements.txt                       ← Python dependencies
├── .env                                   ← Environment variables
└── README.md
```

## 🚨 Common Mistakes

### ❌ Mistake 1: Wrong environment.py Location
```
demo/
├── steps/
│   └── environment.py          ❌ WRONG! Hooks won't execute
├── features/
```

**Symptoms**:
- `AttributeError: 'Context' object has no attribute 'page'`
- `AttributeError: 'Context' object has no attribute 'browser'`
- No setup/teardown output in console

### ❌ Mistake 2: Steps Outside features/steps/
```
demo/
├── steps/                      ❌ WRONG! Behave can't find steps
│   └── my_steps.py
├── features/
    └── my_test.feature
```

**Symptoms**:
- Steps show as "undefined" in test output
- Test shows: `Then I should see the header # None`

### ❌ Mistake 3: Missing __init__.py
```
features/
├── steps/
│   ├── common_steps.py        ❌ Missing __init__.py
│   └── login_steps.py
```

**Symptoms**:
- Import errors
- Steps not discovered by Behave

## 🔄 How Behave Works

### Hook Execution Order

```
before_all
    └── before_feature
            └── before_scenario
                    └── before_step
                            └── Execute Step
                            └── after_step
                    └── (repeat for each step)
                    └── after_scenario
            └── (repeat for each scenario)
            └── after_feature
    └── (repeat for each feature)
    └── after_all
```

### Key Hooks in `environment.py`

| Hook | When It Runs | Purpose |
|------|--------------|---------|
| `before_all(context)` | Once before all tests | Initialize browser, set global config |
| `before_scenario(context, scenario)` | Before each scenario | Create `context.page`, setup screenshot manager |
| `after_step(context, step)` | After each step | Capture screenshots, log step status |
| `after_scenario(context, scenario)` | After each scenario | Close page, capture failure screenshots |
| `after_all(context)` | Once after all tests | Close browser, generate reports |

## 🎯 Verification Steps

After applying the fix, verify it works:

### 1. Check File Locations
```powershell
# These should return True
Test-Path "features\environment.py"
Test-Path "features\steps"
```

### 2. Run a Simple Test
```powershell
behave features/example.feature
```

### 3. Look for Initialization Messages
You should see:
```
🚀 Initializing test framework...

✅ Browser: chromium (headless: False)
✅ App URL: http://localhost:3000
✅ Default timeout: 10000ms
```

If you see these messages, `environment.py` is being loaded correctly!

### 4. Verify context.page Exists
In your step definitions, you should be able to use:
```python
@given('I am on the homepage')
def step_impl(context):
    context.page.goto("https://example.com")  # Should work!
```

## 📊 Test Results - Before vs After

### Before Fix ❌
```
Feature: Herokuapp Homepage Navigation
  Scenario: Successfully navigate to Herokuapp homepage
    Given I am on the internet homepage
      AttributeError: 'Context' object has no attribute 'page'

Errored scenarios: 1
0 steps passed, 0 failed, 1 error, 2 skipped
```

### After Fix ✅
```
🚀 Initializing test framework...

Feature: Herokuapp Homepage Navigation
  📝 Scenario: Successfully navigate to Herokuapp homepage

    ✓ Given I am on the internet homepage
    ✓ Then I should see the homepage header
    ✓ And I should see the list of available examples

✅ Scenario passed: Successfully navigate to Herokuapp homepage
📸 Screenshots captured: 3

1 feature passed, 0 failed, 0 skipped
1 scenario passed, 0 failed, 0 skipped
3 steps passed, 0 failed, 0 skipped
```

## 🛠️ Enhanced Quick Fix Script

Run this PowerShell script to automatically fix the structure:

```powershell
# Save as: fix-behave-structure.ps1

$projectRoot = "c:\Users\ksmuv\Downloads\Research\ai-playwright-framework\cli\demo"
cd $projectRoot

Write-Host "🔧 Fixing Behave project structure..." -ForegroundColor Cyan
Write-Host ""

# ============================================================================
# THE ACTUAL ISSUE:
# ============================================================================
# Behave REQUIRES environment.py in the features/ directory (NOT steps/)
# This is because Behave's file discovery mechanism looks for environment.py
# at the root of the features directory to load hooks before running tests.
#
# Without environment.py in the correct location:
# 1. before_all() hook never executes → Browser never initialized
# 2. before_scenario() hook never executes → context.page never created
# 3. Step definitions try to use context.page → AttributeError occurs
#
# This script fixes the structure by moving files to the correct locations.
# ============================================================================

Write-Host "📝 Understanding the problem:" -ForegroundColor Yellow
Write-Host "   • Behave looks for environment.py in features/ directory" -ForegroundColor Gray
Write-Host "   • If it's in steps/, Behave won't find it" -ForegroundColor Gray
Write-Host "   • Result: Hooks don't run, context.page is never created" -ForegroundColor Gray
Write-Host ""

# Step 1: Check if environment.py is in the wrong location
Write-Host "🔍 Step 1: Checking for misplaced environment.py..." -ForegroundColor Cyan
if (Test-Path "steps\environment.py") {
    Write-Host "   ⚠️  Found environment.py in steps/ (WRONG LOCATION!)" -ForegroundColor Yellow
    Write-Host "   → Moving to features/ directory..." -ForegroundColor Gray

    # This is the CRITICAL FIX - moving environment.py to where Behave expects it
    Move-Item "steps\environment.py" "features\environment.py" -Force

    Write-Host "   ✅ Moved environment.py to features/" -ForegroundColor Green
    Write-Host "   → Behave will now find and load hooks properly!" -ForegroundColor Gray
} elseif (Test-Path "features\environment.py") {
    Write-Host "   ✅ environment.py already in correct location (features/)" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  environment.py not found anywhere!" -ForegroundColor Red
    Write-Host "   → You may need to create it manually" -ForegroundColor Gray
}
Write-Host ""

# Step 2: Create features/steps directory if it doesn't exist
Write-Host "🔍 Step 2: Setting up features/steps directory..." -ForegroundColor Cyan
if (!(Test-Path "features\steps")) {
    Write-Host "   → Creating features\steps directory..." -ForegroundColor Gray

    # Step definitions must be in features/steps/ for Behave to discover them
    New-Item -ItemType Directory -Path "features\steps" -Force | Out-Null

    Write-Host "   ✅ Created features\steps/" -ForegroundColor Green
} else {
    Write-Host "   ✅ features\steps/ directory already exists" -ForegroundColor Green
}
Write-Host ""

# Step 3: Copy step definition files to correct location
Write-Host "🔍 Step 3: Copying step definitions..." -ForegroundColor Cyan
if (Test-Path "steps\*.py") {
    Write-Host "   → Copying all .py files from steps/ to features/steps/..." -ForegroundColor Gray

    # Copy step definitions so Behave can discover them
    # Behave automatically loads all Python files from features/steps/
    Copy-Item "steps\*.py" -Destination "features\steps\" -Force

    Write-Host "   ✅ Step definitions copied to features/steps/" -ForegroundColor Green
    Write-Host "   → Behave will auto-discover these step files" -ForegroundColor Gray
} else {
    Write-Host "   ⚠️  No step definition files found in steps/" -ForegroundColor Yellow
}
Write-Host ""

# Step 4: Verify the final structure
Write-Host "📋 Step 4: Verifying project structure..." -ForegroundColor Cyan
$checks = @(
    @{Path="features\environment.py"; Name="environment.py"; Critical=$true},
    @{Path="features\steps"; Name="steps directory"; Critical=$true},
    @{Path="features\steps\__init__.py"; Name="__init__.py"; Critical=$false}
)

$allCriticalPass = $true
foreach ($check in $checks) {
    if (Test-Path $check.Path) {
        Write-Host "   ✅ $($check.Name) - Found" -ForegroundColor Green
    } else {
        if ($check.Critical) {
            Write-Host "   ❌ $($check.Name) - MISSING (CRITICAL!)" -ForegroundColor Red
            $allCriticalPass = $false
        } else {
            Write-Host "   ⚠️  $($check.Name) - Missing (recommended)" -ForegroundColor Yellow
        }
    }
}
Write-Host ""

# Step 5: Display summary and next steps
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "🎉 Structure Fix Complete!" -ForegroundColor Green
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host ""
Write-Host "WHAT WAS FIXED:" -ForegroundColor Yellow
Write-Host "1. Moved environment.py from steps/ to features/" -ForegroundColor White
Write-Host "   → Behave can now find and load hooks" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Ensured features/steps/ directory exists" -ForegroundColor White
Write-Host "   → Step definitions are in the correct location" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Copied step definition files to features/steps/" -ForegroundColor White
Write-Host "   → Behave will auto-discover all step implementations" -ForegroundColor Gray
Write-Host ""
Write-Host "HOW THIS FIXES THE ERROR:" -ForegroundColor Yellow
Write-Host "• before_scenario() hook in environment.py will now run" -ForegroundColor White
Write-Host "• context.page will be initialized before each scenario" -ForegroundColor White
Write-Host "• Step definitions can successfully use context.page" -ForegroundColor White
Write-Host "• No more AttributeError!" -ForegroundColor White
Write-Host ""

if ($allCriticalPass) {
    Write-Host "✅ All critical files in place - ready to run tests!" -ForegroundColor Green
    Write-Host ""
    Write-Host "NEXT STEPS:" -ForegroundColor Yellow
    Write-Host "1. Run your tests: " -NoNewline -ForegroundColor White
    Write-Host "behave features/your-test.feature" -ForegroundColor Cyan
    Write-Host "2. You should now see hook initialization messages" -ForegroundColor White
    Write-Host "3. Tests should execute without AttributeError" -ForegroundColor White
} else {
    Write-Host "⚠️  Some critical files are missing - please review" -ForegroundColor Red
    Write-Host "   Check the verification results above" -ForegroundColor Gray
}
Write-Host ""
```

## 📝 What the Script Fixes

### Before Running Script ❌
```
demo/
├── steps/
│   ├── environment.py          ← PROBLEM: Wrong location
│   ├── common_steps.py
│   └── login_steps.py
└── features/
    └── login.feature
```

### After Running Script ✅
```
demo/
├── features/
│   ├── environment.py          ← FIXED: Correct location
│   ├── steps/
│   │   ├── common_steps.py
│   │   └── login_steps.py
│   └── login.feature
└── steps/
    └── (old files can be deleted)
```

## 🔍 Debugging Checklist

If tests still fail after applying the fix:

- [ ] Verify `features/environment.py` exists
- [ ] Verify `features/steps/` directory exists
- [ ] Verify step definition files are in `features/steps/`
- [ ] Check for Python syntax errors in `environment.py`
- [ ] Verify all imports in `environment.py` are correct
- [ ] Check that `behave.ini` has `paths = features`
- [ ] Ensure virtual environment is activated
- [ ] Verify all dependencies are installed: `pip install -r requirements.txt`
- [ ] Check for conflicting Behave installations: `pip list | grep behave`

## 📚 Additional Resources

- **Behave Documentation**: https://behave.readthedocs.io/
- **Directory Layout**: https://behave.readthedocs.io/en/latest/gherkin.html#directory-layout
- **Environment Controls**: https://behave.readthedocs.io/en/latest/tutorial.html#environmental-controls
- **Context Object**: https://behave.readthedocs.io/en/latest/context_attributes.html

## 💡 Best Practices

1. **Always use the standard Behave structure** - Don't try to customize directory locations
2. **Keep environment.py in features/** - This is non-negotiable for Behave
3. **Use features/steps/ for all step definitions** - Behave automatically discovers them here
4. **Include __init__.py** - Makes the steps directory a proper Python package
5. **Test after changes** - Run a simple test to verify hooks are executing

## 🎓 Understanding Why This Happens

This issue commonly occurs when:

1. **Copying from templates** - Example projects may use non-standard structures
2. **Manual project setup** - Creating files without following Behave conventions
3. **IDE auto-generation** - Some IDEs create incorrect default structures
4. **Migration from other frameworks** - Converting from Cucumber, PyTest-BDD, etc.

The key is to always follow Behave's expected directory structure to ensure hooks and steps are properly discovered.
