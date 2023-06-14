/******/ ( async () => { // webpackBootstrap
        var __webpack_exports__ = {};
        /*!***********************************************!*\
        !*** ./src/js/pages/components-apexcharts.js ***!
        \***********************************************/
    
        const device_id = document.querySelector('#device_id').value;
        
        const fetchData = async () => {
            const response = await fetch(`/chart/four_chart/${device_id}/get_data`);
            const data = await response.json();
            return  data;
        }   

        let sensors = document.querySelectorAll(`div[id^='lastval']`);
    
        var onLoad =  async function onLoad() {

            const data = await fetchData();
            let parsedData = Array();

            data.forEach(e => {
                parsedData.push(decoder(JSON.parse(e.value)));
            })
            parsedData = parsedData.reverse();

            let x = parsedData.map(e => {
                return new Date(e['data']['time']* 1000).toLocaleString("default")
            })

            let co2 = parsedData.map(e => {return e.data.co2});
            let temp = parsedData.map(e => {return e.data.temp});
            let hum = parsedData.map(e => {return e.data.hum});
            let noise = parsedData.map(e => {return e.data.noise});

            let xaxis = {
                labels: {
                    maxHeight: 45,
                    show: true,
                    rotate: 0,
                    formatter: function (value) {
                        if (value){
                            let s = value.split(', ')
                            return ['D: ' + s[0].split('.').slice(0, 2), 'T: ' + s[1].split(':').slice(0, 2)];
                        }
                    },
                },
                tickAmount: 2,
                categories:x
            };
            
            const pdLen = parsedData.length-1;
            sensors.forEach(e => {
                let childForInsertion = e.querySelector(`span[id='for-data']`);
                debugger
                switch (e.outerText) {
                    case 'Потребляемая мощность':
                        childForInsertion.textContent = parsedData[pdLen].data.battery;
                        break;

                    case 'Температура':
                        childForInsertion.textContent = parsedData[pdLen].data.temp;
                        break;

                    case 'Влажность':
                        childForInsertion.textContent = parsedData[pdLen].data.hum;
                        break;

                    case 'Освещенность помещения':
                        childForInsertion.textContent = parsedData[pdLen].data.lux;
                        break;

                    case 'Уровень шума':
                        childForInsertion.textContent = parsedData[pdLen].data.noise;
                        break;

                    case 'Уровень CO2':
                        childForInsertion.textContent = parsedData[pdLen].data.co2;
                        break;
                
                    default:
                        break;
                }
            })


            var demoChart1 = {
                colors: ["#9c51ab"],
                series: [{
                    name: "Количество CO2",
                    data: co2
                }],
                chart: {
                    height: 'auto',
                    width: '100%',
                    type: "area",
                    toolbar: {
                    show: false
                    }
                },
                dataLabels: {
                    enabled: false
                },
                stroke: {
                    curve: "smooth"
                },
                yaxis: {
                    max:  Math.max(...co2)*1.1,
                    min:  Math.min(...co2)*0.9,
                    tickAmount: 3           
                },
                xaxis: {
                    labels: {
                        show: true,
                        rotate: -10,
                        formatter: function (value) {
                            if (value){
                                let s = value.split(', ')
                                console.log(s)
                                return 'D: ' + s[0].split('.').slice(0, 2)  + '\n  T: ' + s[1].split(':').slice(0, 2);
                            }
                        },
                    },
                    tickAmount: 2,
                    categories:x
                },
                tooltip: {
                    x: {
                    format: "dd/MM/yy HH:mm"
                    }
                },
                legend: {
                    position: "top",
                    horizontalAlign: "left",
                    fontSize: "14px"
                }
            };
            demoChart1.xaxis = xaxis

            var demoChart2 = {
                colors: ["#ec9a1f"],
                series: [{
                    name: "Температура",
                    data: temp
                }],
                chart: {
                    height: 'auto',
                    type: "area",
                    toolbar: {
                    show: false
                    }
                },
                dataLabels: {
                    enabled: false
                },
                stroke: {
                    curve: "smooth"
                },
                yaxis: {
                    max:  Math.max(...temp)*1.1,
                    min:  Math.min(...temp)*0.9,
                    tickAmount: 3           
                },
                xaxis: {
                    labels: {
                        maxHeight: 45,
                        show: true,
                        rotate: 0,
                        formatter: function (value) {
                            if (value){
                                let s = value.split(', ')
                                console.log(s)
                                return ['D: ' + s[0].split('.').slice(0, 2), 'T: ' + s[1].split(':').slice(0, 2)];
                            }
                        },
                    },
                    offsetX: -15,
                    tickAmount: 2,
                    categories:x
                },
                tooltip: {
                    x: {
                    format: "dd/MM/yy HH:mm"
                    }
                },
                legend: {
                    position: "top",
                    horizontalAlign: "left",
                    fontSize: "14px"
                }
            };
            demoChart2.xaxis = xaxis

            var demoChart3 = {
                colors: ["#17fc03"],
                series: [{
                    name: "Влажность",
                    data: hum
                }],
                chart: {
                    height: 'auto',
                    type: "area",
                    toolbar: {
                    show: false
                    }
                },
                dataLabels: {
                    enabled: false
                },
                stroke: {
                    curve: "smooth"
                },
                yaxis: {
                    max:  Math.max(...hum)*1.1,
                    min:  Math.min(...hum)*0.9,
                    tickAmount: 3           
                },
                xaxis: {
                    labels: {
                        show: true,
                        rotate: -75,
                        formatter: function (value) {
                            if (value){
                                let s = value.split(', ')
                                console.log(s)
                                return 'D: ' + s[0].split('.').slice(0, 2)  + '  T: ' + s[1].split(':').slice(0, 2);
                            }
                        },
                    },
                    tickAmount: 2,
                    categories:x
                },
                tooltip: {
                    x: {
                    format: "dd/MM/yy HH:mm"
                    }
                },
                legend: {
                    position: "top",
                    horizontalAlign: "left",
                    fontSize: "14px"
                }
            };
            demoChart3.xaxis = xaxis

            var demoChart4 = {
                colors: ["#03a5fc"],
                series: [{
                    name: "Шум",
                    data: noise
                }],
                chart: {
                    height: 'auto',
                    type: "area",
                    toolbar: {
                    show: false
                    }
                },
                dataLabels: {
                    enabled: false
                },
                stroke: {
                    curve: "smooth"
                },
                yaxis: {
                    max:  Math.max(...noise)*1.01,
                    min:  Math.min(...noise)*0.95,
                    tickAmount: 3           
                },
                xaxis: {
                    labels: {
                        show: true,
                        rotate: -75,
                        formatter: function (value) {
                            if (value){
                                let s = value.split(', ')
                                console.log(s)
                                return 'D: ' + s[0].split('.').slice(0, 2)  + '  T: ' + s[1].split(':').slice(0, 2);
                            }
                        },
                    },
                    tickAmount: 2,
                    categories:x
                },
                tooltip: {
                    x: {
                    format: "dd/MM/yy HH:mm"
                    }
                },
                legend: {
                    position: "top",
                    horizontalAlign: "left",
                    fontSize: "14px"
                }
            };
            demoChart4.xaxis = xaxis

            
            var demo1 = document.querySelector("#demoChart1");
            var demo2 = document.querySelector("#demoChart2");
            var demo3 = document.querySelector("#demoChart3");
            var demo4 = document.querySelector("#demoChart4");

            setTimeout(function () {
                demo1._chart = new ApexCharts(demo1, demoChart1);
                demo1._chart.render();

                demo2._chart = new ApexCharts(demo2, demoChart2);
                demo2._chart.render();

                demo3._chart = new ApexCharts(demo3, demoChart3);
                demo3._chart.render();

                demo4._chart = new ApexCharts(demo4, demoChart4);
                demo4._chart.render();
            });
        };
        
        window.addEventListener("app:mounted", onLoad, {
            once: true
        });
    /******/ })();