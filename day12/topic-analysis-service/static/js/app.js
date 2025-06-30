class TopicAnalysisApp {
    constructor() {
        this.form = document.getElementById('analysisForm');
        this.resultsCard = document.getElementById('resultsCard');
        this.resultsContainer = document.getElementById('analysisResults');
        this.confidenceSlider = document.getElementById('confidence');
        this.confidenceValue = document.getElementById('confidenceValue');
        this.analyzeBtn = this.form.querySelector('button[type="submit"]');
        this.buttonText = document.getElementById('buttonText');
        this.loadingSpinner = document.getElementById('loadingSpinner');
        
        this.initializeEventListeners();
    }
    
    initializeEventListeners() {
        this.form.addEventListener('submit', (e) => this.handleSubmit(e));
        this.confidenceSlider.addEventListener('input', (e) => {
            this.confidenceValue.textContent = e.target.value;
        });
    }
    
    async handleSubmit(event) {
        event.preventDefault();
        
        const formData = this.getFormData();
        if (!this.validateForm(formData)) {
            return;
        }
        
        this.setLoadingState(true);
        
        try {
            const response = await this.analyzeContent(formData);
            this.displayResults(response);
        } catch (error) {
            this.displayError(error.message);
        } finally {
            this.setLoadingState(false);
        }
    }
    
    getFormData() {
        return {
            content: document.getElementById('content').value.trim(),
            options: {
                max_topics: parseInt(document.getElementById('maxTopics').value),
                confidence_threshold: parseFloat(document.getElementById('confidence').value),
                include_subtopics: document.getElementById('includeSubtopics').checked,
                extract_concepts: document.getElementById('extractConcepts').checked
            }
        };
    }
    
    validateForm(formData) {
        if (!formData.content) {
            this.displayError('Please enter content to analyze.');
            return false;
        }
        
        if (formData.content.length < 10) {
            this.displayError('Content must be at least 10 characters long.');
            return false;
        }
        
        return true;
    }
    
    async analyzeContent(formData) {
        const response = await fetch('/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Analysis failed');
        }
        
        return await response.json();
    }
    
    setLoadingState(isLoading) {
        this.analyzeBtn.disabled = isLoading;
        this.buttonText.style.display = isLoading ? 'none' : 'inline';
        this.loadingSpinner.style.display = isLoading ? 'block' : 'none';
    }
    
    displayResults(response) {
        this.resultsCard.style.display = 'block';
        
        const html = `
            <div class="results-summary">
                <h3>Analysis Summary</h3>
                <p><strong>Summary:</strong> ${response.summary}</p>
                <p><strong>Word Count:</strong> ${response.word_count}</p>
                <p><strong>Processing Time:</strong> ${response.processing_time.toFixed(3)}s</p>
                <p><strong>Cache Hit:</strong> ${response.cache_hit ? 'Yes' : 'No'}</p>
                <p><strong>Topics Found:</strong> ${response.topics.length}</p>
            </div>
            
            <div class="topics-grid">
                ${response.topics.map(topic => this.createTopicCard(topic)).join('')}
            </div>
        `;
        
        this.resultsContainer.innerHTML = html;
        this.resultsCard.scrollIntoView({ behavior: 'smooth' });
    }
    
    createTopicCard(topic) {
        const confidenceClass = topic.confidence >= 0.8 ? 'high' : 
                               topic.confidence >= 0.6 ? 'medium' : 'low';
        
        return `
            <div class="topic-card">
                <div class="topic-header">
                    <span class="topic-name">${topic.name}</span>
                    <span class="confidence-badge ${confidenceClass}">
                        ${(topic.confidence * 100).toFixed(0)}%
                    </span>
                </div>
                <div class="topic-category">Category: ${topic.category}</div>
                
                ${topic.subtopics.length > 0 ? `
                    <div class="topic-section">
                        <strong>Subtopics:</strong>
                        <div class="topic-tags">
                            ${topic.subtopics.map(subtopic => `<span class="tag">${subtopic}</span>`).join('')}
                        </div>
                    </div>
                ` : ''}
                
                ${topic.concepts.length > 0 ? `
                    <div class="topic-section">
                        <strong>Concepts:</strong>
                        <div class="topic-tags">
                            ${topic.concepts.map(concept => `<span class="tag">${concept}</span>`).join('')}
                        </div>
                    </div>
                ` : ''}
                
                ${topic.keywords.length > 0 ? `
                    <div class="topic-section">
                        <strong>Keywords:</strong>
                        <div class="topic-tags">
                            ${topic.keywords.map(keyword => `<span class="tag">${keyword}</span>`).join('')}
                        </div>
                    </div>
                ` : ''}
            </div>
        `;
    }
    
    displayError(message) {
        this.resultsCard.style.display = 'block';
        this.resultsContainer.innerHTML = `
            <div class="error-message">
                <h3>Error</h3>
                <p>${message}</p>
            </div>
        `;
        this.resultsCard.scrollIntoView({ behavior: 'smooth' });
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new TopicAnalysisApp();
});
