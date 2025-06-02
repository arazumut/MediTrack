"use strict";

// Laboratuvar Test Sonuçları Grafiği
class LabResultsChart {
    
    constructor() {
        this.initLabResultsChart();
    }
    
    // Lab Sonuçları Trend Grafiği
    initLabResultsChart() {
        const element = document.getElementById('lab_results_chart');
        if (!element) {
            return;
        }
        
        const resultsData = JSON.parse(element.getAttribute('data-results'));
        
        const options = {
            series: [{
                name: resultsData.unit,
                data: resultsData.values
            }],
            chart: {
                fontFamily: 'inherit',
                type: 'line',
                height: 350,
                toolbar: {
                    show: false
                }
            },
            plotOptions: {},
            legend: {
                show: true
            },
            dataLabels: {
                enabled: false
            },
            stroke: {
                curve: 'smooth',
                show: true,
                width: 3,
                colors: ['#009ef7']
            },
            xaxis: {
                categories: resultsData.dates,
                axisBorder: {
                    show: false,
                },
                axisTicks: {
                    show: false
                },
                labels: {
                    style: {
                        colors: '#A1A5B7',
                        fontSize: '12px'
                    }
                },
                crosshairs: {
                    position: 'front',
                    stroke: {
                        color: '#009ef7',
                        width: 1,
                        dashArray: 3
                    }
                },
                tooltip: {
                    enabled: true,
                    formatter: undefined,
                    offsetY: 0,
                    style: {
                        fontSize: '12px'
                    }
                }
            },
            yaxis: {
                labels: {
                    style: {
                        colors: '#A1A5B7',
                        fontSize: '12px'
                    }
                }
            },
            states: {
                normal: {
                    filter: {
                        type: 'none',
                        value: 0
                    }
                },
                hover: {
                    filter: {
                        type: 'none',
                        value: 0
                    }
                },
                active: {
                    allowMultipleDataPointsSelection: false,
                    filter: {
                        type: 'none',
                        value: 0
                    }
                }
            },
            tooltip: {
                style: {
                    fontSize: '12px'
                },
                y: {
                    formatter: function (val) {
                        return val + " " + resultsData.unit
                    }
                }
            },
            colors: ['#009ef7'],
            grid: {
                borderColor: '#F1F1F1',
                strokeDashArray: 4,
                yaxis: {
                    lines: {
                        show: true
                    }
                }
            },
            markers: {
                strokeColor: '#009ef7',
                strokeWidth: 3
            },
            annotations: {
                yaxis: [
                    {
                        y: resultsData.reference_range.min,
                        y2: resultsData.reference_range.max,
                        borderColor: '#00E396',
                        fillColor: '#00E396',
                        opacity: 0.1,
                        label: {
                            borderColor: '#00E396',
                            style: {
                                color: '#fff',
                                background: '#00E396'
                            },
                            text: 'Normal Aralık'
                        }
                    }
                ]
            }
        };
        
        const chart = new ApexCharts(element, options);
        chart.render();
    }
}

// Sayfa yüklendiğinde grafikleri başlat
document.addEventListener('DOMContentLoaded', function() {
    new LabResultsChart();
});
