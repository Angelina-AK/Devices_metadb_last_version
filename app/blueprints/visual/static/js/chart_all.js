/******/ ( async () => { // webpackBootstrap
    var __webpack_exports__ = {};
    /*!***********************************************!*\
    !*** ./src/js/pages/components-apexcharts.js ***!
    \***********************************************/

    const device_id = document.querySelector('#device_id').value;

    // Получаем данные с устройства (включая value - необработанные значения)
    const fetchData = async () => {
        const response = await fetch(`/chart/${device_id}/get_data`);
        const data = await response.json();
        return  data;
    }   

    // Зоны графика и декодированных данных
    let otherStatSensors = document.querySelectorAll(`div[data-decodekey]`);
    let chartsArea = document.querySelectorAll(`div[id^=myAreaChart]`) 

    // Функция декодирования
    var onLoad =  async function onLoad() {


        const data = await fetchData(); // полученные данные с устройства
        let parsedData = Array(); // массив с будущими декодированными данными

        // декодирование значений с устройства
        data.forEach(e => {
            parsedData.push(decoder(JSON.parse(e.value)));
        })

        parsedData = parsedData.reverse();
        const parsedDataLen = parsedData.length - 1;

        // перевод к локальному времени
        let x = parsedData.map(e => {
            return new Date(e['data']['time']* 1000).toLocaleString("default")
        })

        otherStatSensors.forEach(e => {
            const sensorKey = e.dataset.decodekey;
            let tmp = e.querySelector('p[id^=now]');
            tmp.textContent = parsedData[parsedDataLen].data[sensorKey];

            tmp =  e.querySelector('p[id^=average]');
            let sum = 0;
            parsedData.forEach(e => {
                sum += e.data[sensorKey];
            })
            const avgVal = (sum/parsedDataLen).toFixed(0);
            tmp.textContent = avgVal;

            tmp = e.querySelector('p[id^=min]');
            let min = parsedData[0].data[sensorKey];
            let max = parsedData[0].data[sensorKey];
            for (let index = 0; index < parsedData.length; index++) {
                const e =  parsedData[index].data[sensorKey]
                if (e < min) min = e;
                if (e > max) max = e;
            }
            tmp.textContent = min;
            tmp = e.querySelector('p[id^=max]');
            tmp.textContent = max;

        });

        chartsArea.forEach( e => {
            const sensor = e.dataset.sensor;
            let series = [];
            for(let i = 0 ; i <= parsedDataLen; i++) {
                series.push(parsedData[i].data[sensor]);
            }

            let ymax = Math.max(...series)*1.1;
            let ymin = Math.min(...series)*0.9;

            if (sensor==='time'){
                ymax = Math.max(...series);
                ymin = Math.min(...series);
            } 

            let demoChart = {
                colors: ["#9c51ab"],
                series: [{
                    name: sensor,
                    data: series
                }],
                chart: {
                    height: 380,
                    width: '100%',
                    type: "area",
                    toolbar: {
                        show: true
                    }
                },
                dataLabels: {
                    enabled: false
                },
                stroke: {
                    curve: "smooth"
                },
                yaxis: {
                    max:  ymax,
                    min:  ymin,
                    tickAmount: 5         
                },
                xaxis: {
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
                    tickAmount: 3,
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
                    fontSize: "14px",
                    showForSingleSeries: true
                }
            };
            
            e._chart = new ApexCharts(e, demoChart);
            e._chart.render();
            console.log(series);
        })
    }

    window.addEventListener("app:mounted", onLoad, {
        once: true
    });
/******/ })();