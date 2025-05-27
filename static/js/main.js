// Main JavaScript for Coding Test Platform

// Global variables
let isCodeRunning = false

// Initialize when DOM is loaded
document.addEventListener("DOMContentLoaded", () => {
  initializeCodeEditor()
  initializeTooltips()
  initializeConfirmDialogs()
  initializeFormValidation()
})

// Code Editor Functionality
function initializeCodeEditor() {
  const codeTextarea = document.getElementById("code-editor")
  if (codeTextarea) {
    // Add line numbers and syntax highlighting
    addLineNumbers(codeTextarea)

    // Add keyboard shortcuts
    codeTextarea.addEventListener("keydown", handleCodeEditorKeydown)

    // Auto-resize textarea
    codeTextarea.addEventListener("input", autoResizeTextarea)
  }

  // Initialize run code button
  const runButton = document.getElementById("run-code-btn")
  if (runButton) {
    runButton.addEventListener("click", runCode)
  }

  // Initialize submit code button
  const submitButton = document.getElementById("submit-code-btn")
  if (submitButton) {
    submitButton.addEventListener("click", submitCode)
  }
}

// Add line numbers to code editor
function addLineNumbers(textarea) {
  const lineNumbers = document.createElement("div")
  lineNumbers.className = "line-numbers"
  lineNumbers.style.cssText = `
        position: absolute;
        left: 0;
        top: 0;
        width: 40px;
        height: 100%;
        background-color: #f0f0f0;
        border-right: 1px solid #ddd;
        padding: 10px 5px;
        font-family: Monaco, Menlo, 'Ubuntu Mono', monospace;
        font-size: 14px;
        line-height: 1.5;
        color: #666;
        user-select: none;
        overflow: hidden;
    `

  // Wrap textarea in container
  const container = document.createElement("div")
  container.style.position = "relative"
  textarea.parentNode.insertBefore(container, textarea)
  container.appendChild(lineNumbers)
  container.appendChild(textarea)

  // Adjust textarea padding
  textarea.style.paddingLeft = "50px"

  // Update line numbers
  function updateLineNumbers() {
    const lines = textarea.value.split("\n").length
    let numbers = ""
    for (let i = 1; i <= lines; i++) {
      numbers += i + "\n"
    }
    lineNumbers.textContent = numbers
  }

  textarea.addEventListener("input", updateLineNumbers)
  textarea.addEventListener("scroll", () => {
    lineNumbers.scrollTop = textarea.scrollTop
  })

  updateLineNumbers()
}

// Handle keyboard shortcuts in code editor
function handleCodeEditorKeydown(event) {
  const textarea = event.target

  // Tab key for indentation
  if (event.key === "Tab") {
    event.preventDefault()
    const start = textarea.selectionStart
    const end = textarea.selectionEnd

    if (event.shiftKey) {
      // Shift+Tab: Remove indentation
      const lines = textarea.value.substring(0, start).split("\n")
      const currentLine = lines[lines.length - 1]
      if (currentLine.startsWith("    ")) {
        const newStart = start - 4
        textarea.value = textarea.value.substring(0, newStart) + textarea.value.substring(start)
        textarea.selectionStart = textarea.selectionEnd = newStart
      }
    } else {
      // Tab: Add indentation
      textarea.value = textarea.value.substring(0, start) + "    " + textarea.value.substring(end)
      textarea.selectionStart = textarea.selectionEnd = start + 4
    }
  }

  // Ctrl+Enter: Run code
  if (event.ctrlKey && event.key === "Enter") {
    event.preventDefault()
    runCode()
  }

  // Auto-close brackets and quotes
  const pairs = {
    "(": ")",
    "[": "]",
    "{": "}",
    '"': '"',
    "'": "'",
  }

  if (pairs[event.key]) {
    const start = textarea.selectionStart
    const end = textarea.selectionEnd

    if (start === end) {
      event.preventDefault()
      const closing = pairs[event.key]
      textarea.value = textarea.value.substring(0, start) + event.key + closing + textarea.value.substring(end)
      textarea.selectionStart = textarea.selectionEnd = start + 1
    }
  }
}

// Auto-resize textarea
function autoResizeTextarea(event) {
  const textarea = event.target
  textarea.style.height = "auto"
  textarea.style.height = Math.max(200, textarea.scrollHeight) + "px"
}

