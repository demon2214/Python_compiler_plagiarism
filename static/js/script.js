document.addEventListener('DOMContentLoaded', function() {
    // Timer functionality (30 minutes)
    let timeLeft = 30 * 60; // 30 minutes in seconds
    const timerElement = document.getElementById('timer');
    
    const updateTimer = () => {
        const minutes = Math.floor(timeLeft / 60);
        const seconds = timeLeft % 60;
        timerElement.textContent = `Time remaining: ${minutes}:${seconds.toString().padStart(2, '0')}`;
        
        if (timeLeft <= 0) {
            clearInterval(timer);
            autoSubmit();
        }
        timeLeft--;
    };
    
    const timer = setInterval(updateTimer, 1000);
    updateTimer(); // Initial call
    
    // Run code button
    const runBtn = document.getElementById('run-btn');
    const submitBtn = document.getElementById('submit-btn');
    const editor = document.getElementById('code-editor');
    const outputArea = document.getElementById('output-area');
    
    runBtn.addEventListener('click', async () => {
        const code = editor.value;
        
        try {
            const response = await fetch('/run', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ code })
            });
            
            const result = await response.json();
            
            if (result.status === 'success') {
                // Format test results
                let outputHTML = '<div class="test-results">';
                
                result.output.forEach((test, index) => {
                    if (test.error) {
                        outputHTML += `
                            <div class="test-case test-error">
                                <strong>Test Case #${index + 1}:</strong> Input=${test.input}
                                <div class="error">${test.error}</div>
                            </div>
                        `;
                    } else {
                        outputHTML += `
                            <div class="test-case ${test.passed ? 'test-passed' : 'test-failed'}">
                                <strong>Test Case #${index + 1}:</strong> 
                                Input=${test.input}, 
                                Expected=${test.expected}, 
                                Actual=${test.actual}
                                <div>${test.passed ? '✓ Passed' : '✗ Failed'}</div>
                            </div>
                        `;
                    }
                });
                
                outputHTML += '</div>';
                outputArea.innerHTML = outputHTML;
            } else {
                outputArea.innerHTML = `<div class="error">${result.output}</div>`;
            }
        } catch (error) {
            outputArea.innerHTML = `<div class="error">Error: ${error.message}</div>`;
        }
    });
    
    // Submit code button
    submitBtn.addEventListener('click', submitCode);
    
    // Auto-submit when time runs out
    function autoSubmit() {
        alert('Time is up! Your code will be submitted automatically.');
        submitCode();
    }
    
    async function submitCode() {
        const code = editor.value;
        
        try {
            const response = await fetch('/submit', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    code,
                    question_id: 1  // Default to question 1 for this demo
                })
            });
            
            const result = await response.json();
            
            if (result.status === 'success') {
                alert('Code submitted successfully!');
                // Disable editor and buttons
                editor.readOnly = true;
                runBtn.disabled = true;
                submitBtn.disabled = true;
                clearInterval(timer);
                
                // Show final output
                if (result.output && result.output.status === 'success') {
                    let outputHTML = '<div class="test-results">';
                    result.output.output.forEach((test, index) => {
                        if (test.error) {
                            outputHTML += `
                                <div class="test-case test-error">
                                    <strong>Test Case #${index + 1}:</strong> Input=${test.input}
                                    <div class="error">${test.error}</div>
                                </div>
                            `;
                        } else {
                            outputHTML += `
                                <div class="test-case ${test.passed ? 'test-passed' : 'test-failed'}">
                                    <strong>Test Case #${index + 1}:</strong> 
                                    Input=${test.input}, 
                                    Expected=${test.expected}, 
                                    Actual=${test.actual}
                                    <div>${test.passed ? '✓ Passed' : '✗ Failed'}</div>
                                </div>
                            `;
                        }
                    });
                    outputHTML += '</div>';
                    outputArea.innerHTML = outputHTML;
                }
            } else {
                alert(`Submission failed: ${result.message || 'Unknown error'}`);
            }
        } catch (error) {
            alert(`Error submitting code: ${error.message}`);
        }
    }
});