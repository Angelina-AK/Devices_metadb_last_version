/******/ (() => { // webpackBootstrap
    var __webpack_exports__ = {};
    /*!*************************************************!*\
      !*** ./src/js/pages/components-table-gridjs.js ***!
      \*************************************************/
    var onLoad = async  function onLoad() {
      var dropdownConfig = {
        placement: "bottom-start",
        modifiers: [{
          name: "offset",
          options: {
            offset: [0, 4]
          }
        }]
      };
     
      new Popper("#dropdown-wrapper4", ".popper-ref", ".popper-root", dropdownConfig);
      const dataUrlObjectsInHierarchy = '/records/get';
      
      response = await fetch(dataUrlObjectsInHierarchy);
      const data = await response.json() 
      console.log(data.data);
      var gridTable4 = document.querySelector("#grid-table-4");
      var gridConfig4 = {
        columns: [{
          id: "id",
          name: "ID",
          formatter: function formatter(cell) {
            return Gridjs.html("<span class=\"mx-2\">".concat(cell, "</span>"));
          }
        }, {
          id: "device_name",
          name: "Device",
          formatter: function formatter(cell) {
            return Gridjs.html("<span class=\"text-slate-700 dark:text-navy-100 font-medium\">".concat(cell, "</span>"));
          }
        }, {
          id: "created",
          name: "Date",
          formatter: function formatter(cell) {
            let date = new Date(cell).toLocaleString();
            return Gridjs.html("<span class=\"text-slate-700 dark:text-navy-100 font-medium\">".concat(date, "</span>"));
          }
        }, {
          id: "config",
          name: "Config",
          sort: false,
          formatter: function formatter(cell) {
            console.log(cell)
            let html = `
              <span class="text-slate-700 dark:text-navy-100 font-medium">
                <a href="${cell}">
                  <span class="inline tag bg-secondary text-white hover:bg-secondary-focus focus:bg-secondary-focus active:bg-secondary-focus/90">Open</span>
                </a>
                
                <a href="${cell+'/edit'}">
                  <span class="inline tag bg-info text-white hover:bg-info-focus focus:bg-info-focus active:bg-info-focus/90">Edit</span>
                </a>
              </span>
            `;
            return Gridjs.html(html);
          }
        }],
        data: data.data,
        sort: true,
        search: true,
        pagination: {
          enabled: true,
          limit: 10
        }
      };
      gridTable4._table = new Gridjs.Grid(gridConfig4).render(gridTable4);
    };
    window.addEventListener("app:mounted", onLoad, {
      once: true
    });
    /******/ })()
    ;

    // [{
    //   id: "1",
    //   name: "John",
    //   email: "john@example.com",
    //   phone: "(01) 22 888 4444",
    //   avatar_url: "images/200x200.png"
    // }, {
    //   id: "2",
    //   name: "Doe",
    //   email: "thedoe@example.com",
    //   phone: "(33) 22 888 4444",
    //   avatar_url: "images/200x200.png"
    // }, {
    //   id: "3",
    //   name: "Nancy",
    //   email: "nancy@example.com",
    //   phone: "(21) 33 888 4444",
    //   avatar_url: "images/200x200.png"
    // }, {
    //   id: "4",
    //   name: "Clarke",
    //   email: "clarke@example.com",
    //   phone: "(44) 33 888 4444",
    //   avatar_url: "images/200x200.png"
    // }, {
    //   id: "5",
    //   name: "Robert",
    //   email: "robert@example.com",
    //   phone: "(27) 63 688 6444",
    //   avatar_url: "images/200x200.png"
    // }, {
    //   id: "6",
    //   name: "Tom",
    //   email: "thetom@example.com",
    //   phone: "(57) 63 688 6444",
    //   avatar_url: "images/200x200.png"
    // }, {
    //   id: "7",
    //   name: "Nolan",
    //   email: "Nolan@example.com",
    //   phone: "(27) 63 688 6444",
    //   avatar_url: "images/200x200.png"
    // }, {
    //   id: "8",
    //   name: "Adam",
    //   email: "Adam@example.com",
    //   phone: "(12) 22 888 4444",
    //   avatar_url: "images/200x200.png"
    // }, {
    //   id: "9",
    //   name: "Glen",
    //   email: "Glen@example.com",
    //   phone: "(74) 22 888 4444",
    //   avatar_url: "images/200x200.png"
    // }, {
    //   id: "10",
    //   name: "Edna",
    //   email: "Edna@example.com",
    //   phone: "(52) 33 888 4444",
    //   avatar_url: "images/200x200.png"
    // }, {
    //   id: "11",
    //   name: "Dianne",
    //   email: "dianne@example.com",
    //   phone: "(78) 33 888 4444",
    //   avatar_url: "images/200x200.png"
    // }, {
    //   id: "12",
    //   name: "Wilson",
    //   email: "wilson@example.com",
    //   phone: "(54) 63 688 6444",
    //   avatar_url: "images/200x200.png"
    // }, {
    //   id: "13",
    //   name: "Ross",
    //   email: "rose@example.com",
    //   phone: "(98) 63 688 6444",
    //   avatar_url: "images/200x200.png"
    // }, {
    //   id: "14",
    //   name: "Henry",
    //   email: "henry@example.com",
    //   phone: "(87) 63 688 6444",
    //   avatar_url: "images/200x200.png"
    // }, {
    //   id: "15",
    //   name: "Kerry",
    //   email: "kerry@example.com",
    //   phone: "(55) 63 688 6444",
    //   avatar_url: "images/200x200.png"
    // }]