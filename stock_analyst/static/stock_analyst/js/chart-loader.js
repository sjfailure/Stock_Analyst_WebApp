let currentChart = null;
let stockData = null; // Global variable to store fetched data
var company_ids = {};

// Function to fetch and store data
async function fetchStockData() {
  // // API call
  if (stockData) {
    return stockData; // Return cached data if already fetched
  }


  try {
    const response = await fetch("/main/data_stream");
    stockData = await response.json();
    console.log(stockData)
    populateCompanyIds(stockData);
    return stockData;
  } catch (error) {
    console.error("Error fetching stock data:", error);
    throw error;
  }

   // practice data call
   // const response = await fetch('/sample.json');
   // stockData = await response.json();
   // // console.log(stockData);
   // populateCompanyIds(stockData); // Populate company_ids after fetching data
   // return stockData;
}

function destroyCurrentChart() {
  if (currentChart) {
    currentChart.destroy();
    currentChart = null;
  }
}

function disableActiveButton(active) {
  const mainButton = document.getElementById("dropdownMenuButton");
  if (mainButton) {
    mainButton.textContent = `Select: ${active.charAt(0).toUpperCase() + active.slice(1, active.lastIndexOf("_"))}`;
  }
  const element = document.getElementById(active);
  if (element && element.parentElement) {
    const parent = element.parentElement;
    const buttons = parent.querySelectorAll(".dropdown-item"); // Assuming items have this class
    buttons.forEach((button) => {
      button.classList.remove("active");
    });
    const activeButton = document.getElementById(active);
    if (activeButton) {
      activeButton.classList.add("active");
    }
  } else {
    console.log("Something wrong with button settings");
    return null;
  }
}

async function loadChart(chart_category) {
  // destroyCurrentChart();

  // constants data for DRY chart manipulate function
  const chart_info = {
    high: [
      "high",
      "Stock High Prices ($)",
      "Stock High Prices by Company",
      "Price ($)",
      "Company",
      "high_button",
    ],
    low: [
      "low",
      "Stock Low Prices ($)",
      "Stock Low Prices by Company",
      "Price ($)",
      "Company",
      "low_button",
    ],
    open: [
      "open",
      "Stock Opening Prices ($)",
      "Stock Opening Prices by Company",
      "Price ($)",
      "Company",
      "open_button",
    ],
    close: [
      "close",
      "Stock Closing Prices ($)",
      "Stock Closing Prices by Company",
      "Price ($)",
      "Company",
      "close_button",
    ],
    volume: [
      "volume",
      "Volume for Day (ea.)",
      "Stock Volume Movement by Company",
      "Units (ea.)",
      "Company",
      "volume_button",
    ],
  };

  try {
    const data = await fetchStockData();
    const companies = Object.values(data);
    const labels = companies.map((company) => company.company_name);
    var numerical_x_data = companies.map((company) => company[chart_category]);
    //    switch (chart_category) {
    //        case 'high':
    //          numerical_x_data = companies.map(company => company.high);
    //          break;
    //        case 'low':
    //          numerical_x_data = companies.map(company => company.low);
    //          break;
    //        case 'open':
    //          numerical_x_data = companies.map(company => company.open);
    //          break;
    //        case 'close':
    //          numerical_x_data = companies.map(company => company.close);
    //          break;
    //        case 'volume':
    //          numerical_x_data = companies.map(company => company.volume);
    //          break;
    //        default:
    //        return;
    //    };
    const date = companies.map((company) => company.date);
    if (currentChart) {
      if (currentChart.data.datasets.length > 0) {
        currentChart.data.labels = labels;
        currentChart.data.datasets[0].data = numerical_x_data;
        currentChart.data.datasets[0].label = chart_info[chart_category][1];
        currentChart.options.scales.y.title.text =
          chart_info[chart_category][3];
        currentChart.options.scales.x.title.text =
          chart_info[chart_category][4];
        currentChart.options.plugins.title.text = chart_info[chart_category][2];
      } else {
        console.error("No datasets found in the chart");
      }
      currentChart.update(); // Update the chart with new data
      // console.log('new chart data')
    } else {
      // Create a new chart if it doesn't exist
      currentChart = new Chart(document.getElementById("main_chart"), {
        type: "bar",
        data: {
          labels: labels,
          datasets: [
            {
              label: chart_info[chart_category][1],
              data: numerical_x_data,
              backgroundColor: [
                "rgba(54, 162, 235, 0.8)",
                "rgba(255, 99, 132, 0.8)",
                "rgba(255, 205, 86, 0.8)",
              ],
              borderColor: [
                "rgba(54, 162, 235, 1)",
                "rgba(255, 99, 132, 1)",
                "rgba(255, 205, 86, 1)",
              ],
              borderWidth: 2,
            },
          ],
        },
        options: {
          responsive: true,
          onClick: (event) => {
            const activePoints = currentChart.getElementsAtEventForMode(
              event,
              "nearest",
              { intersect: true },
              false,
            );
            if (activePoints.length) {
              const firstPoint = activePoints[0];
              const label = currentChart.data.labels[firstPoint.index];
              const companyId = company_ids[label]; // Use company_ids to retrieve company_id
              console.log(`Navigating to details of company: ${label}, id: ${companyId}`);
              window.location.assign(`/main/detail/${companyId}`);
            }
          },
          plugins: {
            title: {
              display: true,
              text: chart_info[chart_category][2],
            },
            legend: { display: false },
            tooltip: {
              callbacks: {
                afterLabel: function (context) {
                  const companyIndex = context.dataIndex;
                  return "Date: " + date[companyIndex];
                },
              },
            },
          },
          scales: {
            y: {
              beginAtZero: true,
              title: { display: true, text: chart_info[chart_category][3] },
            },
            x: {
              title: { display: true, text: chart_info[chart_category][4] },
            },
          },
        },
      });
    }
  } catch (error) {
    console.error("Error loading data:", error);
  }
  disableActiveButton(chart_info[chart_category][5]);
}

// Function to populate company_ids
function populateCompanyIds(data) {
   for (const company of Object.values(data)) {
       company_ids[company.company_name] = company.company_id;
   }
}

// Load the default chart on page load
document.addEventListener("DOMContentLoaded", function () {
  loadChart("high");
});
