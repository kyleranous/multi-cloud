#!/bin/bash
# filepath: /home/kyle/multi_cloud/scripts/unit_tests_all_versions.sh

set -e  # Exit on any error

# Deactivate current virtual environment if one is active
deactivate_current_venv() {
    if [[ -n "$VIRTUAL_ENV" ]]; then
        warning "Currently in virtual environment: $VIRTUAL_ENV"
        log "Deactivating current virtual environment..."
        
        # Check if deactivate function exists
        if type deactivate >/dev/null 2>&1; then
            deactivate
            success "Deactivated virtual environment"
        else
            # Alternative method - unset environment variables
            unset VIRTUAL_ENV
            unset VIRTUAL_ENV_PROMPT
            # Reset PATH by removing venv paths
            export PATH=$(echo $PATH | tr ':' '\n' | grep -v "/venv" | grep -v "/.venv" | tr '\n' ':' | sed 's/:$//')
            warning "Manually cleared virtual environment variables"
        fi
    else
        log "No virtual environment currently active"
    fi
}

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
RESULTS_DIR="${PROJECT_ROOT}/test_results/${TIMESTAMP}"

# Supported Python versions (adjust as needed)
PYTHON_VERSIONS=("3.11" "3.12" "3.13" "3.14")

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Arrays to store results
declare -a RESULTS
declare -a COVERAGE_RESULTS
declare -a FAILED_VERSIONS

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Create results directory with timestamp
create_results_dir() {
    mkdir -p "${RESULTS_DIR}"
    log "Created results directory: ${RESULTS_DIR}"
    
    # Create a summary info file
    cat > "${RESULTS_DIR}/test_run_info.txt" << EOF
MultiCloud Test Run Information
===============================
Test Run Started: $(date)
Project Root: ${PROJECT_ROOT}
Python Versions: ${PYTHON_VERSIONS[*]}
Results Directory: ${RESULTS_DIR}
Initial Virtual Environment: ${VIRTUAL_ENV:-"None"}
EOF
}

# Check if virtual environment exists
check_venv() {
    local version=$1
    local venv_path="${PROJECT_ROOT}/venv${version}"
    
    if [[ ! -d "$venv_path" ]]; then
        error "Virtual environment for Python $version not found at $venv_path"
        # List available venv directories for debugging
        log "Available virtual environments:"
        ls -la "$PROJECT_ROOT" | grep -E "venv|\.venv" || echo "No virtual environments found"
        return 1
    fi
    
    if [[ ! -f "$venv_path/bin/activate" ]]; then
        error "Activation script not found for Python $version venv"
        return 1
    fi
    
    return 0
}

# Install dependencies in virtual environment
install_dependencies() {
    local version=$1
    local venv_path="${PROJECT_ROOT}/venv${version}"
    local install_log="${RESULTS_DIR}/install_${version}.log"
    
    log "Installing dependencies for Python $version..."
    
    # Use a subshell to avoid contaminating the parent shell environment
    (
        # Ensure we start clean
        unset VIRTUAL_ENV
        unset VIRTUAL_ENV_PROMPT
        
        # Activate the specific virtual environment
        source "$venv_path/bin/activate"
        
        # Verify we're in the right environment
        log "Activated virtual environment: $VIRTUAL_ENV"
        
        # Upgrade pip first
        log "Upgrading pip..."
        python -m pip install --upgrade pip --quiet 2>&1 | tee -a "$install_log"
        
        # Install requirements.txt if it exists
        if [[ -f "${PROJECT_ROOT}/requirements.txt" ]]; then
            log "Installing requirements.txt..."
            pip install -r "${PROJECT_ROOT}/requirements.txt" --quiet 2>&1 | tee -a "$install_log"
        else
            warning "requirements.txt not found, skipping..."
        fi
        
        # Install package in editable mode
        log "Installing package in editable mode..."
        pip install -e "${PROJECT_ROOT}" --quiet 2>&1 | tee -a "$install_log"
        
        # Save installed packages list
        pip list > "${RESULTS_DIR}/packages_${version}.txt"
        
        # Verify key packages are installed
        log "Verifying installation..."
        python -c "
import sys
packages = ['pytest', 'coverage', 'click']
missing = []
for pkg in packages:
    try:
        __import__(pkg)
    except ImportError:
        missing.append(pkg)

if missing:
    print(f'Missing packages: {missing}')
    sys.exit(1)
else:
    print('All key packages verified')
" 2>&1 | tee -a "$install_log"
    )
}

