var x = 7;
var y = 'high';
let currentChart = null;
let stockData = null;
company_id = null;
company_name = null;

// Function to fetch and store data
async function fetchStockData(period, category) {
  // if (stockData) {
  //   return stockData; // Return cached data if already fetched
  // }

  // try {
  //   const response = await fetch('/main/data_stream');
  //   stockData = await response.json();
  //   return stockData;
  // } catch (error) {
  //   console.error('Error fetching stock data:', error);
  //   throw error;
  // }

  var data_file;
  switch (period) {
    case (7):
      switch (category) {
        case ('high'):
          data_file = '/seven_day_high.json';
          break;
        case ('low'):
          data_file = '/seven_day_low.json';
          break;
        case ('open'):
          data_file = '/seven_day_open.json';
          break;
        case ('close'):
          data_file = '/seven_day_close.json';
        case ('volume'):
          data_file = '/seven_day_volume.json';
      }
      break;
    case (30):
      switch (category) {
        case ('high'):
          data_file = '/thirty_one_day_high.json';
          break;
        case ('low'):
          data_file = '/thirty_one_day_low.json';
          break;
        case ('open'):
          data_file = '/thirty_one_day_open.json';
          break;
        case ('close'):
          data_file = '/thirty_one_day_close.json';
        case ('volume'):
          data_file = '/thirty_one_day_volume.json';
      }
      break;
    case(365):
      switch (category) {
        case ('high'):
          data_file = '/three_six_five_day_high.json';
          break;
        case ('low'):
          data_file = '/three_six_five_day_low.json';
          break;
        case ('open'):
          data_file = '/three_six_five_day_open.json';
          break;
        case ('close'):
          data_file = '/three_six_five_day_close.json';
        case ('volume'):
          data_file = '/three_six_five_day_volume.json';
      }
      break;
      case(5):
        switch (category)  {
            case ('high'):
              data_file = '/five_year_high.json';
              break;
            case ('low'):
              data_file = '/five_year_low.json';
              break;
            case ('open'):
              data_file = '/five_year_open.json';
              break;
            case ('close'):
              data_file = '/five_year_close.json';
            case ('volume'):
        }
      }
  
  const response = fetch(data_file);
  stockData = response;
  return stockData;
}

function destroyCurrentChart() {
  if (currentChart) {
    currentChart.destroy();
  }
  currentChart = null;
}

function loadChartx(period) {
  x = period;
  loadChart()
}

function loadCharty(category) {
  y = category;
  loadChart()
}