// Run code functionality
async function runCode() {
  if (isCodeRunning) return

  const codeEditor = document.getElementById("code-editor")
  const runButton = document.getElementById("run-code-btn")
  const outputDiv = document.getElementById("code-output")

  if (!codeEditor || !outputDiv) return

  const code = codeEditor.value.trim()
  if (!code) {
    showOutput("No code to run", "error")
    return
  }

  // Update UI
  isCodeRunning = true
  runButton.disabled = true
  runButton.innerHTML = '<span class="loading"></span> Running...'
  showOutput("Running code...", "info")

  try {
    const response = await fetch("/student/run_code", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ code: code }),
    })

    const result = await response.json()

    if (result.success) {
      showOutput(result.output || "Code executed successfully (no output)", "success")
    } else {
      showOutput(result.error || "Unknown error occurred", "error")
    }
  } catch (error) {
    showOutput("Network error: " + error.message, "error")
  } finally {
    // Reset UI
    isCodeRunning = false
    runButton.disabled = false
    runButton.innerHTML = '<i class="fas fa-play"></i> Run Code'
  }
}

// Submit code functionality
function submitCode() {
  const codeEditor = document.getElementById("code-editor")
  const submitForm = document.getElementById("submit-form")
  const codeInput = document.getElementById("code-input")

  if (!codeEditor || !submitForm || !codeInput) return

  const code = codeEditor.value.trim()
  if (!code) {
    alert("Please write some code before submitting")
    return
  }

  if (confirm("Are you sure you want to submit this code?")) {
    codeInput.value = code
    submitForm.submit()
  }
}

// Show output in the output div
function showOutput(message, type = "info") {
  const outputDiv = document.getElementById("code-output")
  if (!outputDiv) return

  outputDiv.textContent = message
  outputDiv.className = `code-output ${type}`

  // Add fade-in animation
  outputDiv.style.opacity = "0"
  setTimeout(() => {
    outputDiv.style.opacity = "1"
  }, 50)
}

// Initialize tooltips
function initializeTooltips() {
  const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
  tooltipTriggerList.map((tooltipTriggerEl) => new bootstrap.Tooltip(tooltipTriggerEl))
}

// Initialize confirmation dialogs
function initializeConfirmDialogs() {
  const deleteButtons = document.querySelectorAll(".btn-delete")
  deleteButtons.forEach((button) => {
    button.addEventListener("click", (event) => {
      if (!confirm("Are you sure you want to delete this item?")) {
        event.preventDefault()
      }
    })
  })
}

// Initialize form validation
function initializeFormValidation() {
  const forms = document.querySelectorAll(".needs-validation")
  forms.forEach((form) => {
    form.addEventListener("submit", (event) => {
      if (!form.checkValidity()) {
        event.preventDefault()
        event.stopPropagation()
      }
      form.classList.add("was-validated")
    })
  })
}

// Utility functions
function formatTimestamp(timestamp) {
  const date = new Date(timestamp)
  return date.toLocaleString()
}

function getSimilarityClass(score) {
  if (score >= 70) return "similarity-high"
  if (score >= 30) return "similarity-medium"
  return "similarity-low"
}

function getSimilarityBadgeClass(score) {
  if (score >= 70) return "badge bg-danger"
  if (score >= 30) return "badge bg-warning"
  return "badge bg-success"
}

// Code comparison functionality
function highlightCodeDifferences() {
  const codeBlocks = document.querySelectorAll(".code-comparison .code-block")
  codeBlocks.forEach((block) => {
    const lines = block.querySelectorAll(".code-line")
    lines.forEach((line) => {
      const type = line.dataset.type
      if (type) {
        line.classList.add(type)
      }
    })
  })
}

// Search functionality
function initializeSearch() {
  const searchInput = document.getElementById("search-input")
  if (searchInput) {
    searchInput.addEventListener("input", function () {
      const query = this.value.toLowerCase()
      const rows = document.querySelectorAll(".searchable-row")

      rows.forEach((row) => {
        const text = row.textContent.toLowerCase()
        if (text.includes(query)) {
          row.style.display = ""
        } else {
          row.style.display = "none"
        }
      })
    })
  }
}

// Statistics animation
function animateStatistics() {
  const statNumbers = document.querySelectorAll(".stat-number")
  statNumbers.forEach((stat) => {
    const target = Number.parseInt(stat.textContent)
    let current = 0
    const increment = target / 50

    const timer = setInterval(() => {
      current += increment
      if (current >= target) {
        current = target
        clearInterval(timer)
      }
      stat.textContent = Math.floor(current)
    }, 20)
  })
}

// Initialize additional features when page loads
document.addEventListener("DOMContentLoaded", () => {
  highlightCodeDifferences()
  initializeSearch()

  // Animate statistics on admin dashboard
  if (document.querySelector(".stat-card")) {
    setTimeout(animateStatistics, 500)
  }
})

// Export functions for use in other scripts
window.CodePlatform = {
  runCode,
  submitCode,
  showOutput,
  formatTimestamp,
  getSimilarityClass,
  getSimilarityBadgeClass,
}
