"use strict";

// Doktor Dashboard Grafikleri
class DoctorDashboardCharts {
    
    constructor() {
        this.initWeeklyAppointmentsChart();
        this.initPatientDemographicsChart();
        this.initTreatmentTypesChart();
    }
    
    // Haftalık Randevu Grafiği
    initWeeklyAppointmentsChart() {
        const element = document.getElementById('weekly_appointments_chart');
        if (!element) {
            return;
        }
        
        const weeklyData = JSON.parse(element.getAttribute('data-appointments'));
        
        const options = {
            series: [{
                name: 'Randevular',
                data: weeklyData.counts
            }],
            chart: {
                fontFamily: 'inherit',
                type: 'area',
                height: 350,
                toolbar: {
                    show: false
                }
            },
            plotOptions: {},
            legend: {
                show: false
            },
            dataLabels: {
                enabled: false
            },
            fill: {
                type: 'gradient',
                gradient: {
                    shadeIntensity: 1,
                    opacityFrom: 0.4,
                    opacityTo: 0.2,
                    stops: [0, 90, 100]
                }
            },
            stroke: {
                curve: 'smooth',
                show: true,
                width: 3,
                colors: ['#009ef7']
            },
            xaxis: {
                categories: weeklyData.days,
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
                        return val + " randevu"
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
            }
        };
        
        const chart = new ApexCharts(element, options);
        chart.render();
    }
    
    // Hasta Demografikleri Pasta Grafiği 
    initPatientDemographicsChart() {
        const element = document.getElementById('patient_demographics_chart');
        if (!element) {
            return;
        }
        
        const demographicsData = JSON.parse(element.getAttribute('data-demographics'));
        
        const options = {
            series: demographicsData.counts,
            chart: {
                fontFamily: 'inherit',
                type: 'pie',
                height: 350,
                toolbar: {
                    show: false
                }
            },
            labels: demographicsData.labels,
            dataLabels: {
                enabled: true,
                formatter: function (val, opt) {
                    return opt.w.globals.series[opt.seriesIndex] + ' (%' + val.toFixed(1) + ')';
                },
                style: {
                    fontSize: '12px',
                    colors: ['#F1F1F1']
                }
            },
            colors: ['#3699FF', '#6610F2', '#E4E6EF', '#FFA800', '#F64E60'],
            stroke: {
                width: 0
            },
            fill: {
                opacity: 1
            },
            legend: {
                position: 'bottom',
                fontSize: '14px',
                fontWeight: 600,
                markers: {
                    strokeColor: ['#3699FF', '#6610F2', '#E4E6EF', '#FFA800', '#F64E60'],
                    radius: 12
                },
                itemMargin: {
                    horizontal: 12,
                    vertical: 5
                }
            },
            tooltip: {
                style: {
                    fontSize: '12px'
                }
            }
        };
        
        const chart = new ApexCharts(element, options);
        chart.render();
    }
    
    // Tedavi Türleri Çubuk Grafiği
    initTreatmentTypesChart() {
        const element = document.getElementById('treatment_types_chart');
        if (!element) {
            return;
        }
        
        const treatmentData = JSON.parse(element.getAttribute('data-treatments'));
        
        const options = {
            series: [{
                name: 'Tedaviler',
                data: treatmentData.counts
            }],
            chart: {
                fontFamily: 'inherit',
                type: 'bar',
                height: 350,
                toolbar: {
                    show: false
                }
            },
            plotOptions: {
                bar: {
                    horizontal: false,
                    columnWidth: '60%',
                    borderRadius: 5
                },
            },
            dataLabels: {
                enabled: false
            },
            stroke: {
                show: true,
                width: 2,
                colors: ['transparent']
            },
            xaxis: {
                categories: treatmentData.types,
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
            fill: {
                opacity: 1
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
                        return val + " vaka"
                    }
                }
            },
            colors: ['#50CD89'],
            grid: {
                borderColor: '#F1F1F1',
                strokeDashArray: 4,
                yaxis: {
                    lines: {
                        show: true
                    }
                }
            }
        };
        
        const chart = new ApexCharts(element, options);
        chart.render();
    }
}

// Sayfa yüklendiğinde grafikleri başlat
document.addEventListener('DOMContentLoaded', function() {
    new DoctorDashboardCharts();
});