# Run tests for a specific Python version
run_tests_for_version() {
    local version=$1
    local venv_path="${PROJECT_ROOT}/venv${version}"
    local result_file="${RESULTS_DIR}/pytest_${version}.xml"
    local coverage_file="${RESULTS_DIR}/coverage_${version}.xml"
    local coverage_html_dir="${RESULTS_DIR}/htmlcov_${version}"
    local log_file="${RESULTS_DIR}/test_${version}.log"
    
    log "Running tests for Python $version..."
    
    # Change to project root
    cd "$PROJECT_ROOT"
    
    # Install dependencies first
    if ! install_dependencies "$version"; then
        error "Failed to install dependencies for Python $version"
        return 1
    fi
    
    # Use a subshell to avoid contaminating the parent shell environment
    (
        # Ensure we start clean
        unset VIRTUAL_ENV
        unset VIRTUAL_ENV_PROMPT
        
        # Activate the specific virtual environment
        source "$venv_path/bin/activate"
        
        # Verify Python version
        local actual_version
        actual_version=$(python --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1-2)
        log "Activated Python $actual_version (expected $version)"
        
        # Save environment info
        cat > "${RESULTS_DIR}/env_${version}.txt" << EOF
Python Version: $(python --version)
Virtual Environment: $VIRTUAL_ENV
Working Directory: $(pwd)
Python Path: $(which python)
Pip Version: $(pip --version)
EOF
        
        # Run pytest with coverage
        log "Running pytest with coverage..."
        python -m pytest \
            --cov=multicloud \
            --cov-report=xml:"$coverage_file" \
            --cov-report=html:"$coverage_html_dir" \
            --cov-report=term \
            --junit-xml="$result_file" \
            --verbose \
            tests/ 2>&1 | tee "$log_file"
        
        local exit_code=${PIPESTATUS[0]}
        return $exit_code
    )
}

# Extract coverage percentage from XML file
extract_coverage() {
    local coverage_file=$1
    
    if [[ -f "$coverage_file" ]]; then
        python3 -c "
import xml.etree.ElementTree as ET
try:
    tree = ET.parse('$coverage_file')
    root = tree.getroot()
    coverage = root.attrib.get('line-rate', '0')
    percentage = float(coverage) * 100
    print(f'{percentage:.1f}%')
except Exception as e:
    print('N/A')
"
    else
        echo "N/A"
    fi
}

# Extract test count from XML file
extract_test_count() {
    local result_file=$1
    
    if [[ -f "$result_file" ]]; then
        python3 -c "
import xml.etree.ElementTree as ET
try:
    tree = ET.parse('$result_file')
    root = tree.getroot()
    
    # Try different possible XML structures
    # Some pytest versions use 'testsuite' as root, others use 'testsuites'
    if root.tag == 'testsuites':
        # Multiple test suites
        total_tests = 0
        total_failures = 0
        total_errors = 0
        for testsuite in root.findall('testsuite'):
            total_tests += int(testsuite.get('tests', 0))
            total_failures += int(testsuite.get('failures', 0))
            total_errors += int(testsuite.get('errors', 0))
        print(f'{total_tests} tests, {total_failures} failures, {total_errors} errors')
    elif root.tag == 'testsuite':
        # Single test suite
        tests = root.get('tests', '0')
        failures = root.get('failures', '0')
        errors = root.get('errors', '0')
        print(f'{tests} tests, {failures} failures, {errors} errors')
    else:
        # Try to count testcase elements directly
        testcases = root.findall('.//testcase')
        tests = len(testcases)
        failures = len(root.findall('.//failure'))
        errors = len(root.findall('.//error'))
        print(f'{tests} tests, {failures} failures, {errors} errors')
        
except Exception as e:
    print(f'Parse error: {e}')
" 2>/dev/null || echo "Unable to parse XML"
    else
        echo "No results file"
    fi
}

