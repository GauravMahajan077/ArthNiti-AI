document.addEventListener('DOMContentLoaded', () => {

    // --- THEME TOGGLE LOGIC ---
    const themeToggle = document.getElementById('theme-toggle');
    const htmlElement = document.documentElement;

    function setTheme(theme) {
        htmlElement.setAttribute('data-theme', theme);
        if (theme === 'dark') {
            themeToggle.textContent = '☀️';
        } else {
            themeToggle.textContent = '🌙';
        }
    }

    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)');
    setTheme(prefersDark.matches ? 'dark' : 'light');

    themeToggle.addEventListener('click', () => {
        const currentTheme = htmlElement.getAttribute('data-theme');
        setTheme(currentTheme === 'dark' ? 'light' : 'dark');
    });

    // --- Get all DOM elements ---
    const creditForm = document.getElementById('creditForm');
    const inputSection = document.getElementById('inputSection');
    const loadingSection = document.getElementById('loadingSection');
    const scoreSection = document.getElementById('scoreSection');
    const agents = {
        agent1: document.getElementById('agent1'),
        agent2: document.getElementById('agent2'),
        agent3: document.getElementById('agent3'),
        agent4: document.getElementById('agent4'),
    };
    const scoreNumber = document.getElementById('scoreNumber');
    const scoreRating = document.getElementById('scoreRating');
    const scoreTrend = document.getElementById('scoreTrend');
    const breakdown = {
        payment: {
            progress: document.getElementById('paymentProgress'),
            value: document.getElementById('paymentValue'),
        },
        stability: {
            progress: document.getElementById('stabilityProgress'),
            value: document.getElementById('stabilityValue'),
        },
        utilization: {
            progress: document.getElementById('utilizationProgress'),
            value: document.getElementById('utilizationValue'),
        },
        richness: {
            progress: document.getElementById('richnessProgress'),
            value: document.getElementById('richnessValue'),
        },
    };
    const insightsList = document.getElementById('insightsList');
    const recommendationsList = document.getElementById('recommendationsList');
    const requestLoanBtn = document.getElementById('requestLoanBtn');
    const loanSuggestionCard = document.getElementById('loanSuggestionCard');
    const loanDetails = document.getElementById('loanDetails');

    // --- Global Variables ---
    let currentUserData = null;
    let currentScore = null;

    // --- Event Listeners ---
    creditForm.addEventListener('submit', handleSubmit);
    requestLoanBtn.addEventListener('click', handleLoanRequest);

    async function handleSubmit(e) {
        e.preventDefault();
        currentUserData = {
            monthlyIncome: document.getElementById('monthlyIncome').value,
            rentAmount: document.getElementById('rentAmount').value,
            rentHistory: document.getElementById('rentHistory').value,
            avgBalance: document.getElementById('avgBalance').value,
            savingsRate: document.getElementById('savingsRate').value,
            overdrafts: document.getElementById('overdrafts').value,
            employmentStability: document.getElementById('employmentStability').value,
            utilityHistory: document.getElementById('utilityHistory').value,
        };

        inputSection.style.display = 'none';
        scoreSection.style.display = 'none';
        loanSuggestionCard.style.display = 'none';
        requestLoanBtn.style.display = 'none';
        loadingSection.style.display = 'block';
        window.scrollTo(0, 0);
        animateLoadingScreen();

        try {
            const response = await fetch('http://127.0.0.1:5000/api/score', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(currentUserData),
            });

            if (!response.ok) {
                let errorMsg = `HTTP error! status: ${response.status}`;
                try {
                    const errorData = await response.json();
                    errorMsg = errorData.error || errorMsg;
                } catch (jsonError) { }
                throw new Error(errorMsg);
            }

            const data = await response.json();

            if (data.error || !data.score || !data.ai_analysis) {
                console.error("Backend returned an error structure:", data);
                throw new Error(data.error || "Incomplete data received from backend.");
            }

            currentScore = data.score.total_score;
            populateScoreData(data);

            loadingSection.style.display = 'none';
            scoreSection.style.display = 'block';
            requestLoanBtn.style.display = 'block';

        } catch (error) {
            console.error('Error during score calculation:', error);
            loadingSection.style.display = 'none';
            scoreSection.style.display = 'none';
            alert(`Could not calculate score: ${error.message}`);
            resetApp();
        }
    }

    function animateLoadingScreen() {
        const agentElems = [agents.agent1, agents.agent2, agents.agent3, agents.agent4];
        let currentAgent = 0;

        agentElems.forEach(agent => {
            const dot = agent.querySelector('.agent-dot');
            const state = agent.querySelector('.agent-state');
            dot.classList.remove('active');
            state.textContent = 'WAITING...';
            state.classList.remove('active');
        });

        const firstDot = agents.agent1.querySelector('.agent-dot');
        const firstState = agents.agent1.querySelector('.agent-state');
        firstDot.classList.add('active');
        firstState.textContent = 'ANALYZING...';
        firstState.classList.add('active');

        const interval = setInterval(() => {
            currentAgent++;
            if (currentAgent < agentElems.length) {
                const prevDot = agentElems[currentAgent - 1].querySelector('.agent-dot');
                const prevState = agentElems[currentAgent - 1].querySelector('.agent-state');
                prevDot.classList.remove('active');
                prevState.textContent = 'DONE';

                const currentDot = agentElems[currentAgent].querySelector('.agent-dot');
                const currentState = agentElems[currentAgent].querySelector('.agent-state');
                currentDot.classList.add('active');
                currentState.textContent = 'ANALYZING...';
                currentState.classList.add('active');

            } else {
                clearInterval(interval);
                const lastDot = agentElems[currentAgent - 1].querySelector('.agent-dot');
                const lastState = agentElems[currentAgent - 1].querySelector('.agent-state');
                lastDot.classList.remove('active');
                lastState.textContent = 'DONE';
            }
        }, 1500);
    }

    function populateScoreData(data) {
        scoreNumber.textContent = data.score.total_score;
        scoreRating.textContent = data.score.rating;
        scoreTrend.textContent = data.score.trend;

        const breakdownMap = {
            payment_history: breakdown.payment,
            financial_stability: breakdown.stability,
            credit_utilization: breakdown.utilization,
            data_richness: breakdown.richness,
        };
        
        for (const [key, value] of Object.entries(data.score.breakdown)) {
            const elem = breakdownMap[key];
            if (elem) {
                const score = value.score;
                elem.progress.style.width = `${score}%`;
                elem.value.textContent = `${score}/100`;
            }
        }

        insightsList.innerHTML = '';
        if (data.ai_analysis && Array.isArray(data.ai_analysis.insights) && data.ai_analysis.insights.length > 0) {
            data.ai_analysis.insights.forEach(insight => {
                const item = document.createElement('div');
                item.className = 'insight-item';
                item.textContent = insight;
                insightsList.appendChild(item);
            });
        } else {
            console.warn("Insights data missing:", data.ai_analysis);
            insightsList.innerHTML = '<div class="insight-item">Could not load AI insights.</div>';
        }

        recommendationsList.innerHTML = '';
        if (data.ai_analysis && Array.isArray(data.ai_analysis.recommendations) && data.ai_analysis.recommendations.length > 0) {
            data.ai_analysis.recommendations.forEach(rec => {
                const priorityClass = rec.priority.toLowerCase();
                const item = document.createElement('div');
                item.className = 'recommendation-item';
                item.innerHTML = `
                    <div class="rec-header">
                        <span class="rec-title">${rec.title}</span>
                        <span class="rec-priority ${priorityClass}">${rec.priority}</span>
                    </div>
                    <div class="rec-details">
                        <div class="rec-detail">
                            <strong>IMPACT</strong>
                            <span>${rec.impact}</span>
                        </div>
                        <div class="rec-detail">
                            <strong>DIFFICULTY</strong>
                            <span>${rec.difficulty}</span>
                        </div>
                    </div>`;
                recommendationsList.appendChild(item);
            });
        } else {
            console.warn("Recommendations data missing:", data.ai_analysis);
            recommendationsList.innerHTML = '<div class="recommendation-item">Could not load AI recommendations.</div>';
        }

        // --- FEATURE BUTTONS INTEGRATION ---
        
        // 1. HEALTH MONITOR BUTTON
        const healthBtn = document.getElementById('healthMonitorBtn');
        if (healthBtn) {
            healthBtn.style.display = 'block';
            const newHealthBtn = healthBtn.cloneNode(true);
            healthBtn.parentNode.replaceChild(newHealthBtn, healthBtn);
            newHealthBtn.addEventListener('click', () => {
                sessionStorage.setItem('currentScore', data.score.total_score);
                sessionStorage.setItem('userData', JSON.stringify(currentUserData));
                sessionStorage.setItem('scoreBreakdown', JSON.stringify(data.score.breakdown));
                window.location.href = 'health-monitor.html';
            });
        }

        // 2. BILL REMINDER BUTTON
        const billBtn = document.getElementById('billReminderBtn');
        if (billBtn) {
            billBtn.style.display = 'block';
            const newBillBtn = billBtn.cloneNode(true);
            billBtn.parentNode.replaceChild(newBillBtn, billBtn);
            newBillBtn.addEventListener('click', () => {
                sessionStorage.setItem('currentScore', data.score.total_score);
                sessionStorage.setItem('userData', JSON.stringify(currentUserData));
                window.location.href = 'bill-reminder.html';
            });
        }

        // 3. CREDITY GAME BUTTON
        const gameBtn = document.getElementById('creditClashBtn');
        if (gameBtn) {
            gameBtn.style.display = 'block';
            const newGameBtn = gameBtn.cloneNode(true);
            gameBtn.parentNode.replaceChild(newGameBtn, gameBtn);
            newGameBtn.addEventListener('click', () => {
                sessionStorage.setItem('realScore', data.score.total_score);
                sessionStorage.setItem('userData', JSON.stringify(currentUserData));
                window.location.href = 'credit-clash.html';
            });
        }
    }

    async function handleLoanRequest() {
        if (!currentScore || !currentUserData) return;

        loanSuggestionCard.style.display = 'block';
        loanDetails.innerHTML = '<p class="loading-text">Asking ArthNiti AI for a loan suggestion...</p>';
        requestLoanBtn.disabled = true;
        requestLoanBtn.textContent = "Processing...";
        loanSuggestionCard.scrollIntoView({ behavior: 'smooth', block: 'center' });

        try {
            const loanData = {
                ...currentUserData,
                score: currentScore
            };

            const response = await fetch('http://127.0.0.1:5000/api/suggest_loan', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(loanData),
            });

            if (!response.ok) {
                let errorMsg = `HTTP error! status: ${response.status}`;
                try {
                    const errorData = await response.json();
                    errorMsg = errorData.error || errorMsg;
                } catch (jsonError) { }
                throw new Error(errorMsg);
            }

            const data = await response.json();

            if (data.error) {
                console.error("Backend returned an error:", data);
                throw new Error(data.error || "Failed to get loan suggestion.");
            }

            // Assuming the backend returns loan suggestion data like { amount, interest_rate, term, eligibility, reason }
            const { amount, interest_rate, term, eligibility, reason } = data;

            loanDetails.innerHTML = `
                <div class="loan-suggestion">
                    <h4>Loan Eligibility: ${eligibility ? '✅ Approved' : '❌ Not Eligible'}</h4>
                    ${eligibility ? `
                        <div class="loan-details-grid">
                            <div class="loan-detail">
                                <strong>Amount:</strong> ₹${amount.toLocaleString()}
                            </div>
                            <div class="loan-detail">
                                <strong>Interest Rate:</strong> ${interest_rate}%
                            </div>
                            <div class="loan-detail">
                                <strong>Term:</strong> ${term} months
                            </div>
                        </div>
                        <p class="loan-reason"><strong>Why this loan?</strong> ${reason}</p>
                        <button class="btn btn-secondary" onclick="applyForLoan()">Apply Now</button>
                    ` : `
                        <p class="loan-reason"><strong>Reason:</strong> ${reason}</p>
                        <p>Improve your score to unlock better loan options!</p>
                    `}
                </div>
            `;

            requestLoanBtn.disabled = false;
            requestLoanBtn.textContent = "Ask Again";

        } catch (error) {
            console.error('Error during loan suggestion:', error);
            loanDetails.innerHTML = `<p class="error-text">Could not fetch loan suggestion: ${error.message}</p>`;
            requestLoanBtn.disabled = false;
            requestLoanBtn.textContent = "Need a Loan? Ask ArthNiti AI";
        }
    }
    
    

    // Utility functions
    function resetApp() {
        inputSection.style.display = 'block';
        scoreSection.style.display = 'none';
        loadingSection.style.display = 'none';
        loanSuggestionCard.style.display = 'none';
        requestLoanBtn.style.display = 'none';
        creditForm.reset();
        scoreNumber.textContent = '---';
        scoreRating.textContent = 'CALCULATING...';
        insightsList.innerHTML = '<div class="insight-item loading"><span class="loading-text">AI AGENTS ANALYZING...</span></div>';
        recommendationsList.innerHTML = '<div class="recommendation-item loading"><span class="loading-text">GENERATING ACTION PLAN...</span></div>';
        Object.values(breakdown).forEach(({ progress, value }) => {
            progress.style.width = '0%';
            value.textContent = '0/100';
        });
        // Hide feature buttons
        document.getElementById('healthMonitorBtn').style.display = 'none';
        document.getElementById('billReminderBtn').style.display = 'none';
        document.getElementById('creditClashBtn').style.display = 'none';
        window.scrollTo(0, 0);
    }

    function useSampleData() {
        document.getElementById('monthlyIncome').value = '4500';
        document.getElementById('rentAmount').value = '1500';
        document.getElementById('rentHistory').value = 'good';
        document.getElementById('avgBalance').value = '3500';
        document.getElementById('savingsRate').value = '0.15';
        document.getElementById('overdrafts').value = '1';
        document.getElementById('employmentStability').value = 'medium';
        document.getElementById('utilityHistory').value = 'good';
        // Trigger submit after a short delay to simulate user interaction
        setTimeout(() => creditForm.dispatchEvent(new Event('submit')), 100);
    }

    // Global functions for onclick in HTML
    window.resetApp = resetApp;
    window.useSampleData = useSampleData;
    window.applyForLoan = () => {
        alert('Redirecting to loan application... (Feature coming soon!)');
        // In a real app, this would navigate to an application form
    };
});