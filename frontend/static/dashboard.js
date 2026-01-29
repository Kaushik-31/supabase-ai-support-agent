/**
 * Dashboard Charts - Supabase Support Agent Analytics
 * Uses Chart.js v4 for rendering charts
 */

// Chart color palette
const COLORS = {
    primary: '#2563eb',
    primaryLight: 'rgba(37, 99, 235, 0.1)',
    success: '#22c55e',
    warning: '#f59e0b',
    danger: '#ef4444',
    purple: '#8b5cf6',
    cyan: '#06b6d4',
    pink: '#ec4899',
    gray: '#6b7280'
};

const CHART_COLORS = [
    COLORS.primary,
    COLORS.success,
    COLORS.warning,
    COLORS.danger,
    COLORS.purple,
    COLORS.cyan,
    COLORS.pink
];

/**
 * Initialize the queries per day line chart
 * @param {Object} data - {labels: string[], data: number[]}
 */
function initQueriesChart(data) {
    const ctx = document.getElementById('queriesChart');
    if (!ctx) return null;

    return new Chart(ctx.getContext('2d'), {
        type: 'line',
        data: {
            labels: data.labels || [],
            datasets: [{
                label: 'Queries',
                data: data.data || [],
                borderColor: COLORS.primary,
                backgroundColor: COLORS.primaryLight,
                fill: true,
                tension: 0.4,
                pointBackgroundColor: COLORS.primary,
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointRadius: 4,
                pointHoverRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                intersect: false,
                mode: 'index'
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    padding: 12,
                    titleFont: {
                        size: 14
                    },
                    bodyFont: {
                        size: 13
                    },
                    cornerRadius: 8
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1,
                        font: {
                            size: 12
                        }
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                },
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        font: {
                            size: 12
                        }
                    }
                }
            }
        }
    });
}

/**
 * Initialize the intent distribution pie chart
 * @param {Object} data - {labels: string[], data: number[]}
 */
function initIntentsChart(data) {
    const ctx = document.getElementById('intentsChart');
    if (!ctx) return null;

    return new Chart(ctx.getContext('2d'), {
        type: 'pie',
        data: {
            labels: data.labels || [],
            datasets: [{
                data: data.data || [],
                backgroundColor: CHART_COLORS,
                borderWidth: 2,
                borderColor: '#fff',
                hoverOffset: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        padding: 16,
                        usePointStyle: true,
                        pointStyle: 'circle',
                        font: {
                            size: 12
                        }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    padding: 12,
                    cornerRadius: 8,
                    callbacks: {
                        label: function(context) {
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((context.raw / total) * 100).toFixed(1);
                            return `${context.label}: ${context.raw} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

/**
 * Initialize the top questions horizontal bar chart
 * @param {Array} data - [{question: string, count: number, intent: string}]
 */
function initQuestionsChart(data) {
    const ctx = document.getElementById('questionsChart');
    if (!ctx) return null;

    const questions = data || [];
    const labels = questions.map(q =>
        q.question.length > 40 ? q.question.substring(0, 40) + '...' : q.question
    );
    const counts = questions.map(q => q.count);

    return new Chart(ctx.getContext('2d'), {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Count',
                data: counts,
                backgroundColor: COLORS.primaryLight.replace('0.1', '0.8'),
                borderColor: COLORS.primary,
                borderWidth: 1,
                borderRadius: 4,
                hoverBackgroundColor: COLORS.primary
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    padding: 12,
                    cornerRadius: 8,
                    callbacks: {
                        title: function(context) {
                            // Show full question in tooltip
                            const index = context[0].dataIndex;
                            return questions[index]?.question || '';
                        },
                        label: function(context) {
                            return `Asked ${context.raw} times`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1,
                        font: {
                            size: 12
                        }
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                },
                y: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        font: {
                            size: 11
                        }
                    }
                }
            }
        }
    });
}

/**
 * Initialize all dashboard charts
 * @param {Object} dashboardData - Data object from Flask template
 */
function initDashboard(dashboardData) {
    const charts = {};

    // Initialize queries chart
    if (dashboardData.queries_by_date) {
        charts.queries = initQueriesChart(dashboardData.queries_by_date);
    }

    // Initialize intents chart
    if (dashboardData.top_intents) {
        charts.intents = initIntentsChart(dashboardData.top_intents);
    }

    // Initialize questions chart
    if (dashboardData.top_questions) {
        charts.questions = initQuestionsChart(dashboardData.top_questions);
    }

    return charts;
}

// Export for use in templates
window.DashboardCharts = {
    init: initDashboard,
    initQueriesChart,
    initIntentsChart,
    initQuestionsChart,
    COLORS,
    CHART_COLORS
};