# Generate summary report
generate_summary_report() {
    local summary_file="${RESULTS_DIR}/summary_report.md"
    
    cat > "$summary_file" << EOF
# MultiCloud Test Results Summary

**Test Run:** ${TIMESTAMP}  
**Date:** $(date)  
**Project:** MultiCloud Framework

## Results Overview

| Python Version | Status | Tests | Coverage | Log File |
|----------------|--------|-------|----------|----------|
EOF

    for i in "${!PYTHON_VERSIONS[@]}"; do
        local version=${PYTHON_VERSIONS[$i]}
        local status=${RESULTS[$i]}
        local coverage=${COVERAGE_RESULTS[$i]}
        local result_file="${RESULTS_DIR}/pytest_${version}.xml"
        local test_count
        test_count=$(extract_test_count "$result_file")
        
        if [[ "$status" == "PASS" ]]; then
            echo "| $version | ✅ $status | $test_count | $coverage | [test_${version}.log](test_${version}.log) |" >> "$summary_file"
        else
            echo "| $version | ❌ $status | $test_count | $coverage | [test_${version}.log](test_${version}.log) |" >> "$summary_file"
        fi
    done
    
    cat >> "$summary_file" << EOF

## Files Generated

- \`summary_report.md\` - This summary report
- \`test_run_info.txt\` - Test run configuration
- \`pytest_{version}.xml\` - JUnit test results for each Python version
- \`coverage_{version}.xml\` - Coverage report XML for each Python version
- \`htmlcov_{version}/\` - HTML coverage reports for each Python version
- \`test_{version}.log\` - Test execution logs for each Python version
- \`install_{version}.log\` - Installation logs for each Python version
- \`packages_{version}.txt\` - Installed packages list for each Python version
- \`env_{version}.txt\` - Environment information for each Python version

## Coverage Reports

EOF

    for version in "${PYTHON_VERSIONS[@]}"; do
        if [[ -d "${RESULTS_DIR}/htmlcov_${version}" ]]; then
            echo "- [Python $version HTML Coverage Report](htmlcov_${version}/index.html)" >> "$summary_file"
        fi
    done

    log "Summary report generated: $summary_file"
}

# Display final results
display_results() {
    echo
    echo "========================================"
    echo "           TEST RESULTS SUMMARY"
    echo "========================================"
    echo
    
    printf "%-10s %-15s %-25s %-15s\n" "Python" "Status" "Tests" "Coverage"
    echo "----------------------------------------------------------------"
    
    for i in "${!PYTHON_VERSIONS[@]}"; do
        local version=${PYTHON_VERSIONS[$i]}
        local status=${RESULTS[$i]}
        local coverage=${COVERAGE_RESULTS[$i]}
        local result_file="${RESULTS_DIR}/pytest_${version}.xml"
        local test_count
        test_count=$(extract_test_count "$result_file")
        
        if [[ "$status" == "PASS" ]]; then
            printf "%-10s ${GREEN}%-15s${NC} %-25s %-15s\n" "$version" "$status" "$test_count" "$coverage"
        else
            printf "%-10s ${RED}%-15s${NC} %-25s %-15s\n" "$version" "$status" "$test_count" "$coverage"
        fi
    done
    
    echo
    
    # Summary statistics
    local total_versions=${#PYTHON_VERSIONS[@]}
    local failed_count=${#FAILED_VERSIONS[@]}
    local passed_count=$((total_versions - failed_count))
    
    if [[ $failed_count -eq 0 ]]; then
        success "All $total_versions Python versions passed! 🎉"
    else
        warning "$passed_count/$total_versions Python versions passed"
        error "Failed versions: ${FAILED_VERSIONS[*]}"
    fi
    
    echo
    echo "Results saved to: $RESULTS_DIR"
    echo "Summary report: ${RESULTS_DIR}/summary_report.md"
    echo "Test run timestamp: $TIMESTAMP"
    echo
}

# Main execution
main() {
    log "Starting multi-version test run..."
    log "Project root: $PROJECT_ROOT"
    log "Results will be saved to: $RESULTS_DIR"
    
    # Deactivate any current virtual environment first
    deactivate_current_venv
    
    create_results_dir
    
    # Check if requirements.txt exists
    if [[ -f "${PROJECT_ROOT}/requirements.txt" ]]; then
        log "Found requirements.txt"
    else
        warning "requirements.txt not found at ${PROJECT_ROOT}/requirements.txt"
    fi
    
    # Check all virtual environments first
    log "Checking virtual environments..."
    for version in "${PYTHON_VERSIONS[@]}"; do
        if ! check_venv "$version"; then
            error "Setup check failed for Python $version"
            exit 1
        else
            success "Python $version venv found"
        fi
    done
    
    # Run tests for each version
    for version in "${PYTHON_VERSIONS[@]}"; do
        echo
        log "=========================================="
        log "Testing Python $version"
        log "=========================================="
        
        if run_tests_for_version "$version"; then
            RESULTS+=("PASS")
            success "Python $version tests passed"
        else
            RESULTS+=("FAIL")
            FAILED_VERSIONS+=("$version")
            error "Python $version tests failed"
        fi
        
        # Extract coverage
        local coverage_file="${RESULTS_DIR}/coverage_${version}.xml"
        local coverage
        coverage=$(extract_coverage "$coverage_file")
        COVERAGE_RESULTS+=("$coverage")
        
        log "Python $version coverage: $coverage"
    done
    
    # Generate summary report
    generate_summary_report
    
    # Display final results
    display_results
    
    # Exit with error if any version failed
    if [[ ${#FAILED_VERSIONS[@]} -gt 0 ]]; then
        exit 1
    fi
}

# Check if running directly (not sourced)
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi