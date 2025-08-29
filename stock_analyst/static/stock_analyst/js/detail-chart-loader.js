var x = "7";
var y = "high";
let currentChart = null;
let stockData = null;
const category_name_map = {
    'high': 'High', 'low': 'Low', 'open': 'Open', 'close': 'Close', 'volume': 'Volume'
};
const category_name_suffix = '_button';
const period_name_map = {
    '7': '7 Days', '30': '30 Days', '365': '1 Year', '5': '5 Years', '10': '10 Years'
};
const period_name_suffix = '';
const period_button_id = 'dropdownMenuxButton';
const category_button_id = 'dropdownMenuyButton';
const category_api_call_map = {
    'high': 1,
    'low': 2,
    'open': 3,
    'close': 4,
    'volume': 5,
}

// Function to fetch and store data
async function fetchStockData(period, category) {
    // for API call
    try {
        let request = `data_stream/${company_id}/${x}/${category_api_call_map[y]}`
        const response = await fetch(request);
        stockData = await response.json();
        return stockData;
    } catch (error) {
        console.error('Error fetching stock data:', error);
        throw error;
    }

    // for practice data
//    const periodMap = {
//        "7": "seven_day",
//        "30": "thirty_one_day",
//        "365": "three_six_five_day",
//        "5": "five_year", // Assuming "5" means 5 years
//    };
//    const periodPath = periodMap[period];
//    if (!periodPath) {
//        console.error(`Invalid period specified: ${period}`);
//        return null;
//    }
//    const data_file = `/${periodPath}_${category}.json`;
//    console.log(`Requesting data file: ${data_file}`);
//    try {
//        const response = await fetch(data_file);
//        if (!response.ok) {
//            throw new Error(`HTTP error! status: ${response.status}`);
//        }
//        const jsonData = await response.json();
//        return jsonData;
//    }
//    catch (error) {
//        console.error(`Could not fetch data from ${data_file}:`, error);
//        return null; // Return null to prevent crash in calling function
//    }
}

function destroyCurrentChart() {
    if (currentChart) {
        currentChart.destroy();
        currentChart = null;
    }
}
// A helper function to create chart text labels dynamically
function getChartLabels(period, category) {
    const periodTextMap = {
        "7": "Last 7 Days",
        "30": "Last 30 Days",
        "365": "Last Year",
        "5": "Last 5 Years",
        "10": "Last 10 Years"
    };
    const categoryTextMap = {
        high: "High Prices ($)",
        low: "Low Prices ($)",
        open: "Opening Prices ($)",
        close: "Closing Prices ($)",
        volume: "Volume (ea.)",
    };
    const yAxisLabelMap = {
        high: "Price ($)",
        low: "Price ($)",
        open: "Price ($)",
        close: "Price ($)",
        volume: "Units (ea.)",
    };
    const title = `${company_name} Stock ${categoryTextMap[category]} for the ${periodTextMap[period]}`;
    const yAxisLabel = yAxisLabelMap[category];
    const xAxisLabel = "Date";
    return { title, yAxisLabel, xAxisLabel };
}
function loadChartx(period) {
    x = period;
    updateActiveButton(period_button_id, x, period_name_map, period_name_suffix);
    loadChart();
}
function loadCharty(category) {
    y = category;
    updateActiveButton(category_button_id, y, category_name_map, category_name_suffix);
    loadChart();
}

// TODO Reverse dataset so dates ascend from left to right
// TODO Fix major performance issues with large datasets
async function loadChart() {
  const current_labels = getChartLabels(x, y);
  console.log(`Loading chart for ${y} data for the last ${x} days`);

  let data;
  try {
    data = await fetchStockData(x, y);
    if (!data) {
      console.error("Fetch returned no data. Aborting chart load.");
      return; // Exit if there's no data
    }
  } catch (error) {
    console.error("Error fetching stock data:", error);
    return; // Exit the function if fetching fails
  }

  // Prepare the new data and labels
  const values = Object.values(data);
  const labels = values.map(value => value.date);
  const numericalData = values.map(value => value[y]);
  const newLabel = y.charAt(0).toUpperCase() + y.slice(1);

  // Check if the chart instance already exists
  if (currentChart) {
    // --- UPDATE EXISTING CHART ---
    console.log("Updating existing chart...");

    // Update the data
    currentChart.data.labels = labels;
    currentChart.data.datasets[0].data = numericalData;
    currentChart.data.datasets[0].label = newLabel;

    // Update the options (like titles)
    currentChart.options.plugins.title.text = current_labels.title;
    currentChart.options.scales.y.title.text = current_labels.yAxisLabel;
    currentChart.options.scales.x.title.text = current_labels.xAxisLabel;

    // Now, call update() on the actual Chart.js instance
    currentChart.update();

  } else {
    // --- CREATE NEW CHART ---
    console.log("Creating new chart...");

    const config = {
      type: "line",
      data: {
        labels: labels,
        datasets: [{
          label: newLabel,
          data: numericalData,
          borderColor: 'rgb(75, 192, 192)',
          tension: 0.1,
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: "top",
          },
          title: {
            display: true,
            text: current_labels.title,
          },
        },
        scales: {
          y: {
            title: {
              display: true,
              text: current_labels.yAxisLabel
            }
          },
          x: {
            title: {
              display: true,
              text: current_labels.xAxisLabel
            }
          }
        }
      },
    };

    const ctx = document.getElementById("lineChart").getContext('2d');
    // Store the Chart.js INSTANCE in the global variable
    currentChart = new Chart(ctx, config);
  }
}

// Dropdown button Handling
function updateActiveButton(mainButtonId, activeId, nameMap, suffix = '') {
    // Update main button text
    const mainButton = document.getElementById(mainButtonId);
    if (mainButton) {
        mainButton.textContent = `Select: ${nameMap[activeId]}`;
    }
    // Update active state on dropdown items
    const element = document.getElementById(activeId + suffix);
    if (element && element.parentElement) {
        const parent = element.parentElement;
        const buttons = parent.querySelectorAll('.dropdown-item'); // Assuming items have this class
        buttons.forEach(button => {
            button.classList.remove('active');
        });
        const activeButton = document.getElementById(activeId + suffix);
        if (activeButton) {
            activeButton.classList.add('active');
        }
    }
}
document.addEventListener("DOMContentLoaded", function () {
    updateActiveButton(period_button_id, x, period_name_map, period_name_suffix);
    updateActiveButton(category_button_id, y, category_name_map, category_name_suffix);
    loadChart();
});
