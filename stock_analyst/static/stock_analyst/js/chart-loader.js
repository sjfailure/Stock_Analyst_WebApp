
let currentChart = null;
let stockData = null; // Global variable to store fetched data

// Function to fetch and store data
async function fetchStockData() {
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

  const response = await fetch('/sample.json');
  stockData = await response.json();
  return stockData;
}

function destroyCurrentChart() {
  if (currentChart) {
    currentChart.destroy();
    currentChart = null;
  }
}

function disableActiveButton(active) {
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
}

async function loadChart(chart_category) {
  // destroyCurrentChart();

  // constants data for DRY chart manipulate function
  const chart_info = {
    'high': ['high', 'Stock High Prices ($)', 'Stock High Prices by Company', 'Price ($)', 'Company', 'high_button'],
    'low': ['low', 'Stock Low Prices ($)', 'Stock Low Prices by Company', 'Price ($)', 'Company', 'low_button' ],
    'open': ['open', 'Stock Opening Prices ($)', 'Stock Opening Prices by Company', 'Price ($)', 'Company', 'open_button' ],
    'close': ['close', 'Stock Closing Prices ($)', 'Stock Closing Prices by Company', 'Price ($)', 'Company', 'close_button' ],
    'volume': ['volume', 'Volume for Day (ea.)', 'Stock Volume Movement by Company', 'Units (ea.)', 'Company', 'volume_button']
  }

  try {
    const data = await fetchStockData();
    const companies = Object.values(data);
    const labels = companies.map(company => company.company_name);
    var numerical_x_data;
    switch (chart_category) {
        case 'high':
          numerical_x_data = companies.map(company => company.high);
          break;
        case 'low':
          numerical_x_data = companies.map(company => company.low);
          break;
        case 'open':
          numerical_x_data = companies.map(company => company.open);
          break;
        case 'close':
          numerical_x_data = companies.map(company => company.close);
          break;
        case 'volume':
          numerical_x_data = companies.map(company => company.volume);
          break;
        default:
        return;
    };
    const date = companies.map(company => company.date);
    if (currentChart) {
      if (currentChart.data.datasets.length > 0) {
        currentChart.data.labels = labels;
        currentChart.data.datasets[0].data = numerical_x_data;
        currentChart.data.datasets[0].label = chart_info[chart_category][1];
        currentChart.options.scales.y.title.text = chart_info[chart_category][3];
        currentChart.options.scales.x.title.text = chart_info[chart_category][4];
        currentChart.options.plugins.title.text = chart_info[chart_category][2];
      } else {
        console.error('No datasets found in the chart')
      }
      currentChart.update(); // Update the chart with new data
      // console.log('new chart data')
    } else {
      // Create a new chart if it doesn't exist
      currentChart = new Chart(
      document.getElementById('main_chart'),
      {
        type: 'bar',
        data: {
          labels: labels,
          datasets: [{
            label: chart_info[chart_category][1],
            data: numerical_x_data,
            backgroundColor: [
              'rgba(54, 162, 235, 0.8)',
              'rgba(255, 99, 132, 0.8)',
              'rgba(255, 205, 86, 0.8)'
            ],
            borderColor: [
              'rgba(54, 162, 235, 1)',
              'rgba(255, 99, 132, 1)',
              'rgba(255, 205, 86, 1)'
            ],
            borderWidth: 2
          }]
        },
        options: {
          responsive: true,
          onClick: (event) => {
            const activePoints = currentChart.getElementsAtEventForMode(event, 'nearest', { intersect: true }, false);
            if (activePoints.length) {
              const firstPoint = activePoints[0];
              const label = currentChart.data.labels[firstPoint.index];
              console.log(`You clicked on ${label}`);
              window.location.assign('detail.html');
            };
          },
          plugins: {
            title: {
              display: true,
              text: chart_info[chart_category][2]
            },
            legend: { display: false },
            tooltip: {
              callbacks: {
                afterLabel: function(context) {
                  const companyIndex = context.dataIndex;
                  return 'Date: ' + date[companyIndex];
                }
              }
            }
          },
          scales: {
            y: {
              beginAtZero: true,
              title: { display: true, text: chart_info[chart_category][3] }
            },
            x: {
              title: { display: true, text: chart_info[chart_category][4] }
            }
          }
        }
      }
    );
    }
  } catch (error) {
    console.error('Error loading data:', error);
  }
  disableActiveButton(chart_info[chart_category][5]);
}

// async function loadLowsChart() {
//   destroyCurrentChart();

//   try {
//     const data = await fetchStockData();
//     const companies = Object.values(data);
//     const labels = companies.map(company => company.company_name);
//     const lows = companies.map(company => company.low);
//     const date = companies.map(company => company.date);

//     currentChart = new Chart(
//       document.getElementById('main_chart'),
//       {
//         type: 'bar',
//         data: {
//           labels: labels,
//           datasets: [{
//             label: 'Stock Low Prices ($)',
//             data: lows,
//             backgroundColor: [
//               'rgba(255, 99, 132, 0.8)',
//               'rgba(54, 162, 235, 0.8)',
//               'rgba(255, 205, 86, 0.8)'
//             ],
//             borderColor: [
//               'rgba(255, 99, 132, 1)',
//               'rgba(54, 162, 235, 1)',
//               'rgba(255, 205, 86, 1)'
//             ],
//             borderWidth: 2
//           }]
//         },
//         options: {
//           responsive: true,
//           plugins: {
//             title: {
//               display: true,
//               text: 'Stock Low Prices by Company'
//             },
//             legend: { display: false },
//             tooltip: {
//               callbacks: {
//                 afterLabel: function(context) {
//                   const companyIndex = context.dataIndex;
//                   return 'Date: ' + date[companyIndex];
//                 }
//               }
//             }
//           },
//           scales: {
//             y: {
//               beginAtZero: true,
//               title: { display: true, text: 'Price ($)' }
//             },
//             x: {
//               title: { display: true, text: 'Company' }
//             }
//           }
//         }
//       }
//     );
//   } catch (error) {
//     console.error('Error loading lows data:', error);
//   }
//   disableActiveButton('low_button');
// }