function loadChart() {
  const chart_texts = [
    [company_name + ' Stock High Prices ($) for the Last 7 Days', 'Price ($)', 'Date', 'high_button'],
      [company_name + ' Stock Low Prices ($) for the Last 7 Days', 'Price ($)', 'Date', 'low_button'],
      [company_name + ' Stock Opening Prices ($) for the Last 7 Days', 'Price ($)', 'Date', 'open_button'],
      [company_name + ' Stock Closing Prices ($) for the Last 7 Days', 'Price ($)', 'Date', 'close_button'],
      [company_name + ' Stock Volume (ea.) for the Last 7 Days', 'Units (ea.)', 'Date', 'volume_button']
      [company_name + ' Stock High Prices ($) for the Last 30 Days', 'Price ($)', 'Date', 'high_button'],
      [company_name + ' Stock Low Prices ($) for the Last 30 Days', 'Price ($)', 'Date', 'low_button'],
      [company_name + ' Stock Opening Prices ($) for the Last 30 Days', 'Price ($)', 'Date', 'open_button'],
      [company_name + ' Stock Closing Prices ($) for the Last 30 Days', 'Price ($)', 'Date', 'close_button'],
      [company_name + ' Stock Volume (ea.) for the Last 30 Days', 'Units (ea.)', 'Date', 'volume_button']
      [company_name + ' Stock High Prices ($) for the Last Year', 'Price ($)', 'Date', 'high_button'],
      [company_name + ' Stock Low Prices ($) for the Last Year', 'Price ($)', 'Date', 'low_button'],
      [company_name + ' Stock Opening Prices ($) for the Last Year', 'Price ($)', 'Date', 'open_button'],
      [company_name + ' Stock Closing Prices ($) for the Last Year', 'Price ($)', 'Date', 'close_button'],
      [company_name + ' Stock Volume (ea.) for the Last Year', 'Units (ea.)', 'Date', 'volume_button']
      [company_name + ' Stock High Prices ($) for the Last 5 Years', 'Price ($)', 'Date', 'high_button'],  
      [company_name + ' Stock Low Prices ($) for the Last 5 Years', 'Price ($)', 'Date', 'low_button'],
      [company_name + ' Stock Opening Prices ($) for the Last 5 Years', 'Price ($)', 'Date', 'open_button'],
      [company_name + ' Stock Closing Prices ($) for the Last 5 Years', 'Price ($)', 'Date', 'close_button'],
      [company_name + ' Stock Volume (ea.) for the Last 5 Years', 'Units (ea.)', 'Date', 'volume_button'],
    ];
  
  var current_labels;
  
  switch (x) {
    case (7):
      switch (y) {
        case ('high'):
          current_labels = chart_texts[0];
          break;
        case ('low'):
          current_labels = chart_texts[1];
          break;
        case ('open'):
          current_labels = chart_texts[2];
          break;
        case ('close'):
          current_labels = chart_texts[3];
          break;
        case ('volume'):
          current_labels = chart_texts[4];
          break;
      }
    case (30):
      switch (y) {
          case ('high'):
          current_labels = chart_texts[5];
          break;
        case ('low'):
          current_labels = chart_texts[6];
          break;
        case ('open'):
          current_labels = chart_texts[7];
          break;
        case ('close'):
          current_labels = chart_texts[8];
          break;
        case ('volume'):
          current_labels = chart_texts[9];
          break;
      }
    case (365):
      switch (y) {
          case ('high'):
          current_labels = chart_texts[10];
          break;
        case ('low'):
          current_labels = chart_texts[11];
          break;
        case ('open'):
          current_labels = chart_texts[12];
          break;
        case ('close'):
          current_labels = chart_texts[13];
          break;
        case ('volume'):
          current_labels = chart_texts[14];
          break;
      }
    case (5):
      switch (y) {
          case ('high'):
          current_labels = chart_texts[15];
          break;
        case ('low'):
          current_labels = chart_texts[16];
          break;
        case ('open'):
          current_labels = chart_texts[17];
          break;
        case ('close'):
          current_labels = chart_texts[18];
          break;
        case ('volume'):
          current_labels = chart_texts[19];
      }
  }                      

  destroyCurrentChart();
  try {
    data = fetchStockData();
    const config = {
      type: 'line',
      data: data,
      options: {
        responsive: true,
        plugins: {
          legend: {
            position: 'top',
          },
          title: {
            display: true,
            text: 'Chart.js Line Chart'
          }
        }
      },
    };

    const values = Object.values(data);
    const labels = values.map(value => value.date);
    const numerical_y_data = values.map(value => value[y]);
    currentChart = new Chart(document.getElementById('lineChart'), config)
    currentChart.options.plugins.title.text = current_labels[0];
    currentChart.data = data;
    // currentChart.options.scales.y.title.text = current_labels[1];
    // currentChart.options.scales.x.title.text = current_labels[2];
    currentChart.update();
    
  } catch (error) {
      console.error('Error loading opening data:', error);
  }
}

// Dropdown button Handling

function disableActiveXButton(active) {
  if (! ['7', '30', '365', '5', '10'].find(active)) {
    console.error('Invalid active button ID, X-axis', active)
  }
  const activeButton = document.getElementById(active);
  activeButton.classList.add('active')
  const high = document.getElementById('7');
  if (activeButton !== high) {
    high.classList.remove('active');
  }
  const low = document.getElementById('30');
  if (activeButton !== low) {
    low.classList.remove('active');
  }
  const open = document.getElementById('365');
  if (activeButton !== open) {
    open.classList.remove('active');
  }
  const close =  document.getElementById('5');
  if (activeButton !== close) {
    close.classList.remove('active');
  }
  loadChart();
}

function disableActiveYButton(active) {
  if (! ['high_button', 'low_button', 'open_button', 'close_button', 'volume_button'].find(active)) {
    console.error('Invalid active button ID, Y-axis', active);
  }
  const activeButton = document.getElementById(active);
  activeButton.classList.add('active')
  const high = document.getElementById('high_button');
  if (activeButton !== high) {
    high.classList.remove('active');
  }
  const low = document.getElementById('low_button');
  if (activeButton !== low) {
    low.classList.remove('active');
  }
  const open = document.getElementById('open_button');
  if (activeButton !== open) {
    open.classList.remove('active');
  }
  const close =  document.getElementById('close_button');
  if (activeButton !== close) {
    close.classList.remove('active');
  }
  const volume = document.getElementById('volume_button');
  if (activeButton !== volume) {
    volume.classList.remove('active');
  }
  loadChart();
}

// Load the default chart on page load
document.addEventListener('DOMContentLoaded', function() {
  loadChart();
});