// async function loadOpenChart() {
//   destroyCurrentChart();

//   try {
//     const data = await fetchStockData();
//     const companies = Object.values(data);
//     const labels = companies.map(company => company.company_name);
//     const open = companies.map(company => company.open);
//     const date = companies.map(company => company.date);

//     currentChart = new Chart(
//       document.getElementById('main_chart'),
//       {
//         type: 'bar',
//         data: {
//           labels: labels,
//           datasets: [{
//             label: 'Stock Opening Prices ($)',
//             data: open,
//             backgroundColor: [
//               'rgba(54, 162, 235, 0.8)',
//               'rgba(255, 99, 132, 0.8)',
//               'rgba(255, 205, 86, 0.8)'
//             ],
//             borderColor: [
//               'rgba(54, 162, 235, 1)',
//               'rgba(255, 99, 132, 1)',
//               'rgba(255, 205, 86, 1)'
//             ],
//             borderWidth: 2
//           }]
//         },
//         options: {
//           responsive: true,
//           plugins: {
//             title: {
//               display: true,
//               text: 'Stock Opening Prices by Company'
//             },
//             legend: { display: false },
//             tooltip: {
//               callbacks: {
//                 afterLabel: function(context) {
//                   const companyIndex = context.dataIndex;
//                   return 'Date: ' + date[companyIndex];
//                 }
//               }
//             }
//           },
//           scales: {
//             y: {
//               beginAtZero: true,
//               title: { display: true, text: 'Price ($)' }
//             },
//             x: {
//               title: { display: true, text: 'Company' }
//             }
//           }
//         }
//       }
//     );
//   } catch (error) {
//     console.error('Error loading opening data:', error);
//   }
//   disableActiveButton('open_button');
// }

// async function loadCloseChart() {
//   destroyCurrentChart();

//   try {
//     const data = await fetchStockData();
//     const companies = Object.values(data);
//     const labels = companies.map(company => company.company_name);
//     const close = companies.map(company => company.close);
//     const date = companies.map(company => company.date);

//     currentChart = new Chart(
//       document.getElementById('main_chart'),
//       {
//         type: 'bar',
//         data: {
//           labels: labels,
//           datasets: [{
//             label: 'Stock Closing Prices ($)',
//             data: close,
//             backgroundColor: [
//               'rgba(255, 205, 86, 0.8)',
//               'rgba(54, 162, 235, 0.8)',
//               'rgba(255, 99, 132, 0.8)'
//             ],
//             borderColor: [
//               'rgba(255, 205, 86, 1)',
//               'rgba(54, 162, 235, 1)',
//               'rgba(255, 99, 132, 1)'
//             ],
//             borderWidth: 2
//           }]
//         },
//         options: {
//           responsive: true,
//           plugins: {
//             title: {
//               display: true,
//               text: 'Stock Closing Prices by Company'
//             },
//             legend: { display: false },
//             tooltip: {
//               callbacks: {
//                 afterLabel: function(context) {
//                   const companyIndex = context.dataIndex;
//                   return 'Date: ' + date[companyIndex];
//                 }
//               }
//             }
//           },
//           scales: {
//             y: {
//               beginAtZero: true,
//               title: { display: true, text: 'Price ($)' }
//             },
//             x: {
//               title: { display: true, text: 'Company' }
//             }
//           }
//         }
//       }
//     );
//   } catch (error) {
//     console.error('Error loading closing data:', error);
//   }
//   disableActiveButton('close_button');
// }

// async function loadVolumeChart() {
//   destroyCurrentChart();

//   try {
//     const data = await fetchStockData();
//     const companies = Object.values(data);
//     const labels = companies.map(company => company.company_name);
//     const volume = companies.map(company => company.volume);
//     const date = companies.map(company => company.date);

//     currentChart = new Chart(
//       document.getElementById('main_chart'),
//       {
//         type: 'bar',
//         data: {
//           labels: labels,
//           datasets: [{
//             label: 'Volume for Day (ea.)',
//             data: volume,
//             backgroundColor: [
//               'rgba(54, 162, 235, 0.8)',
//               'rgba(255, 99, 132, 0.8)',
//               'rgba(255, 205, 86, 0.8)'
//             ],
//             borderColor: [
//               'rgba(54, 162, 235, 1)',
//               'rgba(255, 99, 132, 1)',
//               'rgba(255, 205, 86, 1)'
//             ],
//             borderWidth: 2
//           }]
//         },
//         options: {
//           responsive: true,
//           plugins: {
//             title: {
//               display: true,
//               text: 'Stock Volume Movement by Company'
//             },
//             legend: { display: false },
//             tooltip: {
//               callbacks: {
//                 afterLabel: function(context) {
//                   const companyIndex = context.dataIndex;
//                   return 'Date: ' + date[companyIndex];
//                 }
//               }
//             }
//           },
//           scales: {
//             y: {
//               beginAtZero: true,
//               title: { display: true, text: 'Units (ea.)' }
//             },
//             x: {
//               title: { display: true, text: 'Company' }
//             }
//           }
//         }
//       }
//     );
//   } catch (error) {
//     console.error('Error loading volume data:', error);
//   }
//   disableActiveButton('volume_button');
// }









// Load the default chart on page load
document.addEventListener('DOMContentLoaded', function() {
  loadChart('high');


});